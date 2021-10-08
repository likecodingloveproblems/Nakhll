from typing import TYPE_CHECKING
from django.db import models
from django.db.models.fields import DateTimeField
from django.utils.translation import gettext, gettext_lazy as _

# Create your models here.
class SMS(models.Model):
    cost = models.IntegerField("مبلغ")
    datetime = models.DateTimeField(auto_now=False, auto_now_add=False)
    receptor = models.CharField(max_length=50)
    sender = models.CharField(max_length=50)
    statustext = models.CharField(max_length=50)
    status = models.IntegerField()
    message = models.CharField(max_length=255)
    messageid = models.IntegerField()
    datetime = models.DateTimeField(auto_now=True, auto_now_add=False)
    user_ip = models.GenericIPAddressField()

    class Meta:
        ordering = ('-datetime',)   
        verbose_name = "پیامک"
        verbose_name_plural = "پیامک ها"


class SMSRequest(models.Model):
    mobile_number = models.CharField(_(""), max_length=15)
    client_ip = models.GenericIPAddressField(_(""), protocol="both", unpack_ipv4=False)
    template = models.CharField(_(""), max_length=50)
    token = models.CharField(_(""), max_length=10)
    TYPE_CHOICE = (
        ('sms', 'sms'),
        ('sms', 'call'),
    )
    type = models.CharField(_(""), choices=TYPE_CHOICE, default='sms', max_length=4)
    block_message = models.CharField(_(""), max_length=127, null=True, blank=True)
    datetime = models.DateTimeField(auto_now_add=True)