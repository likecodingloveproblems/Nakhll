from django.contrib.messages.api import success
from Payment.models import Wallet
from datetime import timedelta
from datetime import datetime
import json
from nakhll_market.views import visitor_ip_address
import random
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.http.response import HttpResponse, JsonResponse

from django.utils import timezone
import requests
from nakhll.settings import SESSION_COOKIE_AGE, KAVENEGAR_KEY
from django.shortcuts import redirect, render
from django.urls.base import reverse
from django.views.generic.base import TemplateView
from django.contrib.auth import authenticate, login, logout

from nakhll_market.models import Profile, SMS, UserphoneValid


from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

# a class that define site user


class SiteUser:
    def __init__(self, mobile_number, password) -> None:
        self.mobile_number = mobile_number
        self.password = password

    def is_national_code_valid(self):
        import re
        if not re.search(r'^\d{10}$', input):
            return False

        check = int(input[9])
        s = sum([int(input[x]) * (10 - x) for x in range(9)]) % 11
        return (s < 2 and check == s) or (s >= 2 and check + s == 11)

    def is_email_valid(self):
        from validate_email import validate_email
        # verify==True check that email smtp server exists
        is_valid = validate_email(self.email, verify=True)
        return is_valid

# base get mobile controller


class GetMobile(TemplateView):
    template = 'registration/registerMobile.html'
    context = {}

    def main(self, request, mobile_number):
        pass


    def get(self, request):
        return render(request, self.template, self.context)

    def post(self, request):
        mobile_number = request.POST.get("mobilenumber", None)
        if not mobile_number:
            mobile_number = request.session.get('mobile_number')
        # validation of phone number
        if (len(mobile_number) == 11 and mobile_number[0] == '0' and mobile_number.isdigit()):
            pass
        else:
            messages.warning(request, 'شماره وارد شده صحیح نمی باشد.')
            return render(request, self.template, self.context)

        if (mobile_number):
            result = self.main(request, mobile_number)
            if result:
                return result

        else:
            messages.warning(request, 'شماره وارد شده نامعتبر است!')
        return render(request, self.template, self.context)


class RegisterMobile(GetMobile):
    context = {
        'header': 'ثبت نام در سایت',
        'id':'register'}

    def main(self, request, mobile_number):
        if not Profile.objects.filter(MobileNumber=mobile_number).exists():
            # check that user is not overloading SMS with many requests
            ten_minutes_ago = timezone.now() + timedelta(minutes=-10)
            num_last_10_min_sms = SMS.objects.filter(
                entries_receptor=mobile_number, datetime__gte=ten_minutes_ago).count()
            if num_last_10_min_sms > 5:  # 5 number in 10 minutes
                messages.warning(request, 'شما بیشتر از تعداد مجاز سعی کردید. 10 دقیقه دیگر تلاش کنید.')

            else:
                # the user has more opportunity
                regcode = str(random.randint(100000, 999999))
                if not UserphoneValid.objects.filter(MobileNumber=mobile_number).exists():
                    userphoneValid = UserphoneValid(
                        MobileNumber=mobile_number, ValidCode=regcode, Validation=False)
                    userphoneValid.save()
                try:
                    userphoneValid = UserphoneValid.objects.get(
                        MobileNumber=mobile_number)
                    userphoneValid.ValidCode = regcode
                    userphoneValid.Validation = False
                    userphoneValid.save()
                    url = 'https://api.kavenegar.com/v1/{}/verify/lookup.json'.format(KAVENEGAR_KEY)
                    params = {'receptor': mobile_number,
                                'token': regcode, 'template': 'nakhl-register'}
                    res = requests.post(url, params=params)
                    text = json.loads(res.text)
                    app_timezone = timezone.get_default_timezone()

                    SMS.objects.create(
                        return_status=text['return']['status'],
                        return_message=text['return']['message'],
                        entries_cost=text['entries'][0]['cost'],
                        entries_datetime=datetime.fromtimestamp(
                            text['entries'][0]['date']).astimezone(app_timezone),
                        entries_receptor=text['entries'][0]['receptor'],
                        entries_sender=text['entries'][0]['sender'],
                        entries_statustext=text['entries'][0]['statustext'],
                        entries_status=text['entries'][0]['status'],
                        entries_message=text['entries'][0]['message'],
                        entries_messageid=text['entries'][0]['messageid'],
                    )

                    if res.status_code == 200:  # TODO check more detail flow chart of kevenegar to be sure that the message is sent
                        # kevenegar post method is successful
                        request = set_mobile_number(request, mobile_number)
                        messages.success(request, 'کد تایید با موفقیت ارسال شد.')
                        return redirect(reverse('auth:register-code'))
                    else:

                        messages.warning(request,'سامانه پیامکی با مشکل مواجه شه است. لطفا با پشتیبانی تماس حاصل فرمایید.')

                except:

                    messages.warning(request,'خطای دریافت شماره تماس')

        else:

            messages.warning(request,'این کاربر قبلا ثبت نام کرده است ! ')


class ForgetPasswordMobile(GetMobile):
    context = {
        'header': 'فراموشی رمز عبور',
        'id':'forget-password',
        }

    def main(self, request, mobile_number):
        if Profile.objects.filter(MobileNumber=mobile_number).exists():
            # check that user is not overloading SMS with many requests
            ten_minutes_ago = timezone.now() + timedelta(minutes=-10)
            num_last_10_min_sms = SMS.objects.filter(
                entries_receptor=mobile_number, datetime__gte=ten_minutes_ago).count()
            if num_last_10_min_sms > 5:  # 5 number in 10 minutes
                messages.warning(request, 'شما بیشتر از تعداد مجاز سعی کردید. 10 دقیقه دیگر تلاش کنید.')

            else:
                # the user has more opportunity
                regcode = str(random.randint(100000, 999999))
                if not UserphoneValid.objects.filter(MobileNumber=mobile_number).exists():
                    userphoneValid = UserphoneValid(
                        MobileNumber=mobile_number, ValidCode=regcode, Validation=False)
                    userphoneValid.save()
                try:
                    userphoneValid = UserphoneValid.objects.get(
                        MobileNumber=mobile_number)
                    userphoneValid.ValidCode = regcode
                    userphoneValid.Validation = False
                    userphoneValid.save()
                    url = 'https://api.kavenegar.com/v1/{}/verify/lookup.json'.format(KAVENEGAR_KEY)
                    params = {'receptor': mobile_number,
                                'token': regcode, 'template': 'nakhl-register'}
                    res = requests.post(url, params=params)
                    text = json.loads(res.text)
                    app_timezone = timezone.get_default_timezone()

                    SMS.objects.create(
                        return_status=text['return']['status'],
                        return_message=text['return']['message'],
                        entries_cost=text['entries'][0]['cost'],
                        entries_datetime=datetime.fromtimestamp(
                            text['entries'][0]['date']).astimezone(app_timezone),
                        entries_receptor=text['entries'][0]['receptor'],
                        entries_sender=text['entries'][0]['sender'],
                        entries_statustext=text['entries'][0]['statustext'],
                        entries_status=text['entries'][0]['status'],
                        entries_message=text['entries'][0]['message'],
                        entries_messageid=text['entries'][0]['messageid'],
                    )

                    if res.status_code == 200:  # TODO check more detail flow chart of kevenegar to be sure that the message is sent
                        # kevenegar post method is successful
                        request = set_mobile_number(request, mobile_number)
                        messages.success(request, 'کد تایید با موفقیت ارسال شد.')
                        return redirect(reverse('auth:forget-password-code'))
                    else:

                        messages.warning(request, 'سامانه پیامکی با مشکل مواجه شه است. لطفا با پشتیبانی تماس حاصل فرمایید.')

                except:
                    messages.warning(request, 'خطای دریافت شماره تماس')

        else:
            messages.warning(request, 'شماره موبایل {} در سایت ثبت نام نکرده است لطفا ابتدا ثبت نام کنید.'.format(mobile_number))
            return redirect(reverse('auth:register-mobile'))

def set_mobile_number(request, mobile_number):
    request.session['mobile_number'] = mobile_number
    return request

def get_mobile_number(request):
    return request.session['mobile_number'] or ''


class ApproveCode(TemplateView):
    template = 'registration/approveCode.html'
    context = {}
    success_redirect = None

    def get(self, request):
        mobile_number = get_mobile_number(request)
        self.context['mobileNumber'] = mobile_number
        return render(request, self.template, self.context)

    def post(self, request):
        mobile_number = get_mobile_number(request)
        code = request.POST.get("code", '')
        if UserphoneValid.objects.filter(MobileNumber=mobile_number, ValidCode=code).exists():
            # user enter the correct register code
            userphoneValid = UserphoneValid.objects.get(
                MobileNumber=mobile_number)
            userphoneValid.Validation = True
            userphoneValid.save()
            request = set_mobile_number(request, mobile_number)
            messages.success(request, 'کد وارد شده صحیح می باشد. لطفا اطلاعات مورد نظر را به دقت وارد فرمایید.')
            return redirect(reverse(self.success_redirect))
        else:
            messages.warning(request, 'کد وارد شده نا معتبر می باشد ')
            return render(request, self.template, self.context)


class RegisterCode(ApproveCode):
    context = {'header': 'ثبت نام در سایت'}
    success_redirect = 'auth:register-data'


class ForgetPasswordCode(ApproveCode):
    context = {'header': 'فراموشی رمز عبور'}
    success_redirect = 'auth:forget-password-data'


class RegisterData(TemplateView):
    """
    this function do all registration related tasks
    """

    def get(self, request):
        return render(request, 'registration/registerData.html')

    def post(self, request):
        # check mobile number of user
        # now he/she can change mobile number and it work!
        # the user can come to this page straightly and register without
        # confirming mobile number
        mobile_number = get_mobile_number(request)

        Email = request.POST.get("email", '')
        password = request.POST.get("password", '')
        newpassword = request.POST.get("newpassword", '')
        reference_code = request.POST.get("referencecode")
        # check password values
        if (password == '') or (newpassword == ''):
            messages.warning(request, 'لطفا تمامی فیلد ها را به درستی پر کنید!')
            return render(request, 'registration/registerData.html')

        else:
            if (password == newpassword):
                site_user = SiteUser(
                    mobile_number=mobile_number, password=password)

                if (User.objects.filter(username=mobile_number).exists()) or \
                        (Profile.objects.filter(MobileNumber=mobile_number).exists()):
                    messages.warning(request, 'کاربری با این مشخصات موجود است!')
                else:

                    try:
                        user = User.objects.create_user(
                            username=mobile_number, email=Email, password=password)
                        profile = Profile.objects.create(
                            FK_User=user,
                            MobileNumber=mobile_number,
                            IPAddress=visitor_ip_address(request),
                            ReferenceCode=reference_code
                        )
                        wallet = Wallet.objects.create(FK_User=user)
                        messages.success(request, 'ثبت نام با موفقیت انجام شد')
                        return redirect('auth:login')

                    except:
                        messages.warning(request, 'هنگام ثبت مشخصات خطایی رخ داده است. لطفا با پشتیبانی تماس حاصل فرمایید.')
            else:
                messages.warning(request, 'رمز عبور و تکرار رمز عبور برابر یکسان نیستند')
        return render(request, 'registration/registerData.html')


class ForgetPasswordData(TemplateView):
    template = 'registration/forget-password.html'

    def get(self, request):
        return render(request, self.template)

    def post(self, request):
        mobile_number = get_mobile_number(request)
        password = request.POST.get('password')
        new_password = request.POST.get('newpassword')
        if len(password) > 4:
            if (password == new_password):
                if Profile.objects.filter(MobileNumber=mobile_number).exists():
                    profile = Profile.objects.get(MobileNumber=mobile_number)
                    user = profile.FK_User
                    user.set_password(password)
                    user.save()
                    update_session_auth_hash(request, user)  # Important!
                    messages.success(request, 'رمز شما با موفقیت تغییر کرد.')
                    return redirect('auth:login')
                else:
                    # profile for this mobile number not exists()
                    messages.info(request, 'کاربری با این مشخصات ثبت نشده است. لطفا ابتدا ثبت نام فرمایید.')
                    return redirect('auth:register-mobile')
            else:
                messages.warning(request,'رمز و تایید رمز وارده شده یکسان نمی باشند.')
        else:
            messages.warning(request, 'رمز عبور باید حداقل 5 حرفی باشد.')
        return render(request, self.template)


class Login(TemplateView):
    """
    Display the login form and handle the login action.
    """
    template_name = 'registration/login.html'
    success_url = '/profile/dashboard/'

    def return_json(self, request):
        return request.path != '/account/login/'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        mobile_number = request.POST.get('mobilenumber', '')
        password = request.POST.get('password', '')
        remember_me = bool(request.POST.get('remember_me'))

        if mobile_number=='' or password=='':
            messages.warning(request, 'لطفا اطلاعات را به درستی وارد نمایید.')
            return render(request, self.template_name)

        if Profile.objects.filter(MobileNumber=mobile_number).exists():
            profile = Profile.objects.get(MobileNumber=mobile_number)
            user = profile.FK_User
            user = authenticate(username=user.username, password=password)
            if user is not None:
                # login user
                login(request, user)
                if remember_me:
                    session_key = request.session.session_key or Session.objects.get_new_session_key()
                    Session.objects.save(session_key, request.session._session, timezone.now(
                    ) + timedelta(seconds=SESSION_COOKIE_AGE))

                messages.success(request, 'شما با موفقیت وارد شدید.')
                if self.return_json(request):
                    response_data = {
                        'status': True,
                        'message': '200',
                    }
                    return JsonResponse(response_data)
                else:
                    return redirect(request.session.get('next') or self.success_url)

            else:
                # show a message with content: please enter correct username and password
                if self.return_json(request):
                    response_data = {
                        'status': True,
                        'message': '400',
                    }
                    return JsonResponse(response_data)
                else:
                    messages.warning(request, 'شماره موبایل با رمز وارد شده تطابق ندارد.')
                    return render(request, self.template_name)
        else:
            # Profile by this mobile number is not exists
            if self.return_json(request):
                response_data = {
                    'status': False,
                    'message': 'کاربری با این مشخصات ثبت نشده است. ابتدا ثبت نام کنید',
                }
                return JsonResponse(response_data)
            else:
                messages.warning(request, 'کاربری با این مشخصات ثبت نشده است. ابتدا ثبت نام کنید.')
                return redirect('auth:register-mobile')


def logout_(request):
    logout(request)
    messages.success(request, 'شما با موفقیت خارج شدید.')
    return redirect(reverse('Profile:index'))
