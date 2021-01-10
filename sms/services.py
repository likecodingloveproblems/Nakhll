from sms.models import SMS, SMSRequest

# only for test purposes
def count_sms():
    return SMS.objects.all().count()

def create_sms(**kwargs):
    SMS.objects.create(**kwargs)