from django import forms
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from .models import Newsletters
from nakhll_market.models import Profile
from django.contrib.auth.forms import UserChangeForm
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
        fields= ['Sex','MobileNumber','ZipCode','PhoneNumber','NationalCode', 'Address', 'State', 'BigCity', 'City', 'BrithDay','Bio', 'TutorialWebsite','ReferenceCode', 'UserReferenceCode','CityPerCode']


class MyUserForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        fields = ['first_name' , 'last_name' , 'email']
        password = None
