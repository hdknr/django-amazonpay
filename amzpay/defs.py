from django.db import models
from django.utils.translation import ugettext_lazy as _


class Merchant(models.Model):
    '''for Direct call'''
    merchant_title = models.CharField(max_length=100)
    merchant_name = models.CharField(max_length=50)
    merchant_id = models.CharField(max_length=200)
    mws_access_key = models.CharField(max_length=200)
    mws_secret_key = models.CharField(max_length=200)

    class Meta:
        abstract = True


class App(models.Model):
    '''for Javascript'''
    app_title = models.CharField(max_length=100)
    app_name = models.CharField(max_length=50)
    app_id = models.CharField(max_length=200, unique=True)
    client_id = models.CharField(max_length=200, unique=True)
    client_secret = models.CharField(max_length=200)
    redirect_uri = models.CharField(max_length=200)

    class Meta:
        abstract = True


class Conf(models.Model):
    region = models.CharField(max_length=50, default='na')
    currency_code = models.CharField(max_length=50, default='JPY')
    sandbox = models.BooleanField(default=True)

    class Meta:
        abstract = True
