# Generated by Django 2.2.6 on 2020-05-06 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Payment', '0046_factor_bigcity'),
    ]

    operations = [
        migrations.AddField(
            model_name='factor',
            name='PaymentType',
            field=models.CharField(choices=[('0', 'پرداخت در محل'), ('1', 'پرداخت آنلاین'), ('2', 'پرداخت با کیف پول'), ('3', 'پرداخت با بن کارت'), ('4', 'پرداخت با آنلاین - کیف پول'), ('5', 'پرداخت با آنلاین - بن کارت'), ('6', 'پرداخت با کیف پول - بن کارت')], default='1', max_length=1, verbose_name='نوع پرداخت'),
        ),
        migrations.DeleteModel(
            name='PayType',
        ),
    ]