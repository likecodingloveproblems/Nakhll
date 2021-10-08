from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from nakhll_market.models import Shop, Product, Profile
from django_jalali.db import models as jmodels
import uuid, random, string, os
from django.utils.deconstruct import deconstructible
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill


# Rename Method
@deconstructible
class PathAndRename():
    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        rand_strings = ''.join( random.choice(string.ascii_letters+string.digits) for i in range(6))
        filename = '{}.{}'.format(rand_strings, ext)

        return os.path.join(self.path, filename)

#----------------------------------------------------------------------------------------------------------------------------------

# Ticketing (پشتیبانی) Model
class Ticketing(models.Model):
    ID=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    Title=models.CharField(verbose_name='عنوان', max_length=100, db_index=True)
    Description=models.TextField(verbose_name='توضیحات', blank=True, null=True)
    Image=models.ImageField(verbose_name='عکس تیکت', upload_to=PathAndRename('media/Pictures/Ticketing/'), help_text='عکس مربوط به تیکت خود را اینجا بارگذاری کنید', null=True, blank=True)
    SECTION_TYPE =(
        ('0','پشتیبانی'),
        ('1','مالی'),
        ('2','فنی'),
    )
    SectionType=models.CharField(verbose_name='بخش', max_length=1, choices=SECTION_TYPE, default='0')
    FK_User=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='کاربر مدنظر', related_name='User_Ticketing', blank=True, null=True)
    FK_Product=models.ForeignKey(Product, on_delete=models.SET_NULL, verbose_name='محصول مدنظر', related_name='Product_Ticketing', blank=True, null=True)
    FK_Shop=models.ForeignKey(Shop, on_delete=models.SET_NULL, verbose_name='حجره مدنظر', related_name='Shop_Ticketing', blank=True, null=True)
    FK_Importer=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='کاربر', related_name='Importer_Ticketing', null=True)
    FK_Responder=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='پاسخ دهنده', related_name='Responder_Ticketing', null=True, blank=True)
    Date=models.DateTimeField(verbose_name='تاریخ ثبت', auto_now_add=True)
    SEEN_STATUS =(
        ('0','خوانده نشده'),
        ('1','در حال بررسی'),
        ('2','بررسی شده'),
        ('3','بسته شده'),
    )
    SeenStatus=models.CharField(verbose_name='وضعیت', max_length=1, choices=SEEN_STATUS, default='0')

    def get_importer_profile(self):
        return Profile.objects.get(FK_User = self.FK_Importer).Image_thumbnail_url()

    # Output Customization Based On Title
    def __str__(self):
        return "{}".format(self.Title)

    # Ordering With DateCreate
    class Meta:
        ordering = ('ID',)
        verbose_name = "تیکت"
        verbose_name_plural = "تیکت ها" 
        
#----------------------------------------------------------------------------------------------------------------------------------

# Message (پیام) Model
class TicketingMessage(models.Model):
    ID=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    FK_Importer=models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='کاربر', related_name='Importer_Message', null=True)
    Description=models.TextField(verbose_name='توضیحات')
    Date=models.DateTimeField(verbose_name='تاریخ ثبت', auto_now_add=True)
    FK_Replay=models.ForeignKey(Ticketing, verbose_name='پاسخ', related_name='Ticketing_Message', on_delete=models.CASCADE, null=True)

    # Output Customization Based On User
    def __str__(self):
        return "{}".format(self.FK_Importer)

    # Ordering With DateCreate
    class Meta:
        ordering = ('ID',)
        verbose_name = "پیام"
        verbose_name_plural = "پیام ها"

#----------------------------------------------------------------------------------------------------------------------------------

# Complaint (شکایت) Model
class Complaint(models.Model):
    Title=models.CharField(verbose_name='عنوان', max_length=100)
    Description=models.TextField(verbose_name='توضیحات')
    MobileNumber=models.CharField(verbose_name='شماره موبایل', max_length=11, blank=True)
    Email=models.EmailField(verbose_name='ایمیل', blank=True)
    TYPE_STATUS =(
        ('0','شکایت'),
        ('1','انتقادات و پیشنهادات'),
        ('2','تماس با مدیریت'),
    )
    Type=models.CharField(verbose_name='نوع', max_length=1, choices=TYPE_STATUS, default='0')
    Image=models.ImageField(verbose_name='عکس', upload_to=PathAndRename('media/Pictures/Complaint/'), blank = True, null = True)
    Image_medium = ImageSpecField(source='Image',
                                      processors=[ResizeToFill(450, 450)],
                                      format='JPEG',
                                      options={'quality': 60} )

    # Output Customization Based On User
    def __str__(self):
        return "{}".format(self.Title)

    def Image_thumbnail_url(self):
        try:
            i = self.Image_medium.url
            url = self.Image_medium.url
            return url
        except:
            url ="https://nakhll.com/media/Pictures/default.jpg"
            return url

    # Ordering With DateCreate
    class Meta:
        ordering = ('id',)
        verbose_name = "شکایت"
        verbose_name_plural = "شکایت ها"

#----------------------------------------------------------------------------------------------------------------------------------
