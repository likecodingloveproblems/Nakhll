from django.db import models

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
