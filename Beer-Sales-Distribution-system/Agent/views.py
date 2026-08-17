
from multiprocessing import context
from operator import attrgetter
from statistics import quantiles
from django import http
from django.forms import EmailField
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from .form import *
from .models import *
from Company.models import *
from Customer.models import Customer_order, Customer_Transaction
import requests
from passlib.hash import pbkdf2_sha256
import json
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.mail import send_mail,EmailMessage
from BGI import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import authenticate, login, logout
from . tokens import generate_token


# Create your views here.
# Dashbord par
@login_required(login_url=('login'))
def Agent_dashboard(request):
    try:
        if request.user.groups.all()[0].name == 'Agent':
            context = {}
            try:
                users = User.objects.get(id=request.user.id)

            except users.DoesNotExist:
                return HttpResponse('404,User: Data Not Found')

            try:

                request_agent = Agent.objects.filter(user=users)
                all_customer = Customer.objects.filter(Agent=request_agent[0])
                all_vechil = Vehicle.objects.filter(Agent=request_agent[0])
                all_driver = Driver.objects.filter(Agent=request_agent[0])
                total_vichel = all_vechil.count()
                total_driver = all_driver.count()
                print(total_driver)
                print(total_vichel)
                total_customer = all_customer.count()
                penndig_order_customer = []
                agent_custome = []
                cust_order = {}
                customer_order = []
                customer_transaction = []
                for agent_cust in all_customer:
                    cust_order[agent_cust] = Customer_order.objects.filter(
                        Customer=agent_cust)

                for customer, order in cust_order.items():

                    for ord in order:
                        customer_order.append(ord)
                        customer_transaction.append(
                            Customer_Transaction.objects.filter(Customer_order_id=ord.id))

                data = zip(customer_order, customer_transaction)

                total_pending_order = 0
                for order in penndig_order_customer:
                    total_pending_order = total_pending_order + 1
                # penndig_order_customer.append(Customer_order.objects.filter(Customer=customer,status='Pending'))

                adds = Advertisment.objects.all()
                context = {
                    'all_customer': all_customer,
                    'total_customer': total_customer,
                    'adds': adds,
                    'data': data,
                    'cust_order': cust_order,
                    'total_pending_order': total_pending_order,
                    'penndig_order_customer': penndig_order_customer,
                    'total_vichel': total_vichel,
                    'total_driver': total_driver,


                }
                return render(request, 'Agent/agent-dashboard.html', context)
            except UnboundLocalError as e:
                return HttpResponse('404,User: Data Not Found')
        messages.error(request, 'permission denied ')
        return redirect('logout')
    except IndexError as e:
        messages.error(request, 'Login Before ')
        return redirect('logout')

def my_draiver(request):

    return render(request, 'Agent/my_draiver.html', {})


def my_vichile(request):

    return render(request, 'Agent/my_vichile.html', {})


def my_product(request):

    return render(request, 'Agent/my_product.html', {})


# ///////////////////////////////////////////////////////////////  user profile part  ////////////////////////////////////////////////////////////////////////////

def show_profile(request):

    try:
        if request.user.groups.all()[0].name == 'Agent':
            users = User.objects.get(id=request.user.id)

            Agent = users.agent

            context = {
                'admin': Agent,
            }
            return render(request, 'Agent/profile/show_profile.html', context)
        messages.error(request, 'permission denied ')
        return redirect('logout')
    except IndexError as e:
        messages.error(request, 'Login Before ')
        return redirect('logout')


def edit_profile(request):
    try:
        if request.user.groups.all()[0].name == 'Agent':
            users = User.objects.get(id=request.user.id)
            admin = users.agent
            context = {
                'admin': admin,

            }
            if request.method == 'POST':
                admin.about = request.POST['about']
                admin.phone1 = request.POST['phone']
                admin.address = request.POST['address']
                admin.facebook = request.POST['facebook']
                admin.telegram = request.POST['telegram']
                admin.instagram = request.POST['instagram']
                users.first_name = request.POST['first_name']
                users.last_name = request.POST['last_name']

                Email = request.POST['email']
                # email uniqueness
                # email_user=User.objects.get(email=Email)
                users.email = request.POST['email']
                new = User.objects.filter(email=Email)
                x = new.count()
                if x > 1:
                    messages.error(request, 'Email Already Exist')
                    return render(request, 'Agent/profile/edit_profile.html', context)

                admin.save()
                users.save()
                return redirect('show_profile_agent')
            return render(request, 'Agent/profile/edit_profile.html', context)
        messages.error(request, 'permission denied ')
        return redirect('logout')
    except IndexError as e:
        messages.error(request, 'Login Before ')
        return redirect('logout')

@login_required(login_url=('login'))
def change_password(request):
    try:
        if request.user.groups.all()[0].name == 'Agent':
            users = User.objects.get(id=request.user.id)
            admin = users.agent

            if request.method == 'POST':
                form = passwordform(request.user, request.POST)
                if form.is_valid():
                    user = form.save()
                    update_session_auth_hash(request, user)  # Important!
                    messages.success(
                        request, 'Your password was successfully updated!')
                    return redirect('show_profile_agent')
                else:
                    messages.error(request, 'Please correct the error below.')
            else:
                form = passwordform(request.user)
            context = {
                'admin': admin,
                'usermodel': users,
                'form': form
            }
            return render(request, 'Agent/profile/chage_password.html', context)
        messages.error(request, 'permission denied ')
        return redirect('logout')
    except IndexError as e:
        messages.error(request, 'Login Before ')
        return redirect('logout')

@login_required(login_url=('login'))
def change_profile_pic(request):
    try:
        if request.user.groups.all()[0].name == 'Agent':
            users = User.objects.get(id=request.user.id)
            admin = users.agent
            context = {
                'admin': admin,
                'usermodel': users
            }
            if request.method == 'POST':
                if len(request.FILES['img']) != 0:
                    admin.profile_pic.delete()
                    admin.profile_pic = request.FILES['img']
                    admin.save()
                    return redirect('edit_profile_agent')
                else:
                    return render(request, 'Agent/profile/change_profile_pic.html', context)

            return render(request, 'Agent/profile/change_profile_pic.html', context)

        messages.error(request, 'permission denied ')
        return redirect('logout')
    except IndexError as e:
        messages.error(request, 'Login Before ')
        return redirect('logout')

@login_required(login_url=('login'))
def delete_profile_pic(request):
    try:
        if request.user.groups.all()[0].name == 'Agent':
            users = User.objects.get(id=request.user.id)
            admin = users.agent
            context = {
                'admin': admin,
                'usermodel': users
            }
            if len(admin.profile_pic) != 0:
                admin.profile_pic.delete()
                return redirect('edit_profile_agent')

            return render(request, 'Agent/profile/edit_profile.html', context)
        messages.error(request, 'permission denied ')
        return redirect('logout')
    except IndexError as e:
        messages.error(request, 'Login Before ')
        return redirect('logout')

# /////////////////////////////////////////////////////////////// end user profile part ////////////////////////////////////////////////////////////////////////////

# ///////////////////////////////////////////////////////////////// Customer Order ///////////////////////////////////////////////////////////////////////////////////

    
#data = zip(customer_order, customer_transaction)
@login_required(login_url=('login'))
def customer_order(request):
    try:
        if request.user.groups.all()[0].name == 'Agent':
            cust_order = {}
            customer_order = []
            customer_transaction = []
            request_agent = Agent.objects.filter(user=request.user)
            all_customer = Customer.objects.filter(Agent=request_agent[0])

            for agent_cust in all_customer:
                cust_order[agent_cust] = Customer_order.objects.filter(Customer=agent_cust)

            for customer, order in cust_order.items():
                for ord in order:
                    customer_order.append(ord)
                    transaction = Customer_Transaction.objects.filter(Customer_order_id=ord.id).first()
                    if transaction:
                        customer_transaction.append(transaction)

            data = zip(customer_order, customer_transaction)
            context = {
                'cust_order': cust_order,
                'data': data,
                'customer_order': customer_order
            }

            return render(request, 'Agent/view-cust-orders.html', context)
        messages.error(request, 'Permission denied')
        return redirect('logout')
    except IndexError as e:
        messages.error(request, 'Login before')
        return redirect('logout')


# //////////////////////////////////////////////////////////////////////////////////// End Customer Order ////////////////////////////////////////////////////////////////////


# //////////////////////////////////////////////////////////////////////////////////// cusomer_order_ditel////////////////////////////////////////////////////////////////////
@login_required(login_url=('login'))
def customer_order_detail(request, pk):
    try:
        if request.user.groups.all()[0].name == 'Agent':
            request_agent = Agent.objects.get(user=request.user)
            drivers= Driver.objects.filter(Agent=request_agent)

            transaction = get_object_or_404(Customer_Transaction, id=pk)
            order = Customer_order.objects.get(id=transaction.Customer_order_id.id)
            products = Product.objects.all()

            if request.method == 'POST':
                driver_id = request.POST['driver']
                driver = get_object_or_404(Driver, id=driver_id)
                # Assign the driver to the order
                order.driver = driver
                order.save()
                return redirect('customer_order')
                messages.success(request, 'Driver assigned successfully.')
                

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
                sub_total.append(product.Price_in_creates * getattr(order, product.Product_Name))

                total_quantity += getattr(order, product.Product_Name)

            data = zip(prods, price, quantity, sub_total)

            context = {
                'transaction': transaction,
                'data': data,
                'total_quantity': total_quantity,
                'drivers': drivers,
            }

            return render(request, 'Agent/customer_order_ditel.html', context)

        messages.error(request, 'Permission denied')
        return redirect('logout')

    except Agent.DoesNotExist:
        messages.error(request, 'Agent not found')
        return redirect('logout')

    except Customer_Transaction.DoesNotExist:
        messages.error(request, 'Transaction not found')
        return redirect('logout')

    except Customer_order.DoesNotExist:
        messages.error(request, 'Order not found')
        return redirect('logout')

    except IndexError:
        messages.error(request, 'Login required')
        return redirect('logout')


# ////////////////////////////////////////////////////////////////////////////// End cusomer_order_ditel /////////////////////////////////////////////////////////////////////////


# ////////////////////////////////////////////////////////////////////////////// make_order /////////////////////////////////////////////////////////////////////////
@login_required(login_url=('login'))
def make_order(request):
    try:
        if request.user.groups.all()[0].name == 'Agent':
            all_product = Product.objects.all()
            all_store = Company_Store.objects.all()
            context = {
                'all_product': all_product,
                'all_store': all_store,

            }
            return render(request, 'Agent/agent_order.html', context)
        messages.error(request, 'permission denied ')
        return redirect('logout')
    except IndexError as e:
        messages.error(request, 'Login Before ')
        return redirect('logout')

# ////////////////////////////////////////////////////////////////////////////// End make_order /////////////////////////////////////////////////////////////////////////


# ////////////////////////////////////////////////////////////////////////////// order_summer /////////////////////////////////////////////////////////////////////////
@login_required(login_url=('login'))
def order_summer(request):
    try:
        if request.user.groups.all()[0].name == 'Agent':
            all_product = Product.objects.all()
            all_store = Company_Store.objects.all()
            ary1 = []
            ary2 = []
            q = 0
            a = 0
            tl = 0
            arr = {}
            arr3 = []
            if request.method == 'POST':
                store = request.POST['store']
                storee = Company_Store.objects.get(Store_Name=store)
                ag = Agent_order.objects.create(status='Pending', Store=storee)
                for product in all_product:
                    a = request.POST[product.Product_Name]
                    arr[product.Product_Name] = a
                    tp = product.Price_in_creates * \
                        int(request.POST[product.Product_Name])
                    ary1.append(a)
                    ary2.append(tp)
                    tl = tl+tp
                    q += int(a)
                    vat = 0.15 * tl
                for key, value in arr.items():
                    setattr(ag, key, value)
                ag.save()

                obj = {
                    "process": "Cart",
                    "successUrl": "http://localhost:8000/Agent/success/",
                    "ipnUrl": "http://localhost:8000/Agent/ipn",
                    "cancelUrl": "http://localhost:8000/Agent/cancel",
                    "merchantId": "SB1560",
                    "merchantOrderId": ag.id,
                    "expiresAfter": 24,
                    "totalItemsDeliveryFee": 0,
                    "totalItemsDiscount": 0,
                    "totalItemsHandlingFee": 0,
                    "totalItemsTax1": vat,
                    "totalItemsTax2": 0
                }
                cart = {"cartitems": [
                    {"itemId": "sku-01", "itemName": "Beer", "unitPrice": tl, "quantity": 1}, ]}
                mylist = zip(all_product, ary1, ary2)
                context = {
                    'all_product': all_product,
                    'all_store': all_store,
                    'a': a,
                    'ary': ary1,
                    'mylist': mylist,
                    'tl': tl,
                    'obj': obj,
                    'cart': cart,
                    'q': q


                }
                return render(request, 'Agent/order_summer.html', context)
            return redirect('agent_make_order')
        messages.error(request, 'permission denied ')
        return redirect('logout')
    except IndexError as e:
        messages.error(request, 'Login Before ')
        return redirect('logout')
# ///////////////////////////////////////////////////////////////////////////////////////// end order_summer /////////////////////////////////////////////////////////

@login_required(login_url=('login'))
def success(request):
    try:
        if request.user.groups.all()[0].name == 'Agent':
            ii = request.GET.get('itemId')
            total = request.GET.get('TotalAmount')
            moi = request.GET.get('MerchantOrderId')
            ti = request.GET.get('TransactionId')
            status = request.GET.get('Status')
            TransactionCode = request.GET.get('TransactionCode')
            MerchantCode = request.GET.get('MerchantCode')
            BuyerId = request.GET.get('BuyerId')
            Currency = request.GET.get('Currency')

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
            Agent_Orders = Agent_order.objects.get(id=moi)
            context = {
                'total': total,
                'status': status,
                'TransactionCode': TransactionCode,
                'MerchantCode': MerchantCode,
                'BuyerId': BuyerId,
                'Currency': Currency,
                'moi': moi,
                'Agent_Orders': Agent_Orders,

            }

            TC = Agent_Transaction.objects.filter(
                TransactionCode=TransactionCode)

            if TC.exists():
                redirect('transactions')
            else:
                Agent_Transaction.objects.create(Agent_order_id=Agent_Orders, Total_Amount=total,
                                                 Paid_status=status, TransactionCode=TransactionCode, MarchentId=MerchantCode)
            return render(request, 'Agent/new_post-payment.html', context)
        messages.error(request, 'permission denied ')
        return redirect('logout')
    except IndexError as e:
        messages.error(request, 'Login Before ')
        return redirect('logout')

@login_required(login_url=('login'))
def cancel(request):
    return render(request, 'Agent/cancel.html')

@login_required(login_url=('login'))
def ipn(request):
    return render(request, 'Agent/ipn.html')

@login_required(login_url=('login'))
def manage_customers(request):
    try:
        if request.user.groups.all()[0].name == 'Agent':
            users = User.objects.get(id=request.user.id)
            print(users)
            request_agent = Agent.objects.get(user=users)
            all_customer = Customer.objects.filter(Agent=request_agent)
            total_customer = all_customer.count()

            context = {
                'all_customer': all_customer,
                'total_customer': total_customer,
            }
            return render(request, 'Agent/manage-customers.html', context)
        messages.error(request, 'permission denied ')
        return redirect('logout')
    except IndexError as e:
        messages.error(request, 'Login Before ')
        return redirect('logout')

@login_required(login_url=('login'))
def add_customers(request):
    try:
        if request.user.groups.filter(name='Agent').exists():
            if request.method == 'POST':
                errorr = request.POST.get('error')

                # required fields
                address = request.POST.get('address')
                driver = request.POST.get('driver')
                TIN_NO = request.POST.get('TIN_NO')
                marchent_id = request.POST.get('marchent_id')
                company_name = request.POST.get('company_name')
                license = request.FILES.get('license')
                first_name = request.POST.get('first_name')
                last_name = request.POST.get('last_name')
                house_no = request.POST.get('house_no')
                email = request.POST.get('email')
                username = request.POST.get('username')
                password1 = request.POST.get('password1')
                password2 = request.POST.get('password2')
                phone1 = request.POST.get('phone1')
                phone2 = request.POST.get('phone2')

                profile = request.FILES.get('profile')
                print(errorr)
                if errorr == '':
                    if password1 == password2:
                        if User.objects.filter(username=username).exists():
                            messages.error(request, "Username already exists")
                        elif User.objects.filter(email=email).exists():
                            messages.error(request, "Email already exists")
                        else:
                            user = User.objects.create_user(
                                username=username, email=email, password=password1, first_name=first_name, last_name=last_name)
                            my_group = Group.objects.get(name='Customer')
                            my_group.user_set.add(user)

                            if user:
                                customer = Customer.objects.create(
                                    user=user, Agent=request.user.agent, Compan_name=company_name,
                                    phone1=phone1, phone2=phone2, Address=address, House_No=house_no,
                                    profile_pic=profile, TIN_NO=TIN_NO, License=license,
                                    Marchent_id=marchent_id
                                )

                                customer.user.is_active=False
                                customer.user.save()

                                if customer:
                                    subject = "Welcome to GFG- Django Login!!"
                                    message = "Hello " + user.first_name + "!! \n" + "Welcome to BGI!! \nThank you for visiting our website\n. We have also sent you a confirmation email, please confirm your email address. \n\nThanking You\nAnubhav Madhav"        
                                    from_email = settings.EMAIL_HOST_USER
                                    to_list = [user.email]
                                    send_mail(subject, message, from_email, to_list, fail_silently=True) 

                                    # Email Address Confirmation Email
                                    current_site = get_current_site(request)
                                    email_subject = "Confirm your Email - Django Login!!"
                                    message2 = render_to_string('email_confirmation.html',{ 
                                                'name': user.first_name,
                                                 'domain': current_site.domain,
                                                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                                'token': generate_token.make_token(user)
                                    })    

                                    email = EmailMessage(email_subject,
                                                              message2,
                                                              settings.EMAIL_HOST_USER,
                                                              [user.email],
                                                             )   
                                    email.fail_silently = True
                                    email.send()  
                                    return redirect('manage_customers')
                                    #messages.success(request, 'Customer registered successfully!')
                    else:
                        messages.error(request, 'Passwords do not match.')
                else:
                    messages.error(request, 'Please fill the form correctly.')

                context = {
                    'address': address,
                    'house_no': house_no,
                    'TIN_NO': TIN_NO,
                    'marchent_id': marchent_id,
                    'driver': driver,
                    'license': license,
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'username': username,
                    'password1': password1,
                    'phone1': phone1,
                    'phone2': phone2,
                }
                return render(request, 'Agent/add-customer.html', context)

            return render(request, 'Agent/add-customer.html')
        
        messages.error(request, 'Permission denied')
        return redirect('logout')

    except IndexError:
        messages.error(request, 'Please log in first.')
        return redirect('logout')
def activate(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        user = None

    if user is not None and generate_token.check_token(user,token):
        user.is_active = True
        # user.profile.signup_confirmation = True
        user.save()
        login(request,user)
        #messages.success(request, "Your Account has been activated!!")
        return redirect('login')
    else:
        return render(request,'activation_failed.html')        

@login_required(login_url=('login'))
def customers_ditel(request, pk):
    try:
        if request.user.groups.all()[0].name == 'Agent':
            customer = Customer.objects.get(id=pk)
            context = {
                'customer': customer,
            }
            return render(request, 'Agent/customer-ditel.html', context)
        messages.error(request, 'permission denied ')
        return redirect('logout')
    except IndexError as e:
        messages.error(request, 'Login Before ')
        return redirect('logout')
@login_required(login_url=('login'))
def remove_customer_page(request,pk):
    try:
        if request.user.groups.all()[0].name == 'Agent':
            customer = Customer.objects.get(pk=pk)

            context = {
                'customer': customer,
            }
            return render(request, 'Agent/remove_customer.html', context)
        messages.error(request, 'permission denied ')
        return redirect('logout')
    except IndexError as e:
        messages.error(request, 'Login Before ')
        return redirect('logout')
@login_required(login_url=('login'))
def reactive_account(request, pk):
    try:
        if request.user.groups.all()[0].name == 'Agent':
            user = User.objects.get(id=pk)
            if user.is_active == True:
                messages.info(request, user.first_name + ' ' +
                              user.last_name + ' is already now activated')
            else:
                user.is_active = True
                user.save()
                messages.success(request, user.first_name + ' ' +
                                 user.last_name + ' is now activated')
            deleted_accounts = []
            all_user = User.objects.all()
            for user in all_user:
                if not user.is_active:
                    deleted_accounts.append(user)

            context = {
                'deleted_accounts': deleted_accounts,
            }
            return render(request, 'Agent/deleted_account.html', context)
        messages.error(request, 'permission denied ')
        return redirect('logout')

    except IndexError as e:
        messages.error(request, 'Login Before ')
        return redirect('logout')   
@login_required(login_url=('login'))
def remove_customer(request, pk):
    try:
        if request.user.groups.all()[0].name == 'Agent':
            customer = Customer.objects.get(pk=pk)
            customer.user.is_active = False
            customer.user.save()
            deleted_accounts = []
            all_user = User.objects.all()
            for user in all_user:
                if not user.is_active:
                    deleted_accounts.append(user)

            messages.info(request, customer.Compan_name + ' ' +
                           ' is now Removed')
            context = {
                'deleted_accounts': deleted_accounts,
                'customer':customer
            }
            return render(request, 'Agent/Deleted_account.html', context)
        messages.error(request, 'permission denied ')
        return redirect('logout')
    except IndexError as e:
        messages.error(request, 'Login Before ')
        return redirect('logout')

@login_required(login_url=('login'))
def deleted_account(request):
    try:
        if request.user.groups.all()[0].name == 'Agent':
            deleted_accounts = []
            all_user = User.objects.all()
            for user in all_user:
                if not user.is_active:
                    deleted_accounts.append(user)
            context = {
                'deleted_accounts': deleted_accounts,
            }
            return render(request, 'Agent/Deleted_account.html', context)
        messages.error(request, 'permission denied ')
        return redirect('logout')
    except IndexError as e:
        messages.error(request, 'Login Before ')
        return redirect('logout')
@login_required(login_url=('login'))
def product_in_store(request):
    return render(request, 'Agent/product-in-agent-store.html', {})

@login_required(login_url=('login'))
def transaction_detail(request, pk):
    try:
        if request.user.groups.all()[0].name == 'Agent':
            transaction = Agent_Transaction.objects.get(id=pk)
            products = Product.objects.all()
            order = Agent_order.objects.get(id=transaction.Agent_order_id.id)
            price = []
            prods = []
            quantity = []
            sub_total = []
            grand_total = 0
            VAT_Paid = 0.0
            total_quantity = 0
            for product in products:
                price.append(product.Price_in_creates)
                prods.append(product.Product_Name)
                quantity.append(getattr(order, product.Product_Name))
                sub_total.append(product.Price_in_creates *
                                 getattr(order, product.Product_Name))
                grand_total += float(product.Price_in_creates *
                                     getattr(order, product.Product_Name))
                total_quantity += (getattr(order, product.Product_Name))
                VAT_Paid = float(grand_total * 0.15)

            data = zip(prods, price, quantity, sub_total)

            context = {
                'transaction': transaction,
                'data': data,
                'total_quantity': total_quantity,
                'grand_total': grand_total,
                'VAT': VAT_Paid,

            }
            return render(request, 'Agent/transaction-details.html', context)
        messages.error(request, 'permission denied ')
        return redirect('logout')
    except IndexError as e:
        messages.error(request, 'Login Before ')
        return redirect('logout')


# ////////////////////////////////////////////////////// Vichel Managemetn //////////////////////////
@login_required(login_url=('login'))
def add_vehicle(request):
    request_agent=Agent.objects.get(user=request.user)
    if request.method == 'POST':
        
        vichel_type = request.POST.get('car_type')
        vichel_name = request.POST.get('vehicle_name')
        vichel_No = request.POST.get('plate_num')
        vichel_pic = request.FILES.get('vehiclePhoto')
        print(vichel_pic)
        new = Vehicle.objects.create(
            vichel_type=vichel_type, vichel_name=vichel_name, vichel_No=vichel_No, vichel_pic=vichel_pic,Agent=request_agent)
        if new:
            messages.success(request, 'vihecle successfully added')
            return redirect('manage_vehicles')
        else:
            messages.error(request, 'something went wrong. please, try again')
    return render(request, 'Agent/add-vehicle.html',)

@login_required(login_url=('login'))
def delete_vehicle(request, pk):

    vihecle = Vehicle.objects.get(id=pk)
    agent = Agent.objects.get(user=request.user)
    if agent == vihecle.Agent:
        vihecle.delete()
        messages.success(request, 'Vihelce successfully deleted')
        return redirect('manage_vehicles')

@login_required(login_url=('login'))
def manage_vehicles(request):

    agent = Agent.objects.get(user=request.user)
    all_vechil = Vehicle.objects.filter(Agent=agent)
    context = {
        'all_vechil': all_vechil,
    }
    return render(request, 'Agent/manage-vehicles.html', context)

# ///////////////////////////////////////////////////// End Vichel /////////////////////////////////////


# ////////////////////////////////////////////////////// Driver Managemetn //////////////////////////
@login_required(login_url=('login'))
def add_driver(request):

    agent = Agent.objects.get(user=request.user)
    all_vechil = Vehicle.objects.filter(Agent=agent)
    context = {
        'all_vechil': all_vechil,
    }
    if request.method == 'POST':
        Full_name = request.POST.get('fullname')
        phone1 = request.POST.get('driverphone')
        vehicle = request.POST.get('vechile')
        assign_ = Vehicle.objects.get(vichel_No=vehicle)
        profile_pic = request.FILES.get('licence')
        Drive_license = request.FILES.get('driverPhoto')
        try:

            driver = Driver.objects.create(Agent=agent, Full_name=Full_name, phone1=phone1,
                                           vehicle=assign_, profile_pic=profile_pic, Drive_license=Drive_license)
            if driver:
                messages.success(request, 'Driver successfully added')
                return redirect('manage_drivers')
            else:
                messages.error(
                    request, 'something went wrong. please, try again')

            return render(request, 'Agent/add-driver.html', context)
        except Exception as e:
            messages.error(request, 'Vihecle already assigned')
            return redirect('add_driver')

    return render(request, 'Agent/add-driver.html', context)


def Assign_driver(request, pk):
    try:
        if request.user.is_authenticated and request.user.groups.filter(name='Agent').exists():
            request_agent = Agent.objects.get(user=request.user)
            drivers= Driver.objects.filter(Agent=request_agent)

            transaction = get_object_or_404(Customer_Transaction, id=pk)
            order = Customer_order.objects.get(id=transaction.Customer_order_id.id)
            products = Product.objects.all()

            if request.method == 'POST':
                driver_id = request.POST.get('driver')
                driver = get_object_or_404(Driver, id=driver_id)
                # Assign the driver to the order
                order.driver = driver
                order.save()
                messages.success(request, 'Driver assigned successfully.')

            price = []
            prods = []
            quantity = []
            sub_total = []
            grand_total = 0
            total_quantity = 0

            for product in products:
                price.append(product.Price_in_creates)
                prods.append(product.Product_Name)
                quantity.append(getattr(order, product.Product_Name.lower()))
                sub_total.append(product.Price_in_creates * getattr(order, product.Product_Name.lower()))

                total_quantity += getattr(order, product.Product_Name.lower())

            data = zip(prods, price, quantity, sub_total)

            context = {
                'transaction': transaction,
                'data': data,
                'total_quantity': total_quantity,
                'drivers': drivers,
            }

            return render(request, 'Agent/customer_order_detail.html', context)

        messages.error(request, 'Permission denied')
        return redirect('logout')

    except Agent.DoesNotExist:
        messages.error(request, 'Agent not found')
        return redirect('logout')

    except Customer_Transaction.DoesNotExist:
        messages.error(request, 'Transaction not found')
        return redirect('logout')

    except Customer_order.DoesNotExist:
        messages.error(request, 'Order not found')
        return redirect('logout')

    except IndexError:
        messages.error(request, 'Login required')
        return redirect('logout')



@login_required(login_url=('login'))
def manage_drivers(request):
    agent = Agent.objects.get(user=request.user)
    all_drive = Driver.objects.filter(Agent=agent)
    context = {
        'all_drive': all_drive,
    }
    return render(request, 'Agent/manage-drivers.html', context)

@login_required(login_url=('login'))
def view_drivers_profile(request, pk):
    agent = Agent.objects.get(user=request.user)
    drive = Driver.objects.get(Agent=agent, id=pk)
    all_vechil = Vehicle.objects.filter(Agent=agent)
    if request.method == 'POST':
        salary = request.POST.get('Salary')
        vichile = request.POST.get('vihecle')
        vehicle = Vehicle.objects.get(vichel_No=vichile)
        drive.salary = salary
        drive.vehicle = vehicle
        drive.save()
    context = {
        'drive': drive,
        'all_vechil': all_vechil,
    }
    return render(request, 'Agent/driver_profile.html', context)

@login_required(login_url=('login'))
def delete_drivers(request, pk):
    agent = Agent.objects.get(user=request.user)
    drive = Driver.objects.get(Agent=agent, id=pk)
    all_drive = Driver.objects.filter(Agent=agent)
    drive.delete()
    messages.success(request, 'Driver successfully removed')

    context = {
        'all_drive': all_drive,
    }
    return render(request, 'Agent/manage-drivers.html', context)
# ////////////////////////////////////////////////////// End Driver Managemetn //////////////////////////

@login_required(login_url=('login'))
def transactions(request):
    try:
        if request.user.groups.all()[0].name == 'Agent':
            all_transaction = Agent_Transaction.objects.all().order_by('-date_created')
            context = {
                'all_transaction': all_transaction,
            }
            return render(request, 'Agent/transactions.html', context)
        messages.error(request, 'permission denied ')
        return redirect('logout')
    except IndexError as e:
        messages.error(request, 'Login Before ')
        return redirect('logout')

@login_required(login_url=('login'))
def send_message(request):

    return render(request, 'Agent/send-message.html', {})

@login_required(login_url=('login'))
def cust_change_password(request, pk):
    try:
        if request.user.groups.all()[0].name == 'Agent':
            if request.method == 'POST':
                old_password = request.POST.get('password')
                customer = Customer.objects.get(id=pk)
                if customer.user.check_password(old_password):
                    new_password = request.POST.get('newpassword')
                    renew_password = request.POST.get('renewpassword')
                    if new_password == renew_password:
                        customer.user.set_password(new_password)
                        customer.user.save()
                        return HttpResponse('password changed ,successfully')
                    return HttpResponse('old password and new password are not the same')
                return HttpResponse('old password doestn\'t exixt in the system')
            return render(request, 'Agent/manage-customers.html')
        messages.error(request, 'permission denied ')
        return redirect('logout')
    except IndexError as e:
        messages.error(request, 'Login Before ')
        return redirect('logout')
