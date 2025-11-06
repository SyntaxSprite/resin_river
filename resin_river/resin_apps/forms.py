from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Your username',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
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
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email already exists.')
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError({
                'password2': 'Passwords do not match.'
            })
        
        return cleaned_data

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
    # Contact Section
    contact_email_phone = forms.CharField(
        max_length=255,
        label='Email or mobile phone number',
        widget=forms.TextInput(attrs={
            'placeholder': 'Email or mobile phone number',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black'
        })
    )
    email_news = forms.BooleanField(
        required=False,
        initial=True,
        label='Email me with news and offers'
    )
    
    # Delivery Section
    delivery_country = forms.CharField(
        max_length=100,
        initial='United States',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black'
        })
    )
    delivery_first_name = forms.CharField(
        max_length=100,
        required=False,
        label='First name (optional)',
        widget=forms.TextInput(attrs={
            'placeholder': 'First name (optional)',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black'
        })
    )
    delivery_last_name = forms.CharField(
        max_length=100,
        label='Last name',
        widget=forms.TextInput(attrs={
            'placeholder': 'Last name',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black'
        })
    )
    delivery_address = forms.CharField(
        max_length=255,
        label='Address',
        widget=forms.TextInput(attrs={
            'placeholder': 'Address',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black'
        })
    )
    delivery_city = forms.CharField(
        max_length=100,
        label='City',
        widget=forms.TextInput(attrs={
            'placeholder': 'City',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black'
        })
    )
    delivery_state = forms.CharField(
        max_length=100,
        label='State',
        widget=forms.TextInput(attrs={
            'placeholder': 'State',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black'
        })
    )
    delivery_postal_code = forms.CharField(
        max_length=20,
        required=False,
        label='Postal code (optional)',
        widget=forms.TextInput(attrs={
            'placeholder': 'Postal code (optional)',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black'
        })
    )
    delivery_phone = forms.CharField(
        max_length=30,
        label='Phone',
        widget=forms.TextInput(attrs={
            'placeholder': 'Phone',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black'
        })
    )
    save_delivery_info = forms.BooleanField(
        required=False,
        label='Save this information for next time'
    )
    text_news = forms.BooleanField(
        required=False,
        label='Text me with news and offers'
    )
    
    # Payment Section - will be populated dynamically
    payment_method = forms.ChoiceField(
        choices=[],
        widget=forms.RadioSelect(attrs={
            'class': 'payment-method-radio'
        })
    )
    
    def __init__(self, *args, **kwargs):
        payment_methods = kwargs.pop('payment_methods', None)
        super().__init__(*args, **kwargs)
        if payment_methods:
            self.fields['payment_method'].choices = [
                (str(pm.id), pm.display_name) for pm in payment_methods
            ]
    
    # Billing Address Section
    billing_same_as_shipping = forms.BooleanField(
        required=False,
        initial=True,
        label='Same as shipping address'
    )
    use_different_billing = forms.BooleanField(
        required=False,
        label='Use a different billing address'
    )
    
    # Billing fields (only required if use_different_billing is True)
    billing_country = forms.CharField(
        max_length=100,
        required=False,
        label='Country/Region',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black'
        })
    )
    billing_first_name = forms.CharField(
        max_length=100,
        required=False,
        label='First name (optional)',
        widget=forms.TextInput(attrs={
            'placeholder': 'First name (optional)',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black'
        })
    )
    billing_last_name = forms.CharField(
        max_length=100,
        required=False,
        label='Last name',
        widget=forms.TextInput(attrs={
            'placeholder': 'Last name',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black'
        })
    )
    billing_address = forms.CharField(
        max_length=255,
        required=False,
        label='Address',
        widget=forms.TextInput(attrs={
            'placeholder': 'Address',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black'
        })
    )
    billing_city = forms.CharField(
        max_length=100,
        required=False,
        label='City',
        widget=forms.TextInput(attrs={
            'placeholder': 'City',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black'
        })
    )
    billing_state = forms.CharField(
        max_length=100,
        required=False,
        label='State',
        widget=forms.TextInput(attrs={
            'placeholder': 'State',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black'
        })
    )
    billing_postal_code = forms.CharField(
        max_length=20,
        required=False,
        label='Postal code (optional)',
        widget=forms.TextInput(attrs={
            'placeholder': 'Postal code (optional)',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black'
        })
    )
    billing_phone = forms.CharField(
        max_length=30,
        required=False,
        label='Phone (optional)',
        widget=forms.TextInput(attrs={
            'placeholder': 'Phone (optional)',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        use_different_billing = cleaned_data.get('use_different_billing')
        billing_same_as_shipping = cleaned_data.get('billing_same_as_shipping')
        
        # If using different billing address, require billing fields
        if use_different_billing and not billing_same_as_shipping:
            required_billing_fields = ['billing_last_name', 'billing_address', 'billing_city', 'billing_state']
            for field in required_billing_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, 'This field is required when using a different billing address.')
        
        return cleaned_data