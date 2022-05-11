"""Nakhll project-wide utility functions."""
from rest_framework.views import exception_handler
import csv


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


def construct_change_message(request, form, formsets, add):
    """Construct a change message from a form and formsets.

    This method is replaced with the default construct_change_message method
    from django.contrib.admin.utils.

    Args:
        request (HttpRequest): The request object.
        form (Form): A form object that is used to get the changed data.
        formsets (list): A list of formsets.
        add (bool): A boolean which indicates if the form is used for adding
                    or editing an object.

    Returns:
        str: A string which represents the change message.
    """
    change_message = ""
    data = ""
    if add:
        data = dict_to_table(form.cleaned_data)
        change_message += 'آیتم جدید با مشخصات زیر ایجاد شد:<br>{data}'
    elif form.changed_data:
        fields = {}
        for field in form.changed_data:
            value = form.cleaned_data[field]
            fields[field] = value
        data = dict_to_table(fields)
    elif 'checkout_invoice' in request.POST:
        data = 'فاکتور تسویه شد'
    change_message += 'تغییر در آیتم:<br>{data}'

    change_message = change_message.format(data=data)
    if formsets:
        change_message += str(build_formset_messages(formsets))
    return change_message


def build_formset_messages(formsets):
    """Build a message for formsets.

    Args:
        formsets: Whole formset which should be iterated to get changes and
                  build messages for them.

    Returns:
        string: A string which represents formset changes.
    """
    change_message = ""
    for formset in formsets:
        for added_object in formset.new_objects:
            change_message += f'آیتم جدید با مشخصات زیر ایجاد شد:<br>{dict_to_table(added_object.__dict__)}'
        for changed_object, changed_fields in formset.changed_objects:
            fields = {}
            form = formset.forms[0]
            for field in changed_fields:
                value = form.cleaned_data[field]
                fields[field] = value
            data = dict_to_table(fields)
            change_message += f'تغییر در آیتم:<br>{data}'
        for deleted_object in formset.deleted_objects:
            change_message += f'آیتم با مشخصات زیر حذف شد:<br>{dict_to_table(deleted_object.__dict__)}'
    return change_message


def dict_to_table(dictionary):
    """Convert a dictionary to a table.

    Args:
        dictionary (dict): A dict with keys and values.

    Returns:
        str: A string which represents dictionary as table.
    """
    table = ''
    for key, value in dictionary.items():
        table += f'{key}: {value}<br>'
    return table



def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    error_message = {}
    if response is not None:
        error_message = {}
        if response.data:
            for key, value in response.data.items():
                error_message[key] = f"{str(value[0])}"
        error_message['status_code'] = response.status_code
        response.data = error_message

    return response
