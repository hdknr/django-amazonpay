# Generated by Django 2.0.5 on 2018-06-24 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('amzpay', '0003_auto_20180530_1356'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='is_default',
            field=models.BooleanField(default=False, verbose_name='Default Client'),
        ),
    ]
