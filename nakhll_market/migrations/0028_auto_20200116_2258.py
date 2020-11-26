# Generated by Django 2.2.6 on 2020-01-16 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nakhll_market', '0027_attrprice_publish'),
    ]

    operations = [
        migrations.AddField(
            model_name='shop',
            name='CanselCount',
            field=models.PositiveIntegerField(default=0, verbose_name='تعداد لغو سفارشات حجره'),
        ),
        migrations.AddField(
            model_name='shop',
            name='CanselFirstDate',
            field=models.DateTimeField(blank=True, null=True, verbose_name='تاریخ اولین لغو سفارش'),
        ),
        migrations.AddField(
            model_name='shop',
            name='LimitCancellationDate',
            field=models.DateTimeField(blank=True, null=True, verbose_name='تاریخ محدودیت لغو سفارشات'),
        ),
        migrations.AlterField(
            model_name='alert',
            name='Part',
            field=models.CharField(choices=[('0', 'ایجاد پروفایل'), ('1', 'ویرایش پروفایل'), ('2', 'ایجاد حجره'), ('3', 'ویراش حجره'), ('4', 'ایجاد بنر حجره'), ('5', 'ویرایش بنر حجره'), ('6', 'ایجاد محصول'), ('7', 'ویراش محصول'), ('8', 'ایجاد بنر محصول'), ('9', 'ویراش بنر محصول'), ('10', 'ایجاد ویژگی جدید'), ('11', 'ثبت ویژگی جدید برای محصول'), ('12', 'ثبت سفارش'), ('13', 'لغو سفارش'), ('14', 'ثبت کامنت جدید'), ('15', 'ثبت نقد و بررسی جدید'), ('16', 'ثبت تیکت جدید'), ('17', 'ایجاد ارزش ویژگی جدید'), ('18', 'ثبت انتقاد و پیشنهاد یا شکایت'), ('19', 'لغو فاکتور'), ('20', 'تایید سفارش'), ('21', 'ارسال سفارش')], default='0', max_length=2, verbose_name='بخش'),
        ),
    ]