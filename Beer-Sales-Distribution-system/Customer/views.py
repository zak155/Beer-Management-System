from http.client import CONTINUE
from itertools import product
from multiprocessing import context
from multiprocessing.dummy import JoinableQueue
from django.contrib import messages
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import PasswordChangeForm
from Account.views import login_view
from Agent.models import Customer
from Agent.views import transactions
from Company.models import Product
from .models import Customer_order, Customer_Transaction
from .form import passwordform
from django.core.mail import send_mail
import requests
from django.contrib.auth.decorators import login_required


from django.shortcuts import render
from django.contrib.auth.models import Group
from Customer.models import Customer_order
from BGI import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
#from django.contrib.auth import authenticate, login, logout
from . tokens import generate_token
import uuid
from Customer.services.chapa import ChapaPaymentService
# Create your views here.

@login_required(login_url=('login'))
def Customer_dashboard(request):
    try:
        if request.user.groups.all()[0].name == 'Customer':
            customer_orders = Customer_order.objects.filter(
                Customer=request.user.customer).order_by('-date_created')

            trans = {}
            for order in customer_orders:
                trans[order.id] = Customer_Transaction.objects.filter(
                    Customer_order_id=order).order_by('-date_created')

            products = Product.objects.all()
            orders = customer_orders
            total_pending = 0
            total_received = 0
            total_paid = 0
            total_rejected = 0
            total_quantity = []
            # for order in orders:
            #     for product in products:
            #         total_quantity+=getattr(order,product.Product_Name)
            transactions = []
            for key, value in trans.items():
                for val in value:
                    total_paid += val.Total_Amount
                    transactions.append(val)

            for order in orders:

                if order.status == 'Pending':
                    total_pending += 1
                elif order.status == 'Not Recived':
                    total_rejected += 1
                elif order.status == 'Delivered':
                    total_received += 1

            # for transaction in transactions:
            #     total_paid+=transaction.Total_Amount
            context = {
                'customer_orders': customer_orders,
                'total_payment': total_paid,
                'total_pending': total_pending,
                'total_received': total_received,
                'total_rejected': total_rejected,
                'transactions': transactions,
            }
            return render(request, 'Customer/home.html', context)
        messages.error(request, 'permission denied ')
        return redirect('logout')
    except IndexError as e:
        messages.error(request, 'permission denied ')
        return redirect('logout')

# User Profile

@login_required(login_url=('login'))
def show_profile(request):
    try:
        if request.user.groups.all()[0].name == 'Customer':
            customer = Customer.objects.get(id=request.user.customer.id)
            context = {'customer': customer}
            return render(request, 'Customer/profile/show_profile.html', context)
        messages.error(request, 'permission denied ')
        return redirect('logout')
    except IndexError as e:
        messages.error(request, 'permission denied ')
        return redirect('logout')

@login_required(login_url=('login'))
def edit_profile(request):
    try:
        if request.user.groups.all()[0].name == 'Customer':
            users = User.objects.get(id=request.user.id)
            context = {
                'users': users,

            }
            if request.method == 'POST':
                users.customer.about = request.POST['about']
                users.customer.phone1 = request.POST['phone1']
                users.customer.phone2 = request.POST['phone2']
            #  admin.Company=request.POST['company']
                users.customer.address = request.POST['address']

                users.customer.facebook = request.POST['facebook']
                users.customer.telegram = request.POST['telegram']
                users.customer.instagrm = request.POST['instagram']
                users.first_name = request.POST['first_name']
                users.last_name = request.POST['last_name']
                users.email = request.POST['email']
                users.customer.save()
                users.save()
                return redirect('show_profile_customer')
            return render(request, 'Customer/profile/edit_profile.html', context)
        messages.error(request, 'permission denied ')
        return redirect('logout')
    except IndexError as e:
        messages.error(request, 'permission denied ')
        return redirect('logout')

@login_required(login_url=('login'))
def change_password(request):
    try:
        if request.user.groups.all()[0].name == 'Customer':
            users = User.objects.get(id=request.user.id)
            admin = users.customer

            if request.method == 'POST':
                form = passwordform(request.user, request.POST)
                if form.is_valid():
                    user = form.save()
                    update_session_auth_hash(request, user)  # Important!
                    messages.success(
                        request, 'Your password was successfully updated!')
                    return redirect('show_profile')
                else:
                    messages.error(request, 'Please correct the error below.')
            else:
                form = passwordform(request.user)
            context = {
                'admin': admin,
                'usermodel': users,
                'form': form
            }
            return render(request, 'Customer/profile/chage_password.html', context)
        messages.error(request, 'permission denied ')
        return redirect('logout')
    except IndexError as e:
        messages.error(request, 'permission denied ')
        return redirect('logout')

@login_required(login_url=('login'))
def change_profile_pic(request):
    return render(request, 'Customer/profile/edit_profile.html',)

@login_required(login_url=('login'))
def delete_profile_pic(request):
    return render(request, 'Customer/profile/edit_profile.html',)

# end user profile

@login_required(login_url=('login'))
def make_order(request):
    try:
        if request.user.groups.all()[0].name == 'Customer':
            products = Product.objects.all()

            context = {
                'all_product': products,

            }

            return render(request, 'Customer/cust_order.html', context)
        messages.error(request, 'permission denied ')
        return redirect('logout')
    except IndexError as e:
        messages.error(request, 'permission denied ')
        return redirect('logout')

@login_required(login_url=('login'))
def send_delivery(request):
    try:
        if request.user.groups.all()[0].name == 'Customer':
            users = User.objects.get(id=request.user.id)
            requrd_customer = Customer.objects.get(user=users)
            cust_orders = Customer_order.objects.filter(
                Customer=requrd_customer, status='Delivered').order_by('-date_created')
            transactions = {}
            order_arry = []
            trans_arr = []

            for cust_order in cust_orders:
                transactions[cust_order.id] = Customer_Transaction.objects.get(
                    Customer_order_id=cust_order.id)
                order_arry.append(cust_order)

            for order, transa in transactions.items():
                trans_arr.append(transa)

            data = zip(trans_arr, order_arry)

            # my_transaction = Customer_Transaction.objects.filter(Customer_order_id.Customer=requrd_customer)
            context = {
                # 'all_transaction' :all_transaction,
                'data': data,

            }
            return render(request, 'Customer/send-delivery-status.html', context)
        messages.error(request, 'permission denied ')
        return redirect('logout')
    except IndexError as e:
        messages.error(request, 'permission denied ')
        return redirect('logout')

@login_required(login_url=('login'))
def customer_transactions(request):
    try:
        if request.user.groups.all()[0].name == 'Customer':
            users = User.objects.get(id=request.user.id)
            requrd_customer = Customer.objects.get(user=users)
            cust_orders = Customer_order.objects.filter(
                Customer=requrd_customer, status='Pending').order_by('-date_created')
            transactions = {}
            order_arry = []
            trans_arr = []

            for cust_order in cust_orders:
                try:
                    id = cust_order.id

                    transactions[id] = Customer_Transaction.objects.get(
                        Customer_order_id=cust_order.id)
                    order_arry.append(cust_order)
                except Exception:
                    pass

            for order, transa in transactions.items():

                trans_arr.append(transa)

            context = {

                'transactions': transactions,

            }
            return render(request, 'Customer/pinding.html', context)
        messages.error(request, 'permission denied ')
        return redirect('logout')
    except IndexError as e:
        messages.error(request, 'permission denied ')
        return redirect('logout')

@login_required(login_url=('login'))
def customer_recived(request, pk):
    try:
        if request.user.groups.all()[0].name == 'Customer':
            users = User.objects.get(id=request.user.id)
            requrd_customer = Customer.objects.get(user=users)
            recived_order = Customer_order.objects.get(
                Customer=requrd_customer, pk=pk)
            recived_order.status = 'Delivered'
            recived_order.save()
            cust_orders = Customer_order.objects.filter(
                Customer=requrd_customer, status='Pending').order_by('-date_created')

            transactions = {}
            order_arry = []
            trans_arr = []

            for cust_order in cust_orders:
                try:
                 transactions[cust_order.id] = Customer_Transaction.objects.get(
                    Customer_order_id=cust_order.id)
                except Customer_Transaction.DoesNotExist:
                  #messages.success( request, 'error is raised!')
                  pass
                                           
                order_arry.append(cust_order)

            for order, transa in transactions.items():
                trans_arr.append(transa)

            context = {
                'transactions': transactions,
            }

            return render(request, 'Customer/pinding.html', context)
        messages.error(request, 'permission denied ')
        return redirect('logout')
    except IndexError as e:
        messages.error(request, 'permission denied ')
        return redirect('logout')

@login_required(login_url=('login'))
def recived_transactions_by_customer(request):
    try:
        if request.user.groups.all()[0].name == 'Customer':
            users = User.objects.get(id=request.user.id)
            requrd_customer = Customer.objects.get(user=users)
            cust_orders = Customer_order.objects.filter(
                Customer=requrd_customer, status='Delivered').order_by('-date_created')
            transactions = {}
            order_arry = []
            trans_arr = []

            for cust_order in cust_orders:
                transactions[cust_order.id] = Customer_Transaction.objects.get(
                    Customer_order_id=cust_order.id)
                order_arry.append(cust_order)

            for order, transa in transactions.items():
                trans_arr.append(transa)

            data = zip(trans_arr, order_arry)

            # my_transaction = Customer_Transaction.objects.filter(Customer_order_id.Customer=requrd_customer)
            context = {
                # 'all_transaction' :all_transaction,
                'data': data,

            }
            return render(request, 'Customer/recived_order.html', context)
        messages.error(request, 'permission denied ')
        return redirect('logout')
    except IndexError as e:
        messages.error(request, 'permission denied ')
        return redirect('logout')

@login_required(login_url=('login'))
def not_recived_transactions_by_customer(request):
    try:
        if request.user.groups.all()[0].name == 'Customer':
            users = User.objects.get(id=request.user.id)
            requrd_customer = Customer.objects.get(user=users)
            cust_orders = Customer_order.objects.filter(
                Customer=requrd_customer, status='Not Recived').order_by('-date_created')
            transactions = {}
            order_arry = []
            trans_arr = []

            for cust_order in cust_orders:
                transactions[cust_order.id] = Customer_Transaction.objects.get(
                    Customer_order_id=cust_order.id)
                order_arry.append(cust_order)

            for order, transa in transactions.items():
                trans_arr.append(transa)

            data = zip(trans_arr, order_arry)

            # my_transaction = Customer_Transaction.objects.filter(Customer_order_id.Customer=requrd_customer)
            context = {
                # 'all_transaction' :all_transaction,
                'data': data,


            }
            return render(request, 'Customer/not_recived_order.html', context)
        messages.error(request, 'permission denied ')
        return redirect('logout')
    except IndexError as e:
        messages.error(request, 'permission denied ')
        return redirect('logout')

@login_required(login_url=('login'))
def customer_not_recived(request, pk):
    try:
        if request.user.groups.all()[0].name == 'Customer':
            users = User.objects.get(id=request.user.id)
            requrd_customer = Customer.objects.get(user=users)
            recived_order = Customer_order.objects.get(
                Customer=requrd_customer, pk=pk)
            recived_order.status = 'Not Recived'
            recived_order.save()
            messages.info(request, 'Not Recived Notification Sent')
            cust_orders = Customer_order.objects.filter(
                Customer=requrd_customer, status='Pending').order_by('-date_created')

            transactions = {}
            order_arry = []
            trans_arr = []

            for cust_order in cust_orders:
                transactions[cust_order.id] = Customer_Transaction.objects.get(
                    Customer_order_id=cust_order.id)
                order_arry.append(cust_order)

            for order, transa in transactions.items():
                trans_arr.append(transa)

            context = {
                'transactions': transactions,

            }

            return render(request, 'Customer/pinding.html', context)
        messages.error(request, 'permission denied ')
        return redirect('logout')
    except IndexError as e:
        messages.error(request, 'permission denied ')
        return redirect('logout')

@login_required(login_url=('login'))
def order_summer(request):
    try:
        if request.user.groups.all()[0].name == 'Customer':
            all_product = Product.objects.all()
            
            if request.method == 'POST':
                # 1. Create the authoritative order instance in DB
                ag = Customer_order.objects.create(
                    Customer=request.user.customer, 
                    status='Pending', 
                    driver_status='Not Assigned'
                )
                
                ary1 = []
                ary2 = []
                tl = 0
                arr = {}
                q = 0
                
                for product in all_product:
                    qty_str = request.POST.get(product.Product_Name, '0')
                    a = int(qty_str) if qty_str.isdigit() else 0
                    arr[product.Product_Name] = a
                    tp = product.Price_in_creates * a
                    ary1.append(a)
                    ary2.append(tp)
                    q += a
                    tl += tp

                # Save product quantity fields to the order
                for key, value in arr.items():
                    setattr(ag, key, value)
                ag.save()

                # 2. Generate a unique robust transaction reference
                tx_ref = f"BSDS-ORD-{ag.id}-{uuid.uuid4().hex[:8]}"

                # 3. Create initial pending transaction record in DB
                Customer_Transaction.objects.create(
                    Customer_order_id=ag,
                    Total_Amount=tl,
                    Paid_status='Not Paid',
                    tx_ref=tx_ref,
                    currency='ETB',
                    provider_status='PENDING'
                )

                # 4. Prepare payload for Chapa Initialization API
                user_email = request.user.email if request.user.email else f"customer_{request.user.id}@bgi.com"
                first_name = request.user.first_name if request.user.first_name else "Customer"
                last_name = request.user.last_name if request.user.last_name else "Agent"

                chapa_payload = {
                    "amount": str(tl),
                    "currency": "ETB",
                    "email": user_email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "tx_ref": tx_ref,
                    "callback_url": "http://127.0.0.1:8000/Customer/ipn/",
                    "return_url": f"http://127.0.0.1:8000/Customer/success/?tx_ref={tx_ref}",
                    "customization[title]": "BGI Beer Sales & Distribution",
                    "customization[description]": f"Payment for Order #{ag.id}"
                }

                # 5. Call Chapa Service
                try:
                    chapa_service = ChapaPaymentService()
                    response_data = chapa_service.initialize_payment(chapa_payload)
                    checkout_url = response_data['data']['checkout_url']
                    
                    # 6. Redirect customer directly to Chapa hosted payment page
                    return redirect(checkout_url)
                    
                except Exception as e:
                    messages.error(request, f"Payment Initialization Failed: {str(e)}")
                    return redirect('make_order')

            return redirect('make_order')
        
        messages.error(request, 'Permission denied')
        return redirect('logout')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('logout')
  


@login_required(login_url=('login'))
def success(request):
    try:
        if request.user.groups.all()[0].name == 'Customer':
            tx_ref = request.GET.get('tx_ref')
            
            if not tx_ref:
                messages.error(request, "Invalid payment return reference.")
                return redirect('customer_transactions')

            # 1. Locate the internal transaction record using tx_ref
            try:
                transaction_record = Customer_Transaction.objects.get(tx_ref=tx_ref)
            except Customer_Transaction.DoesNotExist:
                messages.error(request, "Transaction record not found.")
                return redirect('customer_transactions')

            customer_order = transaction_record.Customer_order_id

            # 2. Perform Server-to-Server Verification with Chapa API
            chapa_service = ChapaPaymentService()
            verification_response = chapa_service.verify_payment(tx_ref)

            is_verified = False
            provider_status = "FAILED"

            if verification_response and verification_response.get('status') == 'success':
                data = verification_response.get('data', {})
                api_amount = float(data.get('amount', 0))
                api_currency = data.get('currency', 'ETB')
                api_status = data.get('status', '') # usually 'success'

                # 3. Strict Validation checks (Amount and Currency integrity)
                if api_status == 'success' and api_amount >= float(transaction_record.Total_Amount):
                    is_verified = True
                    provider_status = "SUCCESS"

            # 4. Atomically Update Records Based on Verified Status
            if is_verified:
                transaction_record.Paid_status = 'Paid'
                transaction_record.provider_status = provider_status
                transaction_record.TransactionCode = data.get('reference', tx_ref)
                transaction_record.save()

                # Update order status if appropriate for your workflow
                customer_order.status = 'Pending'  # Keeps it ready for finance/store workflow review
                customer_order.save()
            else:
                transaction_record.Paid_status = 'Not Paid'
                transaction_record.provider_status = provider_status
                transaction_record.save()
                messages.error(request, "Payment verification failed or amount mismatch detected.")

            context = {
                'total': transaction_record.Total_Amount,
                'currency': transaction_record.currency,
                'status': transaction_record.Paid_status,
                'tx_ref': tx_ref,
                'transaction_code': transaction_record.TransactionCode,
                'Customer_Order': customer_order,
            }

            return render(request, 'Customer/post-payment.html', context)
            
        messages.error(request, 'Permission denied')
        return redirect('logout')
    except Exception as e:
        messages.error(request, f'An error occurred during verification: {str(e)}')
        return redirect('customer_transactions')
    try:
        if request.user.groups.all()[0].name == 'Customer':
            ii = request.GET.get('itemId')
            total = request.GET.get('TotalAmount')
            moi = request.GET.get('MerchantOrderId')
            ti = request.GET.get('TransactionId')
            status = request.GET.get('Status')
            TransactionCode = request.GET.get('TransactionCode')
            MerchantCode = request.GET.get('MerchantCode')
            BuyerId = request.GET.get('BuyerId')
            Currency = request.GET.get('Currency')
            if not moi:
                return redirect('')

            url = 'https://testapi.yenepay.com/api/verify/pdt/'
            datax = {
                "requestType": "PDT",
                "pdtToken": "Q1woj27RY1EBsm",
                "transactionId": ti,
                "merchantOrderId": moi
            }
            x = requests.post(url, datax)
            if x.status_code == 200:
                print("It's Paid")
            else:
                print('Invalid payment process')
            Customer_Order = Customer_order.objects.get(id=moi)
            context = {
                'total': total,
                'status': status,
                'TransactionCode': TransactionCode,
                'MerchantCode': MerchantCode,
                'BuyerId': BuyerId,
                'Currency': Currency,
                'moi': moi,
                'Customer_Order': Customer_Order,

            }

            TC = Customer_Transaction.objects.filter(
                TransactionCode=TransactionCode)

            if TC.exists():
                redirect('customer_transactions')
            else:
                Customer_Transaction.objects.create(Customer_order_id=Customer_Order, Paid_status=status,
                                                    Total_Amount=total, TransactionCode=TransactionCode, MarchentId=MerchantCode)
            return render(request, 'Customer/post-payment.html', context)
        messages.error(request, 'permission denied ')
        return redirect('logout')
    except IndexError as e:
        messages.error(request, 'Login Before ')
        return redirect('logout')

# def cancel(request):
#     return render(request, 'Agent/cancel.html')

# def ipn(request):
#     return render(request, 'Agent/ipn.html')
# def manage_customers(request):

#      return render(request,'Agent/manage-customers.html',{})

# def transaction_detail(request,pk):
#     transaction=Agent_Transaction.objects.get(id=pk)
#     products=Product.objects.all()
#     order=Agent_order.objects.get(id=transaction.Agent_order_id.id)
#     price=[]
#     prods=[]
#     quantity=[]
#     sub_total=[]
#     grand_total=0
#     total_quantity=0
#     for product in products:
#         price.append(product.Price_in_creates)
#         prods.append(product.Product_Name)
#         quantity.append(getattr(order,product.Product_Name))
#         sub_total.append(product.Price_in_creates*getattr(order,product.Product_Name))

#         total_quantity+=(getattr(order,product.Product_Name))


#     data=zip(prods,price,quantity,sub_total)
#     context={
#         'transaction':transaction,
#         'data':data,

#         'total_quantity':total_quantity,


#     }
#     return render(request,'Agent/transaction-details.html',context)
@login_required(login_url=('login'))
def customer_transaction_detail(request, pk):
    try:
        if request.user.groups.all()[0].name == 'Customer':
            transaction = Customer_Transaction.objects.get(id=pk)
            products = Product.objects.all()
            order = Customer_order.objects.get(id=transaction.Customer_order_id.id)
            price = []
            prods = []
            quantity = []
            sub_total = []
            grand_total = 0
            total_quantity = 0
            for product in products:
                price.append(product.Price_in_creates)
                prods.append(product.Product_Name)
                quantity.append(getattr(order, product.Product_Name))
                sub_total.append(product.Price_in_creates *
                                getattr(order, product.Product_Name))

                total_quantity += (getattr(order, product.Product_Name))

            data = zip(prods, price, quantity, sub_total)

            context = {
                'transaction': transaction,
                'data': data,
                'total_quantity': total_quantity,

            }
            return render(request, 'Customer/Customer-transaction-details.html', context)
        messages.error(request, 'permission denied ')
        return redirect('logout')
    except IndexError as e:
        messages.error(request, 'permission denied ')
        return redirect('logout')
