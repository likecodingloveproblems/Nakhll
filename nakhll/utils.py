import csv


def queryset_to_csv(queryset, filename):
    """
    Export a queryset to a csv file.
    """
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=list(queryset._fields), extrasaction='ignore', restval='NA')
        writer.writeheader()
        for obj in queryset:
            writer.writerow(obj)