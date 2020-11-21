from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()

# -------------------------------------------------------------------------------------------------------------------------------------

def currency(value):
    return '{:,}'.format(int(value))
register.filter('currency', currency)