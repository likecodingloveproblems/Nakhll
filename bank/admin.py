from django.contrib import admin
from django.contrib.auth import get_permission_codename
from import_export.admin import ExportActionMixin
from bank.models import (
    CoinMintBurn,
    Account,
    AccountRequest,
    AccountTransaction
)
from bank.resources import AccountRequestResource
from nakhll.admin_utils import AppendOnlyModelAdmin, ReadOnlyModelAdmin
from bank.constants import (
    BANK_ACCOUNT_ID,
    FUND_ACCOUNT_ID,
)

@admin.register(CoinMintBurn)
class CoinMinBurnAdmin(AppendOnlyModelAdmin):
    fields = ['user', 'value', 'description', 'date_created']
    readonly_fields = ['user', 'date_created']
    list_display = ['user', 'value', 'description', 'date_created']

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        return super().save_model(request, obj, form, change)


@admin.register(Account)
class AccountAdmin(AppendOnlyModelAdmin):
    autocomplete_fields = ['user']
    list_display = ['name', 'balance', 'date_created']
    search_fields = ['user__username']
    list_filter = ['date_created']
    readonly_fields = [
        'balance',
        'blocked_balance',
        'cashable_amount',
        'blocked_cashable_amount',
        'date_created', ]

    @admin.display(ordering='user__username', description='حساب')
    def name(self, obj):
        return obj

    def get_search_results(self, request, queryset, search_term):
        if search_term == 'بانک':
            return queryset.filter(id=BANK_ACCOUNT_ID), False
        elif search_term == 'صندوق':
            return queryset.filter(id=FUND_ACCOUNT_ID), False
        else:
            return super().get_search_results(request, queryset, search_term)

@admin.register(AccountRequest)
class AccountRequestAdmin(ExportActionMixin, AppendOnlyModelAdmin):
    autocomplete_fields = ['from_account', 'to_account']
    createonly_fields = [
        'request_type',
        'from_account',
        'to_account',
        'value',
        'description',
        'cashable_value',
    ]
    readonly_fields = [
        'status',
        'date_confirmed',
        'date_rejected',
        'staff_user',
        'cashable_value', ]
    search_fields = [
        'from_account__user__username',
        'to_account__user__username']
    list_filter = ['status', 'request_type']
    change_form_template = "admin/custom/account_request_change_confirm_or_reject.html"
    custom_model_actions = {'create', 'confirm', 'reject'}
    resource_class = AccountRequestResource

    def save_model(self, request, obj, form, change):
        if not change:
            obj.create()
        elif "confirm" in request.POST:
            obj.confirm(request.user)
            self.message_user(
                request, "درخواست انتقال با موفقیت تایید شد.")
        elif "reject" in request.POST:
            if request.user.has_perm('bank.account_request'):
                obj.reject(request.user)
                self.message_user(request, "درخواست انتقال رد شد.")

    def has_change_permission(self, request, obj=None):
        custom_action = list(
            self.custom_model_actions.intersection(
                request.POST))
        if custom_action:
            codename = get_permission_codename(custom_action[0], self.opts)
            return request.user.has_perm(
                "%s.%s" % (self.opts.app_label, codename))

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + self.createonly_fields
        return self.readonly_fields


@admin.register(AccountTransaction)
class AccountTransactionAdmin(ReadOnlyModelAdmin):
    pass
