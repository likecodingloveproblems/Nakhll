from datetime import datetime, timedelta
import logging

import requests
from nakhll.settings import KAVENEGAR_KEY
import random

from django.db.models.query_utils import Q
from nakhll_market.models import Profile

from django.utils import timezone
from sms.models import SMS as SMSModel
import json
from kavenegar import KavenegarAPI, APIException, HTTPException

logger = logging.getLogger(__name__)

class SMS:
    '''
    this class handle actions about sending sms
    '''

    def send(self, request, mobile_number, **kwargs) -> bool:
        '''
        this method handle all action actions about checking the restrictions
        and then send SMS and log the results
        '''
        # get user ip from request
        ip = self._get_client_ip(request)
        # confirm sending SMS
        self._confirm_allowed(mobile_number, ip)
        # send code
        res = self._send(mobile_number, **kwargs)
        # log it
        self._log(res)

    def _send(self, mobile_number, **kwargs):
        '''
        this method handle actions about sending SMS
        '''

    def _log(self, res):
        '''
        this method log sent sms in database
        '''

    def _get_try_count(self,mobile_number, ip, deltatime):
        return SMSModel.objects.filter(
            (Q(receptor=mobile_number) or Q(user_ip=ip)) 
            and Q(datetime__gte=deltatime)
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
        if count_day < MAX_NUMBER_SMS_IN_A_DAY and\
            count_10min < MAX_NUMBER_SMS_IN_10_MIN:
            return True
        else: 
            return False

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

    def _log(self, res):
        if isinstance(res, Exception):
            return logger.error(res)
        if isinstance(res, list):
            res = res[0]
        app_timezone = timezone.get_default_timezone()
        try:
            return SMSModel.objects.create(
                return_status=res['status'],
                return_message=res['message'],
                entries_cost=res['cost'],
                entries_datetime=datetime.fromtimestamp(
                    res['date']).astimezone(app_timezone),
                entries_receptor=res['receptor'],
                entries_sender=res['sender'],
                entries_statustext=res['statustext'],
                entries_status=res['status'],
                entries_message=res['message'],
                entries_messageid=res['messageid'],
                user_ip = self.ip,
            )
        except:
            return None

    def generate_code(self):
        return str(random.randint(100000, 999999))

