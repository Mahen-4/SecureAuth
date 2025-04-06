from django.shortcuts import render, redirect
from authSys.models import Member
from .forms import MemberForm, LoginForm, digiCodeForm
import django.contrib.auth.password_validation as validators
from django.core import exceptions
from django.contrib.auth.hashers import make_password
import environ
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.urls import reverse
import random
import datetime


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

            # if yes send to code a2f verif
            if member is not None:
                request.session['member_email'] = member.email
                return redirect("authSys:code_a2f")
            
            else:
                return render(request, "login.html", {"error": "Email or Password is incorrect !", form: form})
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})


def logout_member(request):
    logout(request)
    return redirect("authSys:login");


def code_a2f_member(request):
    print(f"Entered code_a2f_member view, method: {request.method}")
    member_email = request.session.get('member_email')

    if member_email is None or request.user.is_authenticated:
        print("1")
        return redirect("authSys:login")

    # Expire check
    expire_time_str = request.session.get(f"digiCode_expire{member_email}")
    if expire_time_str:
        expire_time = datetime.datetime.strptime(expire_time_str, "%Y-%m-%d %H:%M:%S.%f")
        if datetime.datetime.now() > expire_time:
            request.session.pop(f"digiCode{member_email}", None)
            request.session.pop(f"digiCode_expire{member_email}", None)
            print("2")
            return redirect("authSys:login")

    form = digiCodeForm(request.POST or None)
    #check if credential valid and there is a user but not connected and code dosn't exist already
    if request.session.get(f"digiCode{member_email}") is None:

        #add to session digiCode et digiCode expire datetime
        request.session[f"digiCode{member_email}"] = random.randint(100000, 999999)
        request.session[f"digiCode_expire{member_email}"] = str(datetime.datetime.now() +  datetime.timedelta(minutes=5))

        #sending email
        subject = 'BigAuth - Your Two-Factor Authentication (2FA) Code'
        message = f"""Hi {member_email},
                Your Two-Factor Authentication (2FA) code is: {request.session[f"digiCode{member_email}"]}
                This code will expire in 5 minutes. If you did not request this code, please secure your account immediately.
                Thank you,
                
                BigAuth"""

        email_from = env('EMAIL_HOST_USER')
        recipient_list = [member_email]   
        send_mail( subject, message, email_from, recipient_list )

    if request.method == "POST":
        form = digiCodeForm(request.POST)
        print("post")
        if form.is_valid():
            print("isValid")
            isValidCode = checkValidCode(request,form.cleaned_data['code'],datetime.datetime.now(), member_email)
            if isValidCode:
                print("here ")
                member = Member.objects.get(email=member_email) 
                login(request,member)
                member.update_last_login()
                print("okeee")
                request.session.pop(f"digiCode{member_email}", None)
                request.session.pop(f"digiCode_expire{member_email}", None)
                request.session.pop("member_email", None)
                return redirect('home_view')
            else:
                form.add_error('code', 'Code does not match or five minutes have passed')
                return render(request, 'code_a2f.html', {'form': form})
        else:
            form = digiCodeForm()

    return render(request, 'code_a2f.html', {'form': form})

def checkValidCode(request,member_code, datetime_now, member_email):
    print(member_code)
    print(f"digiCode{member_email}")
    print(datetime_now < datetime.datetime.strptime(request.session.get(f"digiCode_expire{member_email}"), "%Y-%m-%d %H:%M:%S.%f"))
    #check if code is correct and check datetime_expired passed 
    if member_code == request.session.get(f"digiCode{member_email}") and datetime_now < datetime.datetime.strptime(request.session.get(f"digiCode_expire{member_email}"), "%Y-%m-%d %H:%M:%S.%f"):
        return True
    else:
        return False
      
 # #send mail
# subject = 'Thank you for registering to our site'
# message = 'WELCOME !'
# email_from = env('EMAIL_HOST_USER')
# recipient_list = [form.cleaned_data['email']]   
# send_mail( subject, message, email_from, recipient_list )