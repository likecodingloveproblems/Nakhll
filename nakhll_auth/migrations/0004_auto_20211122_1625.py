# Generated by Django 3.1.6 on 2021-11-22 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nakhll_auth', '0003_auto_20211122_1236'),
    ]

    operations = [
        migrations.RenameField(
            model_name='authrequest',
            old_name='valid_to',
            new_name='expire_datetime',
        ),
        migrations.AlterField(
            model_name='authrequest',
            name='request_status',
            field=models.CharField(choices=[('pending', 'در انتظار'), ('valid', 'معتبر'), ('invalid', 'نامعتبر')], default='pending', max_length=10),
        ),
    ]