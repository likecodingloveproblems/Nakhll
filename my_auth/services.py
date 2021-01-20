from nakhll.services import get_client_ip, get_or_none
from typing import Any
from django.contrib.sessions.models import Session
from Payment.models import Wallet
from django.contrib.auth.models import User
from nakhll_market.models import Profile
from my_auth.models import UserphoneValid

### mobile number validation
def validate_mobile_number(mobile_number, code) -> bool:
    if UserphoneValid.objects.filter(MobileNumber=mobile_number, ValidCode=code).exists():
        # user enter the correct register code
        user_phone_valid = UserphoneValid.objects.get(
            MobileNumber=mobile_number)
        user_phone_valid.Validation = True
        user_phone_valid.save()
        return True
    else:
        return False

def mobile_number_is_validated(mobile_number) -> bool:
    if UserphoneValid.objects.filter(MobileNumber=mobile_number).exists():
        # user enter the correct register code
        return UserphoneValid.objects.get(
            MobileNumber=mobile_number).Validation
    else:
        return False

def get_mobile_number_auth_code(mobile_number):
    return UserphoneValid.objects.get(MobileNumber=mobile_number).ValidCode

def set_mobile_number_auth_code(mobile_number, code, validation=False) -> UserphoneValid:
    '''
    this method create or update auth code
    '''
    return UserphoneValid.objects.update_or_create(
        MobileNumber=mobile_number, 
        defaults={'ValidCode':code, 'Validation':validation}
        )[0]

### user and profile processes
def get_user_by_mobile_number(mobile_number):
    profile = get_or_none(Profile, MobileNumber=mobile_number)
    if profile:
        return profile.FK_User
    else:
        return None
    
def get_user_by_username(username):
    return get_or_none(User, username=username)

def user_exists_by_mobile_number(mobile_number: str) -> bool:
    if get_user_by_mobile_number(mobile_number) or \
        get_user_by_username(mobile_number):
        return True
    else:
        return False

def create_user(request, mobile_number, email, password, reference_code):
    '''
    this function create user and all related objects
    it must be transactional because we create 3 objects 
    or we don't need none of them.
    TODO MAKE IT TRANSACTIONAL
    '''
    try:
        ip = get_client_ip(request)
        user = User.objects.create_user(username=mobile_number, email=email, password=password)
        profile = Profile.objects.create(
            FK_User=user,
            MobileNumber=mobile_number,
            IPAddress=ip,
            ReferenceCode=reference_code
        )
        # TODO it must be done by a function in Payment app
        wallet = Wallet.objects.create(FK_User=user)
        return user, profile, wallet
    except Exception as e:
        print(e)
        return None, None, None

def set_user_password_by_mobile_number(mobile_number, password) -> User:
    user = get_user_by_mobile_number(mobile_number)
    if user:
        user.set_password(password)
        user.save()
        return user
    else:
        return None

def set_session_expiration_time(request, expiration_time) -> Any:
    session_key = request.session.session_key or Session.objects.get_new_session_key()
    Session.objects.save(session_key, request.session._session, expiration_time)
