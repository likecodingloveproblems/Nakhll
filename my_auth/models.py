from django.db import models
from django_jalali.db import models as jmodels

# UserphoneValid (فعالسازی شماره) Model   
class UserphoneValid(models.Model):
    MobileNumber=models.CharField(verbose_name='شماره موبایل', max_length=11, unique=True)
    ValidCode=models.CharField(verbose_name='کد فعال سازی', max_length=8, blank=True,default='80')
    Validation=models.BooleanField(verbose_name='تایید شماره تماس', default=False)
    Date=jmodels.jDateField(verbose_name='تاریخ', null=True, auto_now=True)
    
    def __str__(self):
       return "{}".format(self.MobileNumber)

    class Meta:
        ordering = ('Date',)   
        verbose_name = "فعالسازی شماره"
        verbose_name_plural = "فعالسازی شماره"

#----------------------------------------------------------------------------------------------------------------------------------

# Profile (پروفایل) Model
# class Profile(models.Model):
#     ID=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
#     FK_User=models.OneToOneField(User, on_delete=models.SET_NULL, verbose_name='کاربر', related_name='User_Profile', null=True)
#     SEX_STATUS =(
#         ('0','انتخاب جنسیت'),
#         ('1','زن'),
#         ('2','مرد'),
#         ('3','سایر'),
#     )
#     Sex=models.CharField(verbose_name='جنسیت', max_length=1, choices=SEX_STATUS, default='0')
#     CountrPreCode=models.CharField(verbose_name='کد کشور', max_length=6, default='098')
#     MobileNumber=models.CharField(verbose_name='شماره موبایل', max_length=11, unique=True)
#     ZipCode=models.CharField(verbose_name='کد پستی', max_length=10, blank=True)
#     NationalCode=models.CharField(verbose_name='کد ملی', max_length=10, unique=True, blank=True, null=True)
#     Address=models.TextField(verbose_name='آدرس', blank=True)
#     State =models.CharField(verbose_name='استان', max_length=50, blank=True)
#     BigCity=models.CharField(verbose_name='شهرستان', max_length=50, blank=True)
#     City=models.CharField(verbose_name='شهر', max_length=50, blank=True)
#     Location=models.CharField(verbose_name='موقعیت مکانی', max_length=150, blank=True, help_text='طول و عرض جغرافیایی')
#     BrithDay=jmodels.jDateField(verbose_name='تاریخ تولد', null=True, auto_now_add=True)
#     FaxNumber=models.CharField(verbose_name='شماره فکس', max_length=8, blank=True)
#     CityPerCode=models.CharField(verbose_name='پیش شماره', max_length=6, blank=True, default='034')
#     PhoneNumber=models.CharField(verbose_name='شماره تلفن ثابت', max_length=8, blank=True)
#     Bio=models.CharField(verbose_name='درباره من', max_length=250, blank=True)
#     Image=models.ImageField(verbose_name='پروفایل', upload_to=PathAndRename('media/Pictures/Profile/'), null=True, default='static/Pictures/DefaultProfile.png')
#     Image_thumbnail = ImageSpecField(source='Image',
#                                 processors=[ResizeToFill(175, 175)],
#                                 format='JPEG',
#                                 options={'quality': 60} )
#     UserReferenceCode=models.CharField(verbose_name='کد شما', max_length=6, unique=True, default=BuildReferenceCode(6))
#     Point=models.PositiveIntegerField(verbose_name='امتیاز کاربر', default=0)
#     TUTORIALWEB_TYPE =(
#         ('0','موتور های جستجو'),
#         ('1','حجره داران'),
#         ('2','شبکه های اجتماعی'),
#         ('3','کاربران'),
#         ('4','رسانه ها'),
#         ('5','تبلیغات'),
#         ('6','NOD'),
#         ('7','سایر'),
#         ('8','هیچ کدام'),
#     )
#     TutorialWebsite=models.CharField(verbose_name='نحوه آشنایی با سایت', max_length=1, choices=TUTORIALWEB_TYPE, blank=True, default='8')
#     ReferenceCode=models.CharField(verbose_name='کد معرف', max_length=6, blank=True)
#     IPAddress=models.CharField(verbose_name='آدرس ای پی', max_length=15, blank=True)

#     # Output Customization Based On UserName (ID)
#     def __str__(self):
#        return "{} ({})".format(self.FK_User, self.ID)

#     def Image_thumbnail_url(self):
#         try:
#             i = self.Image_thumbnail.url
#             url = self.Image_thumbnail.url
#             return url
#         except:
#             url = "https://nakhll.com/media/Pictures/avatar.png"
#             return url

#     # Get User Bank Account Info
#     def get_bank_account_name(self):
#         if BankAccount.objects.filter(FK_Profile = self).exists():
#             return BankAccount.objects.get(FK_Profile = self).AccountOwner
#         else:
#             return None

#     def get_credit_card_number(self):
#         if BankAccount.objects.filter(FK_Profile = self).exists():
#             return BankAccount.objects.get(FK_Profile = self).CreditCardNumber
#         else:
#             return None


#     def get_shaba_number(self):
#         if BankAccount.objects.filter(FK_Profile = self).exists():
#             return BankAccount.objects.get(FK_Profile = self).ShabaBankNumber
#         else:
#             return None

#     def chack_user_bank_account(self):
#         if (self.get_bank_account_name() == None) or (self.get_credit_card_number() == None) or (self.get_shaba_number() == None):
#             return True
#         else:
#             return False


#     def is_user_shoper(self):
#         if Shop.objects.filter(FK_ShopManager = self.FK_User).exists():
#             return True
#         else:
#             return False

    
#     def get_user_shops(self):
#         return Shop.objects.filter(FK_ShopManager = self.FK_User, Publish = True)


#     def get_user_products(self):
#         return Product.objects.filter(FK_Shop__in = self.get_user_shops(), Publish = True)


#     # Ordering With DateCreate
#     class Meta:
#         ordering = ('ID',)   
#         verbose_name = "پروفایل"
#         verbose_name_plural = "پروفایل ها "

#----------------------------------------------------------------------------------------------------------------------------------
