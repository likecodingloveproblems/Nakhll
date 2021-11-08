# Generated by Django 3.1.6 on 2021-11-07 14:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shop', '0005_auto_20211107_1648'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shoplanding',
            name='status',
            field=models.CharField(choices=[('active', 'فعال'), ('inactive', 'غیرفعال')], default='inactive', max_length=10, verbose_name='وضعیت'),
        ),
        migrations.CreateModel(
            name='PinnedURL',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='نام')),
                ('link', models.URLField(verbose_name='لینک')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pinned_urls', to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
            options={
                'verbose_name': 'لینک پین شده',
                'verbose_name_plural': 'لینک پین شده',
            },
        ),
    ]