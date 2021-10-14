import json
from cart.models import Cart
from rest_framework.permissions import BasePermission
from cart.utils import get_user_or_guest

def _get_privileges_by_key(permission_key):
    """ internal function to return user side bar items by permission key """
    """ side bar items defined here and assing to groups by permission_key """
    # TODO: SHOULD NOT HARD CODED

    sidebar = []
    # sidebar items in dict
    dashboard_dict = {'id':'dasboard', 'name':'داشبورد', 'url':reverse('nakhll_market:Dashboard'), 'class':'fas fa-id-badge', 'isActive':False, 'staffOnly':False}
    transaction_dict = {'id':'transaction', 'name':'تراکنش ها', 'url':reverse('nakhll_market:Transaction'), 'class':'fad fa-clipboard-list', 'isActive':False, 'staffOnly':False}
    factor_dict = {'id':'factor', 'name':' فاکتور ها', 'url':reverse('nakhll_market:Factor'), 'class':'fas fa-file-invoice-dollar', 'isActive':False, 'staffOnly':False}
    ticketing_dict = {'id':'ticketing', 'name':'پشتیبانی', 'url':reverse('nakhll_market:Ticketing'), 'class':'fad fa-user-headset', 'isActive':False, 'staffOnly':False}
    user_shop_dict = {'id':'userShop', 'name':'مدیریت حجره', 'url':'/fp', 'class':'fas fa-store', 'isActive':False, 'staffOnly':False}
    review_dict = {'id':'review', 'name':'نقدها و نظرات', 'url':reverse('nakhll_market:Review'), 'class':'fad fa-comments-alt', 'isActive':False, 'staffOnly':False}
    alert_dict = {'id':'alert', 'name':'هشدار ها', 'url':reverse('nakhll_market:Alert'), 'class':'fas fa-bell', 'isActive':False, 'staffOnly':True}
    all_user_dict = {'id':'allUser', 'name':'کاربران', 'url':reverse('nakhll_market:Show_All_User_Info'), 'class':'fas fa-users', 'isActive':False, 'staffOnly':True}
    coupon_dict = {'id':'coupon', 'name':'کوپن ها', 'url':reverse('nakhll_market:ManagementCoupunList'), 'class':'fad fa-window-maximize', 'isActive':False, 'staffOnly':True}
    all_shop_dict = {'id':'allShop', 'name':'مدیریت محتوا', 'url':reverse('nakhll_market:Show_All_Content'), 'class':'fas fa-sliders-h', 'isActive':False, 'staffOnly':True}

    # TODO: define access here
    privileges = [
        {'permission_key': 'compress_team_privileges', 'privilege': [dashboard_dict, ]},
        {'permission_key': 'seo_team_privileges', 'privilege': [dashboard_dict, ]},
        {'permission_key': 'accounting_team_privileges', 'privilege': [dashboard_dict, ]},
        {'permission_key': 'writer_team_privileges', 'privilege': [dashboard_dict, ]},
        {'permission_key': 'content_team_privileges', 'privilege': [dashboard_dict, ]},
    ]
    for privilege in privileges:
        if permission_key == privilege['permission_key']:
            sidebar.append(privilege['privilege'])
    return sidebar


def _remove_duplicate_items(list_of_dicts):
    """ remove duplicate dictionaries that are in list by using json """
    list_of_strings = [json.dumps(dictionary) for dictionary in list_of_dicts]
    list_of_strings = set(list_of_strings)
    return [json.loads(s) for s in list_of_strings]


def groups_and_permission(group_name):
    """ a simple method that return group permission code by group_name """
    # method returns type: string
    groups_perms = [
        {'group_name': 'Photo-compress', 'permission_key': 'compress_team_privileges'},
        {'group_name': 'SEO', 'permission_key': 'seo_team_privileges'},
        {'group_name': 'accounting', 'permission_key': 'accounting_team_privileges'},
        {'group_name': 'نویسندگان', 'permission_key': 'writer_team_privileges'},
        {'group_name': 'کاربر محتوا', 'permission_key': 'content_team_privileges'},
    ]
    
    for group_perm in groups_perms :
        if group_perm['group_name'] == group_name:
            return group_perm['permission_key']


def get_group_privileges_sidebar(permission_keys):
    # method returns type: sidebar items array
    final_sidebar = []
    for permission_key in permission_keys:
        final_sidebar.append(_get_privileges_by_key(permission_key))

    final_sidebar = _remove_duplicate_items(final_sidebar)
    return final_sidebar



class IsInvoiceOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        prev_result = super().has_object_permission(request, view, obj)
        user = request.user 
        return prev_result and obj.user == user


class IsInvoiceProvider(BasePermission):
    def has_object_permission(self, request, view, obj):
        prev_result = super().has_object_permission(request, view, obj)
        user = request.user 
        return prev_result and user.id in obj.items.all().values_list('product__FK_Shop__FK_ShopManager__id', flat=True)

