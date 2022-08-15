from import_export.resources import ModelResource
from import_export.fields import Field

from .models import AccountRequest


class AccountRequestResource(ModelResource):
    class Meta:
        model = AccountRequest
        fields = (
            'from_account',
            'to_account',
            'staff_user',
            'value',
            'request_type',
            'description',
            'status',
            'date_created',
            'date_confirmed',
            'date_rejected')

    def dehydrate_request_type(self, obj):
        return obj.get_request_type_display()

    def dehydrate_status(self, obj):
        return obj.get_status_display()

    from_account = Field(
        attribute='from_account',
        column_name='حساب مبدا',
        readonly=True
    )
    to_account = Field(
        attribute='to_account',
        column_name='حساب مقصد',
        readonly=True
    )
    staff_user = Field(
        attribute='staff_user',
        column_name='کارمند تایید/رد کننده',
        readonly=True
    )
    value = Field(
        attribute='value',
        column_name='مقدار سکه',
        readonly=True
    )
    request_type = Field(
        column_name='نوع',
        readonly=True
    )
    description = Field(
        attribute='description',
        column_name='توضیحات',
        readonly=True
    )
    status = Field(
        column_name='وضعیت',
        readonly=True
    )
    cashable_value = Field(
        attribute='cashable_value',
        column_name='مقدار قابل تسویه از حساب مبدا',
        readonly=True
    )
    date_created = Field(
        attribute='date_created',
        column_name='تاریخ ایجاد',
        readonly=True
    )
    date_confirmed = Field(
        attribute='date_confirmed',
        column_name='تاریخ تایید',
        readonly=True
    )
    date_rejected = Field(
        attribute='date_rejected',
        column_name='تاریخ رد',
        readonly=True
    )
