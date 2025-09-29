from django import forms

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Your username',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))
    email = forms.CharField(widget=forms.EmailInput(attrs={
        'placeholder': 'Your email address',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Your password',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Repeat password',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))

class LoginForm(AuthenticationForm):
    class Meta:
        Model = User 
        fields = ('username', 'password')

    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Your username',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Your password',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'placeholder': 'Full name',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'Email address',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))
    phone = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Phone number (optional)',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))
    address_line1 = forms.CharField(max_length=255, widget=forms.TextInput(attrs={
        'placeholder': 'Address line 1',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))
    address_line2 = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Address line 2 (optional)',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))
    city = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'placeholder': 'City',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))
    state = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'placeholder': 'State/Province (optional)',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))
    postal_code = forms.CharField(max_length=20, widget=forms.TextInput(attrs={
        'placeholder': 'Postal/ZIP code',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))