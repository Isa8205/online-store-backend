from django.forms import Form
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from authentication.models import User

class UserSignupForm(UserCreationForm):
    phone = forms.CharField(max_length=14)
    class Meta:
        model = User
        fields = ('last_name', 'email', 'username', 'phone')

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=20, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)