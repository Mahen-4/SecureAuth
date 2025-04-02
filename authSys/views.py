from django.shortcuts import render, redirect
from authSys.models import Member
from .forms import MemberForm, LoginForm
import django.contrib.auth.password_validation as validators
from django.core import exceptions
from django.contrib.auth.hashers import make_password
import environ
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.urls import reverse


env = environ.Env()
def register_member(request):

    if request.method == 'POST':

        form = MemberForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password'] 

            #try to see if password valid and catch the exception if not
            try:
                # validate the password 
                validators.validate_password(password=password)
         
            except exceptions.ValidationError as e:
                #return form with errors
                form.add_error('password', e)
                return render(request, 'register.html', {'form': form})
            
            # create user 
            Member.objects.create_user(email=email, password=password)
            return redirect('authSys:login') 
    else:
        form = MemberForm()


    return render(request, 'register.html', {'form': form})


def login_member(request):

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():  # check if form is valid
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
    
            member = authenticate(request, email=email, password=password) #check if member exist and credentials correct

            # if yes login
            if member is not None:
                login(request,member) 
                member.update_last_login() 
                return redirect("home_view")
            
            else:
                return render(request, "login.html", {"error": "Email or Password is incorrect !", form: form})
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})


def logout_member(request):
    logout(request)
    return redirect("authSys:login");

 # #send mail
# subject = 'Thank you for registering to our site'
# message = 'WELCOME !'
# email_from = env('EMAIL_HOST_USER')
# recipient_list = [form.cleaned_data['email']]   
# send_mail( subject, message, email_from, recipient_list )