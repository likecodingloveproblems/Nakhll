# Generated by Django 2.2.6 on 2020-01-06 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Payment', '0014_factorpost_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='factorpost',
            name='Description',
            field=models.TextField(blank=True, null=True, verbose_name='توضیحات'),
        ),
    ]