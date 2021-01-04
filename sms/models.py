from django.db import models

# Create your models here.
class SMS(models.Model):
    return_status = models.IntegerField()
    return_message = models.CharField('پیام درخواست', max_length=50)
    entries_cost = models.IntegerField("مبلغ")
    entries_datetime = models.DateTimeField(auto_now=False, auto_now_add=False)
    entries_receptor = models.CharField(max_length=50)
    entries_sender = models.CharField(max_length=50)
    entries_statustext = models.CharField(max_length=50)
    entries_status = models.IntegerField()
    entries_message = models.CharField(max_length=255)
    entries_messageid = models.IntegerField()
    datetime = models.DateTimeField(auto_now=True, auto_now_add=False)
    user_ip = models.GenericIPAddressField()

    class Meta:
        ordering = ('-entries_datetime',)   
        verbose_name = "پیامک"
        verbose_name_plural = "پیامک ها"
