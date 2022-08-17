from django.db import models
from django.db.models import Q, Sum
from bank.constants import (
    BANK_ACCOUNT_ID,
    FUND_ACCOUNT_ID,
    RequestStatuses,
    RequestTypes,
)


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
    def bank_account(self):
        return self.get_queryset().get(pk=BANK_ACCOUNT_ID)

    @property
    def bank_account_for_update(self):
        return self.get_queryset().select_for_update().get(pk=BANK_ACCOUNT_ID)

    @property
    def fund_account(self):
        return self.get_queryset().get(pk=FUND_ACCOUNT_ID)

    @property
    def fund_account_for_update(self):
        return self.get_queryset().select_for_update().get(pk=FUND_ACCOUNT_ID)



class AccountRequestQuerySet(models.QuerySet):
    def filter_account_requests(self, account):
        return self.filter(Q(from_account=account) | Q(to_account=account))

    def request_coins_report(self):
        return self.values(
            'request_type', 'status').annotate(
            coins=Sum('value'))

    def update_request_and_status_to_labels(self):
        list(map(lambda row: row.update(
            {
                'request_type_label': RequestTypes(row['request_type']).label,
                'status_label': RequestStatuses(row['status']).label
            }
        ), self))
        return self


class AccountRequestManager(models.Manager):
    def get_queryset(self):
        return AccountRequestQuerySet(self.model, using=self._db)

    def create(self, *args, **kwargs):
        self._for_write = True
        return self.model(*args, **kwargs).create()


    def account_request_coins_report(
            self, account):
        queryset = self.get_queryset().filter(
            status=RequestStatuses.CONFIRMED).filter_account_requests(
            account).request_coins_report().update_request_and_status_to_labels()
        return queryset


class DepositRequestManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(request_type=RequestTypes.DEPOSIT)
