from multiprocessing import context
from pickle import TRUE
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from Company.models import *
from Customer.models import *
from .form import CreateSuperUser
from django.contrib.auth.decorators import login_required
from django.core import validators
from django.contrib.auth.decorators import login_required
# Create your views here.


def login_view(request):
    if request.user.is_authenticated:
        if hasattr(request.user,'groups'):
           
                a = request.user.groups.all()[0].name
                if a == 'Admin':
                    return redirect('admin-dashbord',)
                elif a == 'Agent':

                    return redirect('agent_dashbord')
                elif a == 'Customer':

                    return redirect('Customer_dashbord')
                elif a == 'Financ_admin':

                    return redirect('finance_admin_home')
                elif a == 'Store_Manager':

                    return redirect('store-manager-home')
        else:
            messages.error(request,'You are not authenticated')
            return render(request, 'Account/login.html')

    else:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if hasattr(user,'groups'):
                    a = user.groups.all()[0].name
                    if a == 'Admin':
                        login(request, user)
                        return redirect('admin-dashbord',)
                    elif a == 'Agent':
                        login(request, user)
                        return redirect('agent_dashbord')
                    elif a == 'Customer':
                        login(request, user)
                        return redirect('Customer_dashbord')
                    elif a == 'Financ_admin':
                        login(request, user)
                        return redirect('finance_admin_home')
                    elif a == 'Store_Manager':
                        login(request, user)
                        return redirect('store-manager-home')
            else:
                messages.error(request,'Username or password is not correct!')
                return render(request, 'Account/login.html')
    return render(request, 'Account/login.html')


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        request.session.flush()
        return redirect('login')
    return redirect('login')


# make crate super order


def SuperUser_CreateView(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        Full_Name = first_name + " " + last_name
        if password1 == password2:
            new = User.objects.filter(username=username)
            if new.count():
                messages.error(request, "User Already Exist")
            else:
                new = User.objects.filter(email=email)
                if new.count():
                    a = new.count()
                    print(a)
                    messages.error(request, "Eamil Already Exist")
                else:
                    cheekis = User.objects.filter(is_superuser=True)
                    if cheekis.count():
                        messages.error(request, 'not allowed to create')
                    else:
                        user = User.objects.create_user(
                            username=username, email=email, password=password1, first_name=first_name, last_name=last_name)
                        user.is_superuser = True
                        user.is_staff = True
                        user.save()
                        my_group = Group.objects.get(name='Admin')
                        my_group.user_set.add(user)
                        admin = Admin.objects.create(
                            user=user, Full_Name=Full_Name)
                        if admin:
                            messages.success(
                                request, "Successfully Create Super User")
                            return redirect('login')
                        else:
                            messages.error(request, "supper user not created")

        else:
            messages.error(request, "password not match")

    return render(request, 'Account/Create_SuperUser_registration.html')
#def homepage(request):
    #return render(request,'Account/index.html')
