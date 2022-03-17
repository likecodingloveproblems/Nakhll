from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .utils import construct_change_message


def seutp():
    """Setups that must be run before the application starts.

    This function is called by nakhll/urls.py
    """
    override_entrylog_message_constructor()
    override_admin_panel_defaults()


def override_entrylog_message_constructor():
    """Replace django's message constructor with our own."""
    ModelAdmin.construct_change_message = (
        lambda self, request, form, formsets, add:
        construct_change_message(request, form, formsets, add)
    )


def override_admin_panel_defaults():
    """Change values in django admin panel UI."""
    admin.site.site_header = "بازار آنلاین نخل"
    admin.site.site_title = "بازار آنلاین نخل"
    admin.site.index_title = "بازار آنلاین نخل، خوش آمدید!"
