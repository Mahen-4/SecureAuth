from django import forms
from .models import Member

#create form for Member model
class MemberForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput())
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = Member
        fields = ['email', 'password']

class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter your email"}),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Enter your password"}),
    )

class DigiCodeForm(forms.Form):
    code = forms.IntegerField(min_value=0, widget=forms.NumberInput())

class Reset_passwordForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput())

class New_passwordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput())