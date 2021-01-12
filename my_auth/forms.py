from my_auth.services import get_user_by_mobile_number, get_user_by_username, mobile_number_is_validated, user_exists_by_mobile_number, validate_mobile_number
from django.contrib.auth.models import User
from django.forms.fields import CharField, RegexField
from django.forms.widgets import CheckboxInput, Widget
from django.core.validators import RegexValidator

from django import forms
from django.contrib.auth import (
    authenticate, get_user,
)
from django.contrib.auth.hashers import (
    UNUSABLE_PASSWORD_PREFIX,
)
from django.utils.translation import gettext, gettext_lazy as _

'''
validators 
'''
mobile_number_validator = RegexValidator(
    regex='09[0-9]{9}', 
    message='لطفا شماره موبایل صحیح را وارد کنید.', 
    code='invalid-mobile-number',
    )

'''
fields 
'''
mobile_number_field = lambda:forms.CharField(
    label=None,
    required=True,
    max_length=11,
    min_length=11,
    widget=forms.TextInput(attrs={
        'placeholder': 'موبایل',
        'class': 'input-login',
        'type': 'number',
        'pattern': '09[0-9]{9}',
    }),
    validators=[mobile_number_validator],
)

'''
error messages
'''
error_messages = {
    'invalid_login': _(
        "لطفا شماره موبایل و رمز صحیح را وارد فرمایید."
    ),
    'not_registered': _(
        "کاربری با این شماره تماس ثبت نشده است. لطفا ابتدا ثبت نام کنید."
    ),
    'inactive': _("این حساب کاربری غیر فعال است."),
    'registered': _("این شماره قبلا ثبت شده است."),
    'invalid_auth_code':_("کد وارد شده صحیح نمی باشد."),
    'password_inconsistency':_("رمز و تکرار رمز عبور باید یکسان باشند."),
    'validated_auth_code':_('لطفا ابتدا شماره موبایل خود را صحت سنجی نمایید.')
}
class AuthenticationForm(forms.Form):
    """
    this form is used for authentication of user
    """
    mobile_number = mobile_number_field()
    password = forms.CharField(
        required=True,
        strip=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'رمز عبور',
            'class': 'input-login'
        })
    )
    remember_me = forms.BooleanField(required=False, widget=CheckboxInput)

    error_messages = error_messages

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        mobile_number = self.cleaned_data.get('mobile_number')
        password = self.cleaned_data.get('password')
        self.remember_me = self.cleaned_data.get('remember_me')

        if mobile_number is not None and password:
            user = get_user_by_mobile_number(mobile_number)
            if user:
                self.user_cache = authenticate(
                    self.request, username=user.username, password=password)
                if self.user_cache is None:
                    # password is not consistent with username
                    self.get_invalid_login_error()
                else:
                    self.confirm_login_allowed(self.user_cache)
            else:
                # User by this mobile_number is not registered
                self.get_user_not_registered_error()

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
        raise forms.ValidationError(
            self.error_messages['invalid_login'],
            code='invalid_login',
        )

    def get_user_not_registered_error(self):
        raise forms.ValidationError(
            self.error_messages['not_registered'],
            code='not_registered',
        )

class ForgetPasswordMobileForm(forms.Form):
    '''
    this class handle get mobile from user when forget password 
    '''
    mobile_number = mobile_number_field()
    
    error_messages = error_messages

    def clean(self):
        # check user is exists
        mobile_number = self.cleaned_data.get('mobile_number')
        if mobile_number is not None:
            user = get_user_by_mobile_number(mobile_number)
            if user:
                if user:
                    self.confirm_login_allowed(user)
                    # send code to user
                else:
                    # profile is available but user not exists
                    pass
            else:
                self.not_registered()
            
        return self.cleaned_data



    def not_registered(self):
        raise forms.ValidationError(
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
    mobile_number = mobile_number_field()
    
    error_messages = error_messages

    def clean(self):
        # check user is exists
        mobile_number = self.cleaned_data.get('mobile_number')
        if mobile_number is not None:
            if not get_user_by_mobile_number(mobile_number):
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
        required=True,
        widget=forms.TextInput(attrs={
        'placeholder': 'کد احراز هویت',
        'class': 'input-login',
        'type': 'number',
        }),
    )

    mobile_number = forms.CharField(
        label = None, 
        max_length=11, 
        required=False,
        widget=forms.HiddenInput(),
        validators=[mobile_number_validator],
    )

    error_messages = error_messages

    def clean(self):
        mobile_number = self.cleaned_data.get('mobile_number')
        code = self.cleaned_data.get('code')
        if code is not None and mobile_number:
            if not validate_mobile_number(mobile_number, code):
                self.invalid_auth_code()

        return self.cleaned_data


    def invalid_auth_code(self):
        raise forms.ValidationError(
            self.error_messages['invalid_auth_code'],
            code='invalid_auth_code'
            )

class PasswordForm(forms.Form):
    
    mobile_number = forms.CharField(
        label = None, 
        max_length=11, 
        required=False,
        widget=forms.HiddenInput(),
    )
    password = forms.CharField(
        required=True,
        strip=False,
        min_length=5,
        max_length=12,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'رمز عبور',
            'class': 'input-login'
        })
    )
    confirm_password = forms.CharField(
        required=True,
        strip=False,
        min_length=5,
        max_length=12,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'تکرار رمز عبور',
            'class': 'input-login'
        })
    )

    def password_inconsistency(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError(
                    error_messages['password_inconsistency'],
                    code='password_inconsistency'
                )

    def registered(self, mobile_number):
        if user_exists_by_mobile_number(mobile_number):
            forms.ValidationError(
                error_messages['registered'],
                code='registered',
            )

    def not_registered(self, mobile_number):
        if not user_exists_by_mobile_number(mobile_number):
            forms.ValidationError(
                error_messages['not_registered'],
                code='not_registered',
            )


    def validated_auth_code(self, mobile_number):
        try:
            if not mobile_number_is_validated(mobile_number):
                forms.ValidationError(
                    error_messages['validated_auth_code'],
                    code='validated_auth_code'
                )
        except:
            forms.ValidationError(
                error_messages['validated_auth_code'],
                code='validated_auth_code'
            )


class ForgetPasswordDataForm(PasswordForm):
    '''
    this is the same as parent class PasswordForm
    '''

    def clean(self):
        mobile_number = self.cleaned_data.get('mobile_number')
        self.password_inconsistency()
        self.not_registered(mobile_number)
        self.validated_auth_code(mobile_number)
        return self.cleaned_data

class RegisterDataForm(PasswordForm):

    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'placeholder':'ایمیل',
            'class':'input-login',
            'type':'email',
        }),
        )

    reference_code = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
        'placeholder': 'کد معرف',
        'class': 'input-login',
        'type': 'text',
        'pattern': '[0-9]{6}',
        }),
        )

    def clean(self):
        mobile_number = self.cleaned_data.get('mobile_number')
        self.password_inconsistency()
        self.registered(mobile_number)
        self.validated_auth_code(mobile_number)
        return self.cleaned_data
