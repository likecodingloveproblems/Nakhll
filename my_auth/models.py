from django.db.models import query
from typing import Optional, Tuple, Union
from django.db import models
from django.db.models.base import Model
from django_jalali.db import models as jmodels
from django.contrib.auth.models import User
import uuid


class UserphoneValidQuerySet(models.QuerySet):
    '''
    this implement the data access object for UserphoneValid table
    '''
    def get_valid_code(self, mobile_number: str) -> str:
        """This method get mobile_number from user and return validation code

        Returns:
            user phone valid {UserphoneValid}: user phone valid record by mobile number
        """
        return self.get(MobileNumber=mobile_number).ValidCode
    
    def validate_mobile_number(self, mobile_number: str, code:str) -> Optional['UserphoneValid']:
        """this function validate phone number, auth code

        Returns:
            [type]: [description]
        """        
        return self.get(MobileNumber=mobile_number, ValidCode=code, Validation=False).update(Validation=True)

    def set_code(self, mobile_number:str, code:str) -> Optional['UserphoneValid']:
        """Set auth code to user

        Args:
            mobile_number (str): mobile number of user
            code (str): authentication code sent to user for verification

        Returns:
            Tuple[Model, bool]: create user phone valid record or update it
        """
        return self.update_or_create(
            MobileNumber=mobile_number, 
            defaults={'ValidCode':code, 'Validation':False}
            )[0]

    def is_validated(self, mobile_number: str) -> bool:
        return self.filter(MobileNumber=mobile_number, Validation=True).exists()


class UserphoneValidManager(models.Manager):
    def get_queryset(self):
        return UserphoneValidQuerySet(
            model=self.model,
            using=self._db,
            hints=self._hints
        )



# UserphoneValid (فعالسازی شماره) Model   
class UserphoneValid(models.Model):
    MobileNumber=models.CharField(verbose_name='شماره موبایل', max_length=11, unique=True)
    ValidCode=models.CharField(verbose_name='کد فعال سازی', max_length=8, blank=True,default='80')
    Validation=models.BooleanField(verbose_name='تایید شماره تماس', default=False)
    Date=jmodels.jDateField(verbose_name='تاریخ', null=True, auto_now=True)
    
    objects = UserphoneValidManager()

    def __str__(self):
       return "{}".format(self.MobileNumber)

    class Meta:
        ordering = ('Date',)   
        verbose_name = "فعالسازی شماره"
        verbose_name_plural = "فعالسازی شماره"

#----------------------------------------------------------------------------------------------------------------------------------

class ProfileManager(models.Manager):


    def get_user_by_mobile_number(self, mobile_number: str) -> User:
        queryset = self.get_queryset()
        return queryset.get(MobileNumber=mobile_number).FK_User
        
    def user_exists_by_mobile_number(self, mobile_number: str) -> bool:
        if self.get_user_by_mobile_number(mobile_number):
            return True
        else:
            return False

    def set_user_password_by_mobile_number(self, mobile_number, password) -> User:
        user = self.get_user_by_mobile_number(mobile_number)
        user.set_password(password)
        user.save()
        return user

    def create_profile(self, mobile_number, user, reference_code, user_ip):
        '''
        this function create user and all related objects
        it must be transactional because we create 3 objects 
        or we don't need none of them.
        TODO MAKE IT TRANSACTIONAL
        '''
        queryset = self.get_queryset()
        return queryset.create(
            FK_User=user,
            MobileNumber=mobile_number,
            IPAddress=user_ip,
            ReferenceCode=reference_code
        )

# ----------------------------------------------------------------------------------------------------------------------------------