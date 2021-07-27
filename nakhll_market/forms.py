from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from .models import Profile



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

class ProfileForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        profile = kwargs['instance']
        self.fields['NationalCode'].widget = forms.TextInput(attrs={
            'class': 'form-control',
            'type':'number',
            'type' : 'text',
            'readonly': True if profile.NationalCode else False,
            'required': True
        })

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
            'CityPerCode', 
            'Image',
        ]
        widgets = {
            'Bio': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'text',
            }),
            'Sex': forms.Select(attrs={
                'class': 'form-control',
                'type':'text',
                'required':True,
            }),
            'MobileNumber': forms.TextInput(attrs={
                'class': 'form-control',
                'type':'number',
                'readonly' : 'readonly',
                'required':True,
            }),
            'BrithDay': forms.TextInput(attrs={
                 'class': 'form-control',
                 'type':'text',
                 'placeholder': '1300-01-01',
            }),
            'State': forms.TextInput(attrs={
                'class': 'form-control',
                'type':'text',
            }),
            'ZipCode': forms.TextInput(attrs={
                'class': 'form-control',
                'type':'number',
                'required':True,
            }),
            'Address': forms.TextInput(attrs={
                'class': 'form-control',
                'type':'text',
                'required':True,
            }),
            'TutorialWebsite': forms.Select(attrs={
                'class': 'form-control',
                'type':'text',
            }),
            'PhoneNumber': forms.TextInput(attrs={
                'class': 'form-control',
                'type':'Number',
                'required':True,
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

    def clean_NationalCode(self):
        national_code = self.cleaned_data['NationalCode'] 
        return national_code
     
class MyUserForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        fields = ('first_name', 'last_name', 'email')
        password = None
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'نام',
                'class': 'form-control',
                'type': 'text',
                'required': True
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'نام خانوادگی',
                'class': 'form-control',
                'type': 'text',
                'required': True
            }),
            'email': forms.TextInput(attrs={
                'placeholder': 'ایمیل',
                'class': 'form-control',
                'type': 'email',
            }),
        }
