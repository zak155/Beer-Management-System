import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ChapaPaymentService:
    """
    Service layer to handle all communications with Chapa Payment Gateway API.
    """
    def __init__(self):
        self.base_url = getattr(settings, 'CHAPA_BASE_URL', 'https://api.chapa.co/v1')
        self.secret_key = getattr(settings, 'CHAPA_SECRET_KEY', None)
        
        if not self.secret_key:
            raise ValueError("CHAPA_SECRET_KEY is not configured in settings or environment variables.")

    def get_headers(self):
        return {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json',
        }

    def initialize_payment(self, payload):
        """
        Initializes a transaction with Chapa and returns the checkout URL and raw response.
        """
        url = f"{self.base_url}/transaction/initialize"
        try:
            response = requests.post(url, json=payload, headers=self.get_headers(), timeout=30)
            response_data = response.json()
            
            if response.status_code == 200 and response_data.get('status') == 'success':
                return response_data
            else:
                logger.error(f"Chapa Initialization Failed: {response.text}")
                raise Exception(response_data.get('message', 'Failed to initialize payment with Chapa.'))
                
        except requests.exceptions.RequestException as e:
            logger.exception("Network error while connecting to Chapa initialization API.")
            raise Exception("Payment gateway is currently unavailable. Please try again later.")

    def verify_payment(self, tx_ref):
        """
        Server-side verification of a transaction using its unique transaction reference.
        """
        url = f"{self.base_url}/transaction/verify/{tx_ref}"
        try:
            response = requests.get(url, headers=self.get_headers(), timeout=30)
            response_data = response.json()
            
            if response.status_code == 200:
                return response_data
            else:
                logger.error(f"Chapa Verification Failed for tx_ref {tx_ref}: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.exception(f"Network error while verifying transaction {tx_ref} with Chapa.")
            return None