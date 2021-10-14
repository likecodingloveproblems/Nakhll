from my_auth.services import get_user_by_mobile_number
from Payment.models import Wallet
from nakhll.services import get_or_none

def get_wallet_by_user(user):
    return get_or_none(Wallet, FK_User=user)

def get_wallet_by_mobile_number(mobile_number):
    user = get_user_by_mobile_number(mobile_number)
    return get_or_none(Wallet, FK_User=user)