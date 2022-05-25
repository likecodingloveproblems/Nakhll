from django.db import migrations


def create_dummy_category(apps, schema_editor):
    '''create a dummy category'''
    Category = apps.get_model("nakhll_market", "Category")
    Category.objects.create(
        name='dummy',
        slug='dummy',
    )


def replace_none_with_dummy_category_in_product(apps, schema_editor):
    '''we have some products without any category,
    so we need to replace them with a dummy category
    then we modify schema to make it not null'''
    Product = apps.get_model("nakhll_market", "Product")
    Category = apps.get_model("nakhll_market", "Category")
    dummy_category = Category.objects.get(name='dummy')
    Product.objects.filter(category=None).\
        update(category=dummy_category)


class Migration(migrations.Migration):

    dependencies = [
        ('nakhll_market', '0146_auto_20220501_1906'),
    ]

    operations = [
        migrations.RunPython(
            create_dummy_category,
            migrations.RunPython.noop),
        migrations.RunPython(
            replace_none_with_dummy_category_in_product,
            migrations.RunPython.noop),
    ]
