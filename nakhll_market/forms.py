from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import ugettext_lazy as _

from nakhll_market.models import Profile

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


# update Profile Form
class ProfileForm(forms.ModelForm):
    class Meta:
        model= Profile
        fields= [
            'Sex',
            'MobileNumber',
            'ZipCode',
            'PhoneNumber',
            'NationalCode',
            'Address',
            'State',
            'BigCity',
            'City',
            'BrithDay',
            'Bio',
            'TutorialWebsite',
            'CountrPreCode',
            'CityPerCode'
        ]
        widgets = {
            'Bio': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'text',
            }),
            'Sex': forms.TextInput(attrs={
                'class': 'form-control',
                'type':'text',
            }),
            'MobileNumber': forms.TextInput(attrs={
                'class': 'form-control',
                'type':'number',
            }),
            'NationalCode': forms.TextInput(attrs={
                'class': 'form-control',
                'type':'number',
            }),
            'BrithDay': forms.TextInput(attrs={
                'class': 'form-control',
                'type':'Date',
            }),
            'State': forms.TextInput(attrs={
                'class': 'form-control',
                'type':'text',
            }),
            'ZipCode': forms.TextInput(attrs={
                'class': 'form-control',
                'type':'number',
            }),
            'Address': forms.TextInput(attrs={
                'class': 'form-control',
                'type':'text',
            }),
            'TutorialWebsite': forms.TextInput(attrs={
                'class': 'form-control',
                'type':'text',
            }),
            'PhoneNumber': forms.TextInput(attrs={
                'class': 'form-control',
                'type':'Number',
            }),
            'CityPerCode': forms.TextInput(attrs={
                'class': 'form-control',
                'type':'Number',
            }),
            'CountrPreCode': forms.TextInput(attrs={
                'class': 'form-control',
                'type':'Number',
            }),
         }


        
     
class MyUserForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        fields = ('first_name', 'last_name', 'email')
        password = None
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'نام',
                'class': 'form-control',
                'type': 'text',
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'نام خانوادگی',
                'class': 'form-control',
                'type': 'text',
            }),
            'email': forms.TextInput(attrs={
                'placeholder': 'ایمیل',
                'class': 'form-control',
                'type': 'email',
            }),
        }

# class ProfileDashboard(forms.Form):
#     first_name = forms.CharField(
#         label=None,
#         required=True,
#         max_length=50,
#         widget=forms.TextInput(attrs={
#                 'placeholder': 'نام',
#                 'class': 'form-control',
#                 'type': 'text',
#             }),
#     )
#     last_name = forms.CharField(
#         label=None,
#         required=True,
#         max_length=50,
#         widget=forms.TextInput(attrs={
#                 'placeholder': 'نام خانوادگی',
#                 'class': 'form-control',
#                 'type': 'text',
#             }),
#     )
#     email = forms.EmailField(
#         label=None,
#         required=False,
#         max_length=127,
#         widget=forms.TextInput(attrs={
#                 'placeholder': 'ایمیل',
#                 'class': 'form-control',
#                 'type': 'email',
#             }),
#     )
