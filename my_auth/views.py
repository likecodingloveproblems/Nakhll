from django.views.generic.base import View
from Payment.models import Wallet
from ast import get_docstring
from nakhll_market.models import Profile
from my_auth.services import create_user, set_mobile_number_auth_code, set_session_expiration_time, set_user_password_by_mobile_number
from typing import Any, Dict
from django import forms, http
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from datetime import timedelta
from django.http.response import HttpResponse, HttpResponseRedirect, JsonResponse

from django.utils import timezone
from nakhll.settings import KAVENEGAR_KEY, REDIRECT_FIELD_NAME, SESSION_COOKIE_AGE
from django.shortcuts import redirect, resolve_url
from django.urls.base import reverse, reverse_lazy
from django.views.generic.edit import FormView
from django.contrib.auth import authenticate, login, logout

from sms.sms import Kavenegar
from my_auth.forms import ApproveCodeForm, AuthenticationForm, ForgetPasswordDataForm, ForgetPasswordMobileForm, RegisterDataForm, RegisterMobileForm , RegisterForm , LoginPasswordForm , LoginCodeForm ,  GetPhoneForm
from nakhll.settings import LOGIN_REDIRECT_URL
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
import logging
import random
from django.db import transaction, DatabaseError
from django.contrib.auth.models import User
from nakhll_market.models import Profile
from kavenegar import KavenegarAPI, APIException, HTTPException

logger = logging.getLogger(__name__)

# base get mobile controller


class GetMobile(FormView):
    context = {
        'header': None,
        'id': None,
    }

    template_name = str()
    form_class = None
    success_url = str()

    def form_valid(self, form) -> HttpResponse:
        mobile_number: str = form.cleaned_data.get('mobile_number')
        # send sms
        kavenegar = Kavenegar()
        code: str = kavenegar.generate_code(mobile_number)
        res: str = kavenegar.send(
            self.request, mobile_number, template='nakhl-register', token=code, type='sms')
        if res:
            messages.warning(self.request, res)
            return redirect(self.request.path)
        # set mobile number in session
        # set_mobile_number(self.request, mobile_number)
        set_mobile_number_auth_code(mobile_number, code)
        set_mobile_number_session(self.request, mobile_number)
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        for item in self.context:
            kwargs[item] = self.context[item]
        return super().get_context_data(**kwargs)



class ForgetPasswordMobile(GetMobile):
    context = {
        'header': 'فراموشی رمز عبور',
        'id': 'forget-password',
    }

    template_name = 'registration/get-mobile.html'
    form_class = ForgetPasswordMobileForm
    success_url = reverse_lazy('auth:forget-password-code')


def set_mobile_number_session(request, mobile_number):
    request.session['auth'] = {
        'mobile_number':mobile_number,
        'verify':False,
        }
    return request

def is_mobile_number_verify_session(request, mobile_number: str) -> bool:
    if get_mobile_number_session(request) == mobile_number:
        if request.session['auth']['verify'] == True:
            return True
    return False

def verify_mobile_number_session(request):
    if request.session.get('auth')['mobile_number'] == get_mobile_number_session(request):
        request.session['auth']['verify'] = True

def get_mobile_number_session(request):
    """get mobile number of user from its session

    Args:
        request ([type]): user wsgi request

    Returns:
        str: user mobile_number or str()
    """
    return request.session.get('auth')['mobile_number'] or ''


class ApproveCode(FormView):
    template_name = 'registration/approve-code.html'
    form_class = ApproveCodeForm
    context = {}
    empty_mobile_number_url = str()

    def dispatch(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
        if not get_mobile_number_session(request):
            messages.warning(
                request, 'ابتدا شماره موبایل خود را وارده کرده و کد احراز هویت را دریافت کنید.')
            return HttpResponseRedirect(self.empty_mobile_number_url)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['mobile_number'] = get_mobile_number_session(self.request)
        return kwargs

    def form_valid(self, form: ApproveCodeForm) -> HttpResponse:
        messages.success(
            self.request, 'کد وارد شده صحیح می باشد. لطفا اطلاعات مورد نظر را به دقت وارد فرمایید.')
        verify_mobile_number_session(self.request)
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        for item in self.context:
            kwargs[item] = self.context[item]
        return super().get_context_data(**kwargs)

class ForgetPasswordCode(ApproveCode):
    context = {
        'header': 'فراموشی رمز عبور',
        'id': 'forget-password',
    }
    success_url = reverse_lazy('auth:forget-password-data')
    empty_mobile_number_url = reverse_lazy('auth:forget-password-mobile')


class ForgetPasswordData(FormView):
    '''
    this class handle all actions about setting password
    '''
    template_name = 'registration/forget-password-data.html'
    form_class = ForgetPasswordDataForm
    success_url = reverse_lazy('auth:get-phone')

    def dispatch(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
        if not is_mobile_number_verify_session(request, get_mobile_number_session(request)):
            messages.warning(request, 'لطفا ابتدا شماره موبایل خود را تایید کنید.')
            return HttpResponseRedirect(reverse('auth:forget-password-mobile'))
        return super().dispatch(request, *args, **kwargs)


    def form_valid(self, form: RegisterDataForm) -> HttpResponse:
        mobile_number = get_mobile_number_session(self.request)
        password = form.cleaned_data.get('password')
        user = set_user_password_by_mobile_number(mobile_number, password)
        if user:
            update_session_auth_hash(self.request, user)  # Important!
            messages.success(self.request, 'رمز شما با موفقیت تغییر کرد.')
            return super().form_valid(form)
        else:
            messages.error(
                self.request, 'خطایی رخ داده است لطفا با پشتیبانی تماس حاصل فرمایید.')
            return self.form_invalid(form)


class SuccessURLAllowedHostsMixin:
    success_url_allowed_hosts = set()

    def get_success_url_allowed_hosts(self):
        return {self.request.get_host(), *self.success_url_allowed_hosts}


def logout_(request):
    logout(request)
    return redirect(reverse('nakhll_market:index'))



def get_user_exists(phone_number):
    return Profile.objects.filter(MobileNumber=phone_number).exists()

def get_user_has_password(user):
    return user.password != ''

def generate_code():
    return str(random.randint(100000, 999999))

def get_user_by_phone_number(phone_number):
    profile = Profile.objects.get(MobileNumber=phone_number)
    return profile.FK_User

def get_prev_code(request):
    return request.session.get('auth-code')

def set_code(request):
    # generate code and set it to session
    code = get_prev_code(request) or generate_code()
    phone_number = get_phone_number(request)
    # send code by sms to user
    params = {
        'receptor': phone_number,
        'template': 'nakhl-register',
        'token': code,
        'type': 'sms',
    }
    try:
        KavenegarAPI(KAVENEGAR_KEY)\
            .verify_lookup(params)
    except APIException as e: 
        messages.error(request, 'خطایی رخ داده است. لطفا با پشتیبانی تماس بگیرید.')
        print(e)
    except HTTPException as e: 
        messages.error(request, 'خطایی رخ داده است. لطفا با پشتیبانی تماس بگیرید.')
        print(e)
    request.session['auth-code'] = code

def create_user_profile(request, phone_number):
    # check user and profile and wallet for this phone is not set
    # and do all DB operations transactional
    try:
        with transaction.atomic():
            user = User.objects.create(username=phone_number)
            profile = Profile.objects.create(MobileNumber=phone_number, FK_User=user)
            Wallet.objects.create(FK_User=user)

    except DatabaseError as e:
        # TODO log error 
        # return a message to the user that it may be has a
        # record in User or Profile or Wallet, or maybe another reason
        messages.error(request, 'با عرض پوزش خطایی رخ داده است. لطفا با پشتیبانی ارتباط بگیرید.')
        return redirect('auth:get-phone')

def get_phone_number(request):
    return _get_phone_number(request)

def _get_phone_number(requset):
    return requset.session.get('phone_number')

def get_code(request):
    return _get_code(request)

def _get_code(request):
    return request.session.get('auth-code')

def next_redirect(request, url_name):
    next = request.GET.get('next')
    if next:
        url = '{}?next={}'.format(reverse(url_name), next)
        request.full_path = url
    else:
        url = reverse(url_name)
        request.full_path = url
    return HttpResponseRedirect(url)

class CheckUserIsAuthenticated(SuccessURLAllowedHostsMixin):
    redirect_authenticated_user = True

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if self.redirect_authenticated_user and self.request.user.is_authenticated:
            redirect_to = self.get_success_url()
            return HttpResponseRedirect(redirect_to)
        return super().dispatch(request, *args, **kwargs)


    def get_success_url(self):
        url = self.get_redirect_url()
        return url or resolve_url(LOGIN_REDIRECT_URL)

    def get_redirect_url(self):
        """Return the user-originating redirect URL if it's safe."""
        redirect_to = self.request.GET.get('next')
        url_is_safe = is_safe_url(
            url=redirect_to,
            allowed_hosts=self.get_success_url_allowed_hosts(),
            require_https=self.request.is_secure(),
        )
        return redirect_to if url_is_safe else ''

class GetPhoneNumber:

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs = super().get_context_data(**kwargs)
        kwargs['phone_number'] = get_phone_number(self.request)
        return kwargs

class GetAuthCodeAndPhone(GetPhoneNumber):

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['auth_code'] = get_code(self.request)
        return kwargs


class GetPhone(CheckUserIsAuthenticated, FormView):
    template_name = 'registration/get-phone.html'
    form_class = GetPhoneForm

    def set_phone_number(self, phone_number):
        self._set_phone_number(phone_number)

    def _set_phone_number(self, phone_number):
        self.request.session['phone_number'] = phone_number

    def form_valid(self, form) -> HttpResponse:
        phone_number = form.cleaned_data.get('phone_number')
        # set phone number to session
        # user exists
        # no -> Register
        # yes -> check user has password
        # yes -> no -> LoginCode
        # yes -> yes -> LoginPassword
        self.set_phone_number(phone_number)
        if get_user_exists(phone_number):
            user = get_user_by_phone_number(phone_number)
            if get_user_has_password(user):
                return next_redirect(self.request, 'auth:login-password')
            else:
                set_code(self.request)
                return next_redirect(self.request, 'auth:login-code')
        else:
            # set code
            set_code(self.request)
            return  next_redirect(self.request, 'auth:register')

class Register(GetAuthCodeAndPhone, CheckUserIsAuthenticated ,FormView):
    template_name = 'registration/register.html'
    form_class = RegisterForm

    def form_valid(self, form) -> HttpResponse:
        phone_number = get_phone_number(self.request)
        # create user
        error = create_user_profile(self.request, phone_number)
        if error:
            return error
        # login
        user = get_user_by_phone_number(phone_number)
        login(self.request, user)
        return HttpResponseRedirect(self.get_success_url())

class LoginPassword(GetPhoneNumber, CheckUserIsAuthenticated, FormView):
    template_name = 'registration/loginpassword.html'
    form_class = LoginPasswordForm

    def form_valid(self, form) -> HttpResponse:
        phone_number = get_phone_number(self.request)
        user = get_user_by_phone_number(phone_number)
        login(self.request, user)
        return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['phone_number'] = get_phone_number(self.request)
        kwargs['request'] = self.request
        return kwargs

class LoginCode(GetAuthCodeAndPhone, CheckUserIsAuthenticated, FormView):
    template_name = 'registration/logincode.html'
    form_class = LoginCodeForm

    def form_valid(self, form) -> HttpResponse:
        phone_number = get_phone_number(self.request)
        user = get_user_by_phone_number(phone_number)
        login(self.request, user)
        return HttpResponseRedirect(self.get_success_url())

class GetCode(View, CheckUserIsAuthenticated):

    def get(self, request):
        set_code(request)
        url = request.GET.get('next')
        return JsonResponse({'message': 'کد با موفقیت ارسال گردید'})