from django.db import models, transaction
from bank import account_requests
from bank.account_requests import CreateRequest
from bank.constants import NAKHLL_ACCOUNT_ID


class AppendOnlyMixin:
    '''we also have modifying object from save method
    and we have bulk_update method
    '''

    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise Exception('you can\'t update coin')
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise Exception('you can\'t delete coin')

    def update(self, *args, **kwargs):
        raise Exception('you can\'t update coin')


class AccountManager(models.Manager):
    @property
    def nakhll_account(self):
        return self.get_queryset().get(pk=NAKHLL_ACCOUNT_ID)

    @property
    def nakhll_account_for_update(self):
        return self.get_queryset().select_for_update().get(pk=NAKHLL_ACCOUNT_ID)


class AccountRequestManager(models.Manager):
    def create(self, *args, **kwargs):
        self._for_write = True
        with transaction.atomic():
            account_request = self.model(*args, **kwargs)
            CreateRequest(account_request).create()
