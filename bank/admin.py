from django.contrib import admin
from django.contrib.auth import get_permission_codename
from bank.models import (
    CoinMintBurn,
    Account,
    AccountRequest,
    AccountTransaction
)
from nakhll.admin_utils import AppendOnlyModelAdmin, ReadOnlyModelAdmin


@admin.register(CoinMintBurn)
class CoinMinBurnAdmin(AppendOnlyModelAdmin):
    readonly_fields = ['user']
    list_display = ['user', 'value', 'description', 'date_created']

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        return super().save_model(request, obj, form, change)


@admin.register(Account)
class AccountAdmin(AppendOnlyModelAdmin):
    autocomplete_fields = ['user']
    list_display = ['user', 'balance', 'date_created']
    search_fields = ['user__username']
    list_filter = ['date_created']


@admin.register(AccountRequest)
class AccountRequestAdmin(AppendOnlyModelAdmin):
    autocomplete_fields = ['from_account', 'to_account']
    createonly_fields = [
        'from_account',
        'to_account',
        'value',
        'request_type',
        'description',
        'cashable_value',
    ]
    readonly_fields = [
        'status',
        'date_confirmed',
        'date_rejected',
        'staff_user', ]
    search_fields = [
        'from_account__user__username',
        'to_account__user__username']
    list_filter = ['status', 'request_type']
    change_form_template = "admin/custom/account_request_change_confirm_or_reject.html"
    custom_model_actions = {'create', 'confirm', 'reject'}

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
