from django import forms
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from .models import Newsletters

# Login Form
class Login (forms.Form):
    username=forms.CharField()
    password=forms.CharField()

    def clean_password (self):
        data=self.cleaned_data['password']

        if len(data) < 8:
           raise ValidationError(_('طول عبارت ورودی کوتاه می باشد.'))

        return data

# Add Email Form
class CheckEmail (forms.Form):

    email=forms.EmailField()

    def clean_email(self):

        email = self.cleaned_data.get('email')

        if validate_email(email):
            return email

