from sms.services import count_sms, create_sms
from Payment.services import get_wallet_by_mobile_number
from logging import error
from my_auth.services import create_user, get_mobile_number_auth_code, get_user_by_mobile_number, get_user_by_username
from django.core.checks import messages
from django.http import request, response
from django.urls.base import reverse
from my_auth.views import Login, get_mobile_number
from django.test import TestCase, RequestFactory, Client
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.messages import get_messages
from django.utils import timezone

from datetime import datetime, timedelta

from nakhll_market.models import Profile, UserPoint

from Payment.models import Wallet
from my_auth.forms import error_messages
from sms.models import SMS

# Create your tests here.
def get_form_errors(response):
    if response.context_data['form'].errors != {}:
        return response.context_data['form'].errors['__all__']

class Authentication(TestCase):

    def setUp(self):
        self.client = Client()
        self.mobile_number = '09135833920'
        self.password = '12345'
        self.user, self.profile, self.wallet = create_user(
            RequestFactory().get('/'), 
            mobile_number='09135833920',
            email='',
            password='12345',
            reference_code='',
            )
        self.login_url = reverse('auth:login')
        self.forget_password_mobile_url = reverse('auth:forget-password-mobile')
        self.forget_password_code_url = reverse('auth:forget-password-code')
        self.forget_password_data_url = reverse('auth:forget-password-data')
        self.register_mobile_url = reverse('auth:register-mobile')
        self.register_code_url = reverse('auth:register-code')
        self.register_data_url = reverse('auth:register-data')



    def test_get_login_url(self):
        response = self.client.get(self.login_url)
        # request.user = AnonymousUser()
        # response = Login.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_anonymous_correct_user_login(self):
        data = {
            'mobile_number':'09135833920',
            'password':'12345',
            'remember_me':"",
        }
        response = self.client.post(
            self.login_url, 
            data,
        )
        self.assertEqual(
            get_user_by_mobile_number(data['mobile_number']),
            get_user_by_username(data['mobile_number'])
            )
        # check user is logged in 
        self.assertEqual(
            response.wsgi_request.user, 
            get_user_by_mobile_number(data['mobile_number']))

    def test_not_registered_login(self):
        data = {
            'mobile_number':'09133422469',
            'password':'12345',
            'remember_me':''
        }
        response = self.client.post(self.login_url, data)
        user = AnonymousUser()
        self.assertEqual(response.wsgi_request.user, user)
        # check the form validation error it returns
        non_field_errors = get_form_errors(response)
        self.assertEqual(len(non_field_errors), 1)
        self.assertEqual(non_field_errors[0], error_messages['not_registered'])

    def test_wrong_password_login(self):
        data = {
            'mobile_number':'09135833920',
            'password':'asdifjkmlavsodi12345',
            'rememeber_me':'False',
        }
        response = self.client.post(self.login_url, data)
        errors = get_form_errors(response)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0], error_messages['invalid_login'])

    def test_correct_forget_password(self):
        data = {
            'mobile_number':'09135833920'
        }
        # get mobile number
        response = self.client.post(self.forget_password_mobile_url, data, follow=True)
        errors = get_form_errors(response)
        self.assertEqual(errors, None)
        self.assertEqual(count_sms(), 1)
        self.assertEqual(response.redirect_chain, [(reverse('auth:forget-password-code'), 302)])
        self.assertEqual(response.wsgi_request.session.get('mobile_number'), data['mobile_number'])
        # get authentication code
        code = get_mobile_number_auth_code(data['mobile_number'])
        response = self.client.post(
            self.forget_password_code_url, 
            {'code':code, 'mobile_number':data['mobile_number']}, 
            follow=True
            )
        self.assertEqual(response.redirect_chain, [(reverse('auth:forget-password-data'), 302)])
        self.assertEqual(response.wsgi_request.session.get('mobile_number'), data['mobile_number'])
        # set new password
        response = self.client.post(
            self.forget_password_data_url, 
            {'password':'mam123', 'confirm_password':'mam123'},
            follow=True,
            )
        self.assertEqual(response.redirect_chain, [(reverse('auth:login'), 302)])
        self.assertEqual(response.wsgi_request.session.get('mobile_number'), data['mobile_number'])
        # now login by new password
        response = self.client.post(
            self.login_url,
            {'mobile_number':'09135833920', 'password':'mam123','remember_me':'True'},
            follow=True,
        )
        assert not response.redirect_chain[0][0].startswith('/account/')
        self.assertEqual(response.wsgi_request.user, self.user)

    def test_not_registered_forget_password_mobile(self):
        data = {
            'mobile_number':'09137146466'
        }
        response = self.client.post(self.forget_password_mobile_url, data, follow=True)
        errors = get_form_errors(response)
        self.assertEqual(errors, [error_messages['not_registered']])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [])
        self.assertEqual(response.wsgi_request.session.get('mobile_number'), None)

    # this method is very costy
    def _test_exceed_sms_limit(self):
        data = {
            'mobile_number':'09135833920',
        }
        response = self.client.post(self.forget_password_mobile_url, data, follow=True)
        self.assertEqual(count_sms(), 1)
        self.assertEqual(response.redirect_chain, [(reverse('auth:forget-password-code'), 302)])
        response = self.client.post(self.forget_password_mobile_url, data, follow=True)
        self.assertEqual(count_sms(), 2)
        self.assertEqual(response.redirect_chain, [(reverse('auth:forget-password-code'), 302)])
        response = self.client.post(self.forget_password_mobile_url, data, follow=True)
        self.assertEqual(count_sms(), 3)
        self.assertEqual(response.redirect_chain, [(reverse('auth:forget-password-code'), 302)])
        response = self.client.post(self.forget_password_mobile_url, data, follow=True)
        self.assertEqual(count_sms(), 4)
        self.assertEqual(response.redirect_chain, [(reverse('auth:forget-password-code'), 302)])
        response = self.client.post(self.forget_password_mobile_url, data, follow=True)
        self.assertEqual(count_sms(), 5)
        self.assertEqual(response.redirect_chain, [(reverse('auth:forget-password-code'), 302)])
        response = self.client.post(self.forget_password_mobile_url, data, follow=True)
        self.assertEqual(count_sms(), 5)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'شما بیشتر از تعداد مجاز درخواست کردید. لطفا 10 دقیقه دیگر امتحان کنید.')

    def test_exceed_sms_limit(self):
        app_timezone = timezone.get_default_timezone()
        ip = '127.0.0.1'
        data = {
            'mobile_number':'09135833920',
        }
        res = {
            'messageid':522553876,
            'message':'بازار آنلاین نخل\nکد شما : 381458\nبا تشکر از اعتماد شما',
            'status':5,
            'statustext':'ارسال به مخابرات',
            'sender':'10007119',
            'receptor':'09135833920',
            'date':datetime.now().astimezone(app_timezone),
            'cost':166,
        }
        for _ in range(5):
            create_sms(
                            cost=res['cost'],
                datetime=datetime.now().astimezone(app_timezone),
                receptor=res['receptor'],
                sender=res['sender'],
                statustext=res['statustext'],
                status=res['status'],
                message=res['message'],
                messageid=res['messageid'],
                user_ip = ip,
            )
        
        self.assertEqual(count_sms(), 5)
        response = self.client.post(self.forget_password_mobile_url, data, follow=True)
        self.assertEqual(response.redirect_chain, [(self.forget_password_mobile_url, 302)])
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'شما بیشتر از تعداد مجاز درخواست کردید. لطفا 10 دقیقه دیگر امتحان کنید.')
    
    def test_register_successfully(self):
        mobile_number = '09137146466'
        # get mobile number of the user to validate
        response = self.client.post(
            self.register_mobile_url, 
            {'mobile_number':mobile_number}, 
            follow=True,
        )
        self.assertEqual(response.redirect_chain, [(self.register_code_url,302)])
        self.assertEqual(response.wsgi_request.session.get('mobile_number'), mobile_number)
        code = get_mobile_number_auth_code(mobile_number)
        # validate mobile number by auth code
        response = self.client.post(
            self.register_code_url,
            {'code':code, 'mobile_number':mobile_number},
            follow=True,
        )
        self.assertEqual(response.redirect_chain, [(self.register_data_url, 302)])
        self.assertEqual(response.wsgi_request.session.get('mobile_number'), mobile_number)
        # set registration data
        response = self.client.post(
            self.register_data_url,
            {
                'password':'mam12345',
                'confirm_password':'mam12345',
                'email':'am.civil90@yahoo.com',
                'reference_code':'12345'
            },
        follow=True,
        )
        self.assertEqual(response.redirect_chain, [(self.login_url, 302)])
        # check user has created
        profile_user = get_user_by_mobile_number(mobile_number)
        user = get_user_by_username(mobile_number)
        self.assertEqual(profile_user, user)
        self.assertNotEqual(get_wallet_by_mobile_number(mobile_number), None)

        # login
        response = self.client.post(
            self.login_url,
            {
                'password':'mam12345',
                'mobile_number':'09137146466',
                'remember_me':True,
            },
            follow=True,
        )
        self.assertEqual(response.wsgi_request.user, user)
        assert not response.redirect_chain[0][0].startswith('/account/')
