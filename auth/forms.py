from django.forms.widgets import CheckboxInput
from nakhll_market.models import Profile


from django import forms
from django.contrib.auth import (
    authenticate,
)
from django.contrib.auth.hashers import (
    UNUSABLE_PASSWORD_PREFIX,
)
from django.utils.translation import gettext, gettext_lazy as _


class AuthenticationForm(forms.Form):
    """
    this form is used for authentication of user
    """
    mobile_number = forms.CharField(
        label=None,
        required=True,
        max_length=11,
        min_length=11,
        widget=forms.TextInput(attrs={
            'placeholder': 'موبایل',
            'class': 'input-login login-input-modal',
            'type': 'number',
            'pattern': '[0-9]{11}',
        }),
    )
    password = forms.CharField(
        required=True,
        strip=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'رمز عبور',
            'class': 'input-login login-input-modal'
        })
    )
    remember_me = forms.BooleanField(required=False, widget=CheckboxInput)

    error_messages = {
        'invalid_login': _(
            "لطفا شماره موبایل و رمز صحیح را وارد فرمایید."
        ),
        'not_registered': _(
            "کاربری با این شماره تماس ثبت نشده است. لطفا ابتدا ثبت نام کنید."
        ),
        'inactive': _("این حساب کاربری غیر فعال است."),
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        self.mobile_number = self.cleaned_data.get('mobile_number')
        password = self.cleaned_data.get('password')
        self.remember_me = self.cleaned_data.get('remember_me')

        if self.mobile_number is not None and password:
            if Profile.objects.filter(MobileNumber=self.mobile_number).exists():
                profile = Profile.objects.get(MobileNumber=self.mobile_number)
                user = profile.FK_User
                self.user_cache = authenticate(
                    self.request, username=user.username, password=password)
                if self.user_cache is None:
                    # password is not consistent with username
                    raise self.get_invalid_login_error()
                else:
                    self.confirm_login_allowed(self.user_cache)
            else:
                # User by this mobile_number is not registered
                raise self.get_user_not_registered_error()

        return self.cleaned_data

    def get_user(self):
        return self.user_cache

    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.

        If the given user cannot log in, this method should raise a
        ``forms.ValidationError``.

        If the given user may log in, this method should return None.
        """
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

    def get_invalid_login_error(self):
        return forms.ValidationError(
            self.error_messages['invalid_login'],
            code='invalid_login',
        )

    def get_user_not_registered_error(self):
        return forms.ValidationError(
            self.error_messages['not_registered'],
            code='not_registered',
        )

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

class RegisterMobileForm(forms.Form):
    '''
    this class handle get mobile from user for validation of mobile number for registration process
    '''
    mobile_number = mobile_number_field
    
    error_messages = error_messages

    def clean(self):
        # check user is exists
        self.mobile_number = self.cleaned_data.get('mobile_number')
        if self.mobile_number is not None:
            if not (Profile.objects.filter(MobileNumber=self.mobile_number).exists()):
                pass
            else:
                self.registered()

        return self.cleaned_data



    def registered(self):
        raise forms.ValidationError(
            self.error_messages['registered'],
            code='registered',
        )

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

class ApproveCodeForm(forms.Form):
    code = forms.CharField(
        label=None, 
        max_length=6, 
        min_length=6,
        required=True,
        widget=forms.TextInput(attrs={
        'placeholder': 'کد احراز هویت',
        'class': 'input-login login-input-modal',
        'type': 'number',
        'pattern': '[0-9]{6}',
         }),
        )

    mobile_number = forms.CharField(
        label = None, 
        max_length=11, 
        required=False,
        widget=forms.HiddenInput(),
    )

    error_messages = error_messages

    def clean(self):
        mobile_number = self.cleaned_data.get('mobile_number')
        code = self.cleaned_data.get('code')
        if code is not None and mobile_number:
            if UserphoneValid.objects.filter(MobileNumber=mobile_number, ValidCode=code).exists():
                # user enter the correct register code
                userphoneValid = UserphoneValid.objects.get(
                    MobileNumber=mobile_number)
                userphoneValid.Validation = True
                userphoneValid.save()
            else:
                self.invalid_auth_code()

        return self.cleaned_data


    def invalid_auth_code(self):
        raise forms.ValidationError(
            self.error_messages['invalid_auth_code'],
            code='invalid_auth_code'
            )