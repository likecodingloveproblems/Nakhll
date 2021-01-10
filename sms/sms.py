from abc import ABC, abstractclassmethod, abstractmethod, abstractproperty

from jdatetime import datetime, timedelta
import logging

import requests
from nakhll.settings import KAVENEGAR_KEY
import random

from django.db.models.query_utils import Q
from nakhll_market.models import Profile, UserphoneValid

from django.utils import timezone
from django.utils.timezone import make_aware
from sms.models import SMS as SMSModel
import json
from kavenegar import KavenegarAPI, APIException, HTTPException

logger = logging.getLogger(__name__)

class SMS(ABC):
    '''
    this class handle actions about sending sms
    '''
    def send(self, request, mobile_number, **kwargs) -> str:
        '''
        this method handle all action actions about checking the restrictions
        and then send SMS and log the results
        '''
        # get user ip from request
        ip = self._get_client_ip(request)
        # confirm sending SMS
        block_message = self._confirm_allowed(mobile_number, ip)
        if not block_message:
            # send code
            res = self._send(mobile_number, **kwargs)
            # log it
            self._log(res, ip)
            return ''
        else:
            return block_message

    @abstractclassmethod
    def _send(self, mobile_number, **kwargs):
        '''
        this method handle actions about sending SMS
        '''

    @abstractmethod
    def _log(self, res, ip):
        '''
        this method log sent sms in database
        '''

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
        


class Kavenegar(SMS):

    def __init__(self) -> None:
        self.api = KavenegarAPI(KAVENEGAR_KEY)
    
    def _send(self, mobile_number, **kwargs):
        kwargs['receptor'] = mobile_number
        return self._verify_send(**kwargs)

    def _sms_send(self, **kwargs):
        try:
            response = self.api.sms_send(kwargs)
            return response
        except APIException as e: 
            return e
        except HTTPException as e:
            return e

    def _verify_send(self, **kwargs):
        try:
            response = self.api.verify_lookup(kwargs)
            return response
        except APIException as e: 
            return e
        except HTTPException as e:
            return e

    def _log(self, res, ip):
        if isinstance(res, Exception):
            return logger.error(res)
        if isinstance(res, list):
            res = res[0]
        app_timezone = timezone.get_default_timezone()
        return SMSModel.objects.create(
            cost=res['cost'],
            datetime=datetime.fromtimestamp(
                res['date']).astimezone(app_timezone),
            receptor=res['receptor'],
            sender=res['sender'],
            statustext=res['statustext'],
            status=res['status'],
            message=res['message'],
            messageid=res['messageid'],
            user_ip = ip,
        )

    def generate_code(self, mobile_number):
        yesterday = make_aware(datetime.today() - timedelta(days=1))
        user_phone_valid = UserphoneValid.objects.filter(MobileNumber = mobile_number, Date__gte=yesterday, Validation=False)
        if user_phone_valid.exists():
            return user_phone_valid[0].ValidCode
        else:
            return str(random.randint(100000, 999999))

    def _get_try_count(self,mobile_number, ip, deltatime):
        return SMSModel.objects.filter(
            (Q(receptor=mobile_number) | Q(user_ip=ip)) 
            ,datetime__gte=deltatime
            ).count()

    def _confirm_allowed(self, mobile_number, ip):
        '''
        this method check this user is allowed to receive SMS 
        now the only policy is checking maximux allowed number of sms

        return :
            confirm -> True
            not confirm -> False
        '''
        MAX_NUMBER_SMS_IN_10_MIN = 5
        MAX_NUMBER_SMS_IN_A_DAY = 10
        # check that user is not overloading SMS with many requests
        ten_minutes_ago = timezone.now() + timedelta(minutes=-10)
        one_day_ago = timezone.now() + timedelta(hours=-24)
        count_10min = self._get_try_count(mobile_number, ip, ten_minutes_ago)
        count_day = self._get_try_count(mobile_number, ip, one_day_ago)
        if count_day < MAX_NUMBER_SMS_IN_A_DAY:
            if count_10min < MAX_NUMBER_SMS_IN_10_MIN:
                return None
            else:
                return 'شما بیشتر از تعداد مجاز درخواست کردید. لطفا 10 دقیقه دیگر امتحان کنید.'

        else: 
            return 'شما بیشتر از تعداد مجاز درخواست کردید. لطفا فردا دوباره امتحان کنید.'
