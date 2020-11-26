# Generated by Django 2.2.6 on 2019-12-20 10:42

import Ticketing.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ticketing', '0006_auto_20191220_1351'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticketingmessage',
            name='Image',
        ),
        migrations.AddField(
            model_name='ticketing',
            name='Description',
            field=models.TextField(blank=True, null=True, verbose_name='توضیحات'),
        ),
        migrations.AddField(
            model_name='ticketing',
            name='Image',
            field=models.ImageField(blank=True, help_text='عکس مربوط به تیکت خود را اینجا بارگذاری کنید', null=True, upload_to=Ticketing.models.PathAndRename('media/Pictures/Ticketing'), verbose_name='عکس تیکت'),
        ),
    ]