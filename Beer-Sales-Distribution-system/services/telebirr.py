# services/telebirr.py

import base64
import time
import uuid
import requests
import logging
from django.conf import settings
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key

logger = logging.getLogger(__name__)

class TelebirrPayService:
    """
    Enterprise Service Layer for Telebirr C2B Integration.
    Handles Fabric Token OAuth, RSA Request Signing, PreOrder Creation,
    Web Checkout URL Assembly, and Webhook Signature Verification.
    """

    def __init__(self):
        # Load configuration dictionary from Django settings
        self.config = settings.TELEBIRR_CONFIG
        self.private_key = self._load_private_key()
        self.public_key = self._load_public_key()

    def _load_private_key(self):
        """Loads the Merchant RSA Private Key PEM file for signing payloads."""
        key_path = self.config['PRIVATE_KEY_PATH']
        with open(key_path, 'rb') as key_file:
            return load_pem_private_key(key_file.read(), password=None)

    def _load_public_key(self):
        """Loads Telebirr's RSA Public Key PEM file for verifying webhooks."""
        key_path = self.config['TELEBIRR_PUBLIC_KEY_PATH']
        with open(key_path, 'rb') as key_file:
            return load_pem_public_key(key_file.read())

    @staticmethod
    def create_nonce_str():
        """Generates a random 32-character string for transaction freshness."""
        return uuid.uuid4().hex

    @staticmethod
    def create_timestamp():
        """Generates a UTC timestamp in seconds string (<= 13 chars)."""
        return str(int(time.time()))

    def sign_payload(self, data_dict):
        """
        Signs a payload dictionary using SHA256WithRSA according to Telebirr spec.
        1. Filters out null/empty values and sign/sign_type keys.
        2. Sorts keys alphabetically (ASCII).
        3. Formats as 'key=value&key2=value2'.
        4. Hashes with SHA-256 and encrypts with Merchant RSA Private Key.
        """
        # Step A: Filter empty values and sign keys
        filtered_items = [
            (k, str(v)) for k, v in data_dict.items()
            if v is not None and v != "" and k not in ['sign', 'sign_type']
        ]
        
        # Step B: Sort keys alphabetically by ASCII order
        sorted_items = sorted(filtered_items, key=lambda x: x[0])
        
        # Step C: Join as key=value format string
        string_to_sign = "&".join([f"{k}={v}" for k, v in sorted_items])
        
        # Step D: Sign using SHA256WithRSA & PKCS1v15 padding
        signature = self.private_key.sign(
            string_to_sign.encode('utf-8'),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        
        # Step E: Base64 encode signature output
        return base64.b64encode(signature).decode('utf-8')

    def verify_signature(self, data_dict, signature_b64):
        """
        Verifies incoming webhook callback signature using Telebirr's Public Key.
        Returns True if signature is authentic, False otherwise.
        """
        try:
            # Reconstruct string to verify
            filtered_items = [
                (k, str(v)) for k, v in data_dict.items()
                if v is not None and v != "" and k not in ['sign', 'sign_type']
            ]
            sorted_items = sorted(filtered_items, key=lambda x: x[0])
            string_to_verify = "&".join([f"{k}={v}" for k, v in sorted_items])

            signature_bytes = base64.b64decode(signature_b64)

            # Verify signature using Telebirr Public Key
            self.public_key.verify(
                signature_bytes,
                string_to_verify.encode('utf-8'),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            logger.error(f"Telebirr signature verification failed: {e}")
            return False

    def fetch_fabric_token(self):
        """
        Step 1: Requests Fabric Access Token from Telebirr Gateway.
        Headers: X-APP-Key
        Body: {"appSecret": "..."}
        """
        url = self.config['FETCH_TOKEN_URL']
        headers = {
            "Content-Type": "application/json",
            "X-APP-Key": self.config['APP_ID']
        }
        body = {
            "appSecret": self.config['APP_SECRET']
        }

        response = requests.post(url, json=body, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Return Bearer Token (e.g. "Bearer 94cc42be...")
        return data.get('token')

    def request_create_order(self, fabric_token, out_trade_no, amount, title):
        """
        Step 2: Calls /payment/v1/merchant/preOrder to generate a prepay_id.
        """
        url = self.config['APPLY_PAYMENT_URL']
        headers = {
            "Content-Type": "application/json",
            "X-APP-Key": self.config['APP_ID'],
            "Authorization": fabric_token
        }

        biz_content = {
            "appid": self.config['MERCHANT_ID'],
            "business_type": "BuyGoods",
            "merch_code": self.config['SHORT_CODE'],
            "merch_order_id": str(out_trade_no),
            "notify_url": self.config['NOTIFY_URL'],
            "redirect_url": self.config['RETURN_URL'],
            "timeout_express": "120m",
            "title": title,
            "total_amount": f"{float(amount):.2f}",
            "trade_type": "Checkout",
            "trans_currency": "ETB",
            "payee_identifier": self.config['SHORT_CODE'],
            "payee_identifier_type": "04",
            "payee_type": "5000"
        }

        payload = {
            "timestamp": self.create_timestamp(),
            "nonce_str": self.create_nonce_str(),
            "method": "payment.preorder",
            "version": "1.0",
            "biz_content": biz_content
        }

        # Sign request payload
        payload['sign'] = self.sign_payload(payload)
        payload['sign_type'] = "SHA256WithRSA"

        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()

    def generate_checkout_url(self, out_trade_no, amount, title="Order Payment"):
        """
        Step 3 & 4 Orchestrator: Fetches token, creates preorder, and builds
        the complete H5 checkout redirect URL.
        """
        # 1. Fetch Fabric Token
        token = self.fetch_fabric_token()
        
        # 2. Call PreOrder API
        preorder_res = self.request_create_order(token, out_trade_no, amount, title)
        
        if preorder_res.get('code') != '0' or preorder_res.get('result') != 'SUCCESS':
            raise ValueError(f"Telebirr PreOrder Error: {preorder_res.get('msg')}")

        prepay_id = preorder_res['biz_content']['prepay_id']

        # 3. Build RawRequest Map for Redirect String
        map_payload = {
            "appid": self.config['MERCHANT_ID'],
            "merch_code": self.config['SHORT_CODE'],
            "nonce_str": self.create_nonce_str(),
            "prepay_id": prepay_id,
            "timestamp": self.create_timestamp()
        }

        sign = self.sign_payload(map_payload)

        raw_request = (
            f"appid={map_payload['appid']}"
            f"&merch_code={map_payload['merch_code']}"
            f"&nonce_str={map_payload['nonce_str']}"
            f"&prepay_id={map_payload['prepay_id']}"
            f"&timestamp={map_payload['timestamp']}"
            f"&sign={sign}"
            f"&sign_type=SHA256WithRSA"
        )

        web_base_url = self.config.get('WEB_BASE_URL', 'https://developerportal.ethiotelebirr.et:38443/payment/web/paygate?')
        other_params = "&version=1.0&trade_type=Checkout"

        checkout_url = f"{web_base_url}{raw_request}{other_params}"
        return checkout_url