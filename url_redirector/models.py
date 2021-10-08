from uuid import uuid4
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

# Create your models here.

class Url(models.Model):
    class Meta:
        verbose_name = _('آدرس')
        verbose_name_plural = _('آدرس‌ها')
    destination_url = models.URLField(verbose_name=_('آدرس مقصد'), default='https://nakhll.com/')
    description = models.TextField(verbose_name=_('توضیحات'), blank=True)
    url_code = models.UUIDField(verbose_name=_('کد آدرس'), unique=True, default=uuid4)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('ایجاد کننده'), null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاریخ ایجاد'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاریخ ویرایش'))

