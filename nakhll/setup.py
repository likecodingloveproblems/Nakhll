from django.contrib import admin
from django.contrib.admin import ModelAdmin


def seutp():
    """Setups that must be run before the application starts.

    This function is called by nakhll/urls.py
    """
    override_admin_panel_defaults()
    change_default_cipher_to_seclevel_1()


def override_admin_panel_defaults():
    """Change values in django admin panel UI."""
    admin.site.site_header = "بازار آنلاین نخل"
    admin.site.site_title = "بازار آنلاین نخل"
    admin.site.index_title = "بازار آنلاین نخل، خوش آمدید!"


def change_default_cipher_to_seclevel_1():
    """Change default cipher to seclevel 1

    To connect to SEP IPG, we need the older cipher that is seclevel 1.
    Ubuntu 20.04 won't allow clients to connect to server with small DH key.
    Workaround from SO: https://stackoverflow.com/a/41041028/14272982
    """
    import requests
    import urllib3
    requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL:@SECLEVEL=1'
