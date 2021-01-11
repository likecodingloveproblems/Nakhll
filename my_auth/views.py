from my_auth.services import create_user, get_user_by_mobile_number, set_mobile_number_auth_code, set_session_expiration_time, set_user_password_by_mobile_number
from typing import Any, Dict
from django.contrib.messages.api import success
from django import forms, http
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from Payment.models import Wallet
from datetime import timedelta
from datetime import datetime
import json
from nakhll_market.views import set_session, visitor_ip_address
import random
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.http.response import HttpResponse, HttpResponseRedirect, JsonResponse

from django.utils import timezone
import requests
from nakhll.settings import REDIRECT_FIELD_NAME, SESSION_COOKIE_AGE, KAVENEGAR_KEY
from django.shortcuts import redirect, render, resolve_url
from django.urls.base import reverse, reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.contrib.auth import authenticate, login, logout

from nakhll_market.models import Profile
from sms.sms import Kavenegar
from my_auth.forms import ApproveCodeForm, AuthenticationForm, ForgetPasswordDataForm, ForgetPasswordMobileForm, RegisterDataForm, RegisterMobileForm
from nakhll.settings import LOGIN_REDIRECT_URL
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
import logging

logger = logging.getLogger(__name__)

# base get mobile controller
class GetMobile(FormView):
    context = {
        'header': None,
        'id':None,
        }

    template_name = str()
    form_class = None
    success_url = str()

    def form_valid(self, form) -> HttpResponse:
        mobile_number: str = form.cleaned_data.get('mobile_number')
        # send sms
        kavenegar = Kavenegar()
        code: str = kavenegar.generate_code(mobile_number)
        res: str = kavenegar.send(self.request, mobile_number, template='nakhl-register', token=code, type='sms')
        if res:
            messages.warning(self.request, res)
            return redirect(self.request.path)
        # set mobile number in session
        set_mobile_number(self.request, mobile_number)
        set_mobile_number_auth_code(mobile_number, code)
        return super().form_valid(form)

    def form_invalid(self, form: forms.Form) -> HttpResponse:
        return super().form_invalid(form)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        for item in self.context:
            kwargs[item] = self.context[item]
        return super().get_context_data(**kwargs)

class RegisterMobile(GetMobile):
    context = {
        'header': 'ثبت نام در سایت',
        'id':'register',
        }

    template_name = 'registration/get-mobile.html'
    form_class = RegisterMobileForm
    success_url = reverse_lazy('auth:register-code')

class ForgetPasswordMobile(GetMobile):
    context = {
        'header': 'فراموشی رمز عبور',
        'id':'forget-password',
        }

    template_name = 'registration/get-mobile.html'
    form_class = ForgetPasswordMobileForm
    success_url = reverse_lazy('auth:forget-password-code')

def set_mobile_number(request, mobile_number):
    request.session['mobile_number'] = mobile_number
    return request

def get_mobile_number(request):
    return request.session.get('mobile_number') or ''

class ApproveCode(FormView):
    template_name = 'registration/approveCode.html'
    form_class = ApproveCodeForm
    context = {}
    empty_mobile_number_url = str()

    def dispatch(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
        if not request.session.get('mobile_number'):
            messages.warning(request, 'ابتدا شماره موبایل خود را وارده کرده و کد احراز هویت را دریافت کنید.')
            return HttpResponseRedirect(self.empty_mobile_number_url)
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self) -> Dict[str, Any]:
        self.initial['mobile_number'] = get_mobile_number(self.request)
        return super().get_initial()

    def form_valid(self, form: ApproveCodeForm) -> HttpResponse:
        messages.success(self.request, 'کد وارد شده صحیح می باشد. لطفا اطلاعات مورد نظر را به دقت وارد فرمایید.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        for item in self.context:
            kwargs[item] = self.context[item]
        return super().get_context_data(**kwargs)

class RegisterCode(ApproveCode):
    context = {
        'header': 'ثبت نام در سایت',
        'id':'register',
        }
    success_url = reverse_lazy('auth:register-data')
    empty_mobile_number_url = reverse_lazy('auth:register-mobile')


class ForgetPasswordCode(ApproveCode):
    context = {
        'header': 'فراموشی رمز عبور',
        'id':'forget-password',
        }
    success_url = reverse_lazy('auth:forget-password-data')
    empty_mobile_number_url = reverse_lazy('auth:forget-password-mobile')



class RegisterData(FormView):
    """
    this function do all registration related tasks
    """
    template_name = 'registration/register-data.html'
    form_class = RegisterDataForm
    success_url = reverse_lazy('auth:login')

    def get_initial(self) -> Dict[str, Any]:
        self.initial['mobile_number'] = get_mobile_number(self.request)
        return super().get_initial()

    def form_valid(self, form: RegisterDataForm) -> HttpResponse:
        mobile_number = get_mobile_number(self.request)
        password = form.cleaned_data.get('password')
        email = form.cleaned_data.get('email')
        reference_code = form.cleaned_data.get('reference_code')
        user, profile, wallet = create_user(self.request, mobile_number, email, password, reference_code)
        if user and profile and wallet:
            messages.success(self.request, 'ثبت نام با موفقیت انجام شد.')
        else:
            messages.error(self.request, 'خطایی رخ داده است. لطفا با پشتیبانی تماس حاصل فرمایید.')
        return super().form_valid(form)

class ForgetPasswordData(FormView):
    '''
    this class handle all actions about setting password
    '''
    template_name = 'registration/forget-password-data.html'
    form_class = ForgetPasswordDataForm
    success_url = reverse_lazy('auth:login')

    def get_initial(self) -> Dict[str, Any]:
        self.initial['mobile_number'] = get_mobile_number(self.request)
        return super().get_initial()

    def form_valid(self, form: RegisterDataForm) -> HttpResponse:
        mobile_number = get_mobile_number(self.request)
        password = form.cleaned_data.get('password')
        user = set_user_password_by_mobile_number(mobile_number, password)
        if user:
            update_session_auth_hash(self.request, user)  # Important!
            messages.success(self.request, 'رمز شما با موفقیت تغییر کرد.')
            return super().form_valid(form)
        else:
            messages.error(self.request, 'خطایی رخ داده است لطفا با پشتیبانی تماس حاصل فرمایید.')
            return self.form_invalid(form)

class SuccessURLAllowedHostsMixin:
    success_url_allowed_hosts = set()

    def get_success_url_allowed_hosts(self):
        return {self.request.get_host(), *self.success_url_allowed_hosts}

class Login(SuccessURLAllowedHostsMixin, FormView):
    """
    Display the login form and handle the login action.
    """
    template_name = 'registration/login.html'
    form_class = AuthenticationForm
    success_url = LOGIN_REDIRECT_URL
    redirect_authenticated_user = True
    redirect_field_name = REDIRECT_FIELD_NAME


    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if self.redirect_authenticated_user and self.request.user.is_authenticated:
            redirect_to = self.get_success_url()
            return HttpResponseRedirect(redirect_to)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        '''
        this function login user
        '''
        # check if remember me is set, increase session life time
        if form.cleaned_data['remember_me']:
            set_session_expiration_time(
                self.request,
                timezone.now() + timedelta(seconds=SESSION_COOKIE_AGE)
                )
        login(self.request, form.user_cache)
        logger.info('request is in form_valid of Login class...')
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        url = self.get_redirect_url()
        return url or resolve_url(LOGIN_REDIRECT_URL)

    def get_redirect_url(self):
        """Return the user-originating redirect URL if it's safe."""
        # redirect_to = self.request.POST.get(
        #     self.redirect_field_name,
        #     self.request.GET.get(self.redirect_field_name, '')
        # )
        redirect_to = self.request.session.get('next')
        url_is_safe = is_safe_url(
            url=redirect_to,
            allowed_hosts=self.get_success_url_allowed_hosts(),
            require_https=self.request.is_secure(),
        )
        return redirect_to if url_is_safe else ''

def logout_(request):
    logout(request)
    return redirect(reverse('Profile:index'))
