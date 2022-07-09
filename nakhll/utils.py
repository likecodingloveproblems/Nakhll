"""Nakhll project-wide utility functions."""
import csv
from import_export.formats.base_formats import XLSX
from django.http import HttpResponse
import jdatetime


def queryset_to_csv(queryset, filename):
    """Export a queryset to a csv file.

    Args:
        queryset (QuerySet): A queryset which should be exported to csv.
        filename (str): A string which represents the filename of the csv file.
    """
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=list(
                queryset._fields),
            extrasaction='ignore',
            restval='NA')
        writer.writeheader()
        for obj in queryset:
            writer.writerow(obj)


def get_dict(objects, key):
    dic = {}
    for item in objects:
        dic[getattr(item, key)] = item.id
    return dic


def excel_response(resource, queryset=None, filename='report'):
    dataset = resource().export(queryset=queryset)
    response = HttpResponse(dataset.xlsx,
                            content_type=XLSX)
    response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
    return response


def datetime2jalali(datetime, date_only=False):
    if datetime is None:
        return None
    date_time_format = '%Y/%m/%d %H:%M'
    date_format = '%Y/%m/%d'
    format = date_format if date_only else date_time_format
    return jdatetime.datetime.fromgregorian(
        datetime=datetime, locale='fa_IR').strftime(format)
