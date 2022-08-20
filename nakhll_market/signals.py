from django.db.models.signals import pre_save
from django.contrib.auth.models import User
from django.dispatch import receiver


@receiver(pre_save, sender=User)
def update_profile_mobile_number_based_on_the_username_on_user_update(
        sender, instance, **kwargs):
    if instance.pk:
        instance.User_Profile.MobileNumber = instance.username
        instance.User_Profile.save()
