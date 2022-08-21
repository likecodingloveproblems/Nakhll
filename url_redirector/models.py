from uuid import uuid4
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User


class Url(models.Model):
    """URL Redirector

    Create a fixed URL in the database and redirect any dynamic URL to it.
    Attributes:
        destination_url: The destination URL which can be changed by the user at any time.
        description: A description of the URL. Use this to describe the purpose of the URL.
        url_code: A unique code for the URL. The fixed URL is https://nakhll.com/goto/<url_code>.
        creator: The user who created the URL.
        created_at: The date and time when the URL was created.
        updated_at: The date and time when the URL was last updated.
    """
    class Meta:
        verbose_name = _('آدرس')
        verbose_name_plural = _('آدرس‌ها')
    destination_url = models.URLField(verbose_name=_('آدرس مقصد'), default='https://nakhll.com/')
    description = models.TextField(verbose_name=_('توضیحات'), blank=True)
    url_code = models.UUIDField(verbose_name=_('کد آدرس'), unique=True, default=uuid4)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('ایجاد کننده'), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاریخ ایجاد'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاریخ ویرایش'))

    def __str__(self):
        return f'{self.url_code} --> {self.destination_url}'

    def get_new_address(self):
        """Get the new URL address of this record."""
        return f'https://nakhll.com/goto/{self.url_code}'
    get_new_address.short_description = _('آدرس جدید')
    get_new_address.admin_order_field = 'url_code'
