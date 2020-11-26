# Generated by Django 2.2.6 on 2020-04-23 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nakhll_market', '0050_auto_20200422_0319'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='PostPrice',
        ),
        migrations.RemoveField(
            model_name='product',
            name='PostType',
        ),
        migrations.RemoveField(
            model_name='product',
            name='Weight',
        ),
        migrations.AddField(
            model_name='product',
            name='Height_With_Packaging',
            field=models.CharField(max_length=4, null=True, verbose_name='ارتفاع محصول با بسته بندی (سانتی متر('),
        ),
        migrations.AddField(
            model_name='product',
            name='Length_With_Packaging',
            field=models.CharField(max_length=4, null=True, verbose_name='طول محصول با بسته بندی (سانتی متر('),
        ),
        migrations.AddField(
            model_name='product',
            name='Net_Weight',
            field=models.CharField(max_length=6, null=True, verbose_name='وزن محصول خالص (گرم)'),
        ),
        migrations.AddField(
            model_name='product',
            name='Packing_Weight',
            field=models.CharField(max_length=5, null=True, verbose_name='وزن محصول بسته بندی (گرم)'),
        ),
        migrations.AddField(
            model_name='product',
            name='Width_With_Packaging',
            field=models.CharField(max_length=4, null=True, verbose_name='عرض محصول با بسته بندی (سانتی متر('),
        ),
    ]