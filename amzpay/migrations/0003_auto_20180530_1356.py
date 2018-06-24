# Generated by Django 2.0.5 on 2018-05-30 04:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('amzpay', '0002_auto_20180219_2342'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payorder',
            name='social',
            field=models.ForeignKey(limit_choices_to={'provider': 'amazon'}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='social_django.UserSocialAuth'),
        ),
    ]
