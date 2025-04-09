from django.shortcuts import render, redirect
from authSys.models import Member, UuidCode
from .forms import MemberForm, LoginForm, DigiCodeForm, Reset_passwordForm, New_passwordForm
import django.contrib.auth.password_validation as validators
from django.core import exceptions
from django.contrib.auth.hashers import make_password
import environ
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.urls import reverse
import random
import datetime
import uuid
from django.utils import timezone
from django.contrib import messages
import logging

#load env variables
env = environ.Env()

# register function 
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
            
            messages.success(request, "Account created !")

            # add logs info
            logger = logging.getLogger('custom')
            logger.info("User created and added to table")

            return redirect('authSys:login') 
    else:
        form = MemberForm() #return empty form


    return render(request, 'register.html', {'form': form})

#login function
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
                form.add_error(None, "Email or password is incorrect !")

                # add logs info
                logger = logging.getLogger('custom')
                logger.info("User connexion failed")

                return render(request, "login.html", {'form': form})
    else:
        form = LoginForm() #return empty form
    
    return render(request, 'login.html', {'form': form})

#logout function
def logout_member(request):
    logout(request)
    return redirect("authSys:login");

#send code by mail and login if code is right
def code_a2f_member(request):
    member_email = request.session.get('member_email')
    form = DigiCodeForm(request.POST or None)

    #if user didn't at least put correct credentials  or already loged in 
    if member_email is None or request.user.is_authenticated:
        return redirect("authSys:login")

    # Expire check
    expire_time_str = request.session.get(f"digiCode_expire{member_email}")
    if expire_time_str:

        expire_time = datetime.datetime.strptime(expire_time_str, "%Y-%m-%d %H:%M:%S.%f")

        if datetime.datetime.now() > expire_time:

            #if expired delete session digiCode data
            request.session.pop(f"digiCode{member_email}", None)
            request.session.pop(f"digiCode_expire{member_email}", None)

            form.add_error('code', "Code expired, new code sended")
            return render(request, 'code_a2f.html', {'form': form, "resend": True})

   
    #check if credential valid and there is a user but not connected and code dosn't exist already
    if request.session.get(f"digiCode{member_email}") is None:

        #add to session digiCode et digiCode expire datetime
        request.session[f"digiCode{member_email}"] = random.randint(100000, 999999) 
        request.session[f"digiCode_expire{member_email}"] = str(datetime.datetime.now() +  datetime.timedelta(minutes=5)) # add 5 minute from now datetime

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

        # add logs info
        logger = logging.getLogger('custom')
        logger.info("Mail for A2F code sent")
        
        messages.success(request, "Mail sended, please check you mailbox")

    if request.method == "POST":
        #get data from form
        form = DigiCodeForm(request.POST)

        if form.is_valid():

            isValidCode = checkValidCode(request,form.cleaned_data['code'],datetime.datetime.now(), member_email)

            if isValidCode:

                #if valid get member with email only (all test passed)
                member = Member.objects.get(email=member_email) 
                login(request,member) 
                member.update_last_login()

                #delete all session data about a2f
                request.session.pop(f"digiCode{member_email}", None)
                request.session.pop(f"digiCode_expire{member_email}", None)
                request.session.pop("member_email", None)

                # add logs info
                logger = logging.getLogger('custom')
                logger.info("User Connected to app")

                return redirect('home_view')
            else:
                form.add_error('code', 'Code does not match or five minutes have passed')
                return render(request, 'code_a2f.html', {'form': form})
        else:
            form = DigiCodeForm() #return empty form

    return render(request, 'code_a2f.html', {'form': form})

#check if code is valid
def checkValidCode(request,member_code, datetime_now, member_email):
    #check if code is correct and check datetime_expired passed 
    if member_code == request.session.get(f"digiCode{member_email}") and datetime_now < datetime.datetime.strptime(request.session.get(f"digiCode_expire{member_email}"), "%Y-%m-%d %H:%M:%S.%f"):
        return True
    else:
        return False
      
#reset password function
def reset_password_member(request):
    
    if request.method  == 'POST':
        form = Reset_passwordForm(request.POST)
        if form.is_valid():
            member_email = form.cleaned_data['email']
            #if email exist in db send email
            if Member.objects.filter(email=member_email).exists() :
                #get member object
                member = Member.objects.get(email=member_email)
                code = uuid.uuid4() # create uuid code
                code_todb = UuidCode(id_member=member,code_uuid=code, expiration_datetime=timezone.now()  +  datetime.timedelta(minutes=10))
                code_todb.save() # save code to table

                #sending email
                subject = 'BigAuth - Reset password link'
                message = f"""Hi {member_email},
                        Your password reset link is : http://127.0.0.1:8000/auth/new_password/{code}
                        This link will expire in 10 minutes. If you did not request this code, please secure your account immediately.
                        Thank you,
                        
                        BigAuth"""

                email_from = env('EMAIL_HOST_USER')
                recipient_list = [member_email]   
                send_mail( subject, message, email_from, recipient_list )
                messages.success(request, "Mail sended, please check you mailbox")

                # add logs info
                logger = logging.getLogger('custom')
                logger.info("Mail for reset password sent")

            else:
                form.add_error('email', "this email doesn't exist")
                return render(request,'reset_password.html', {'form': form})
            
    else:
        form = Reset_passwordForm() #return empty form

    return render(request,'reset_password.html', {'form': form})

def new_password_member(request, uuid):

    
    if uuid is None: redirect('authSys:register') # if none redirect to register

    #check if uuid exist in table
    uuidCode_object = UuidCode.objects.filter(code_uuid=uuid).first()
    if uuidCode_object is not None:
        member = Member.objects.get(id=uuidCode_object.id_member_id) # get the member linked to

    if request.method == "POST":
        form = New_passwordForm(request.POST)
        if form.is_valid():
            #set hash password 
            member.set_password(form.cleaned_data['password']) 
            member.save() # save to table
            messages.success(request, "Password updated")

            # add logs info
            logger = logging.getLogger('custom')
            logger.info("Member table password field updated")


            return redirect('authSys:login')
    else:
        form = New_passwordForm()

    return render(request,'new_password.html', {'form': form})