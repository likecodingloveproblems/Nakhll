from django.contrib import admin
from django.contrib.admin import ModelAdmin


def seutp():
    """Setups that must be run before the application starts.

    This function is called by nakhll/urls.py
    """
    override_admin_panel_defaults()


def override_admin_panel_defaults():
    """Change values in django admin panel UI."""
    admin.site.site_header = "بازار آنلاین نخل"
    admin.site.site_title = "بازار آنلاین نخل"
    admin.site.index_title = "بازار آنلاین نخل، خوش آمدید!"
