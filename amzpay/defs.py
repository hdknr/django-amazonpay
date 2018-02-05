from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property
import json


class Scope(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True, default=None)

    class Meta:
        abstract = True


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

    # handle_throttle       # Bool
    # api_version           # Char(Fixed)
    # service_version       # Char('2013-01-01')
    # mws_endpoint          #  'https://mws.amazonservices.com/OffAmazonPayments_Sandbox/{}'.format(self.service_version

    class Meta:
        abstract = True


BUTTON_TYPE_CHOICES = (
    ('LwA', _('Login with Amazon')),
    ('PwA', _('Pay with Amazon')),
)

BUTTON_COLOR_CHOICES = (
    ('Gold', _('Gold')),
    ('LightGray', _('Light Gray')),
    ('DarkGray', _('Dark Gray')),
)

BUTTON_SIZE_CHOICES = (
    ('small', _('Small Button Size')),
    ('medium', _('Medium Button Size')),
    ('large', _('Large Button Size')),
    ('x-large', _('XLarge Button Size')),
)


class Button(models.Model):
    '''
    https://pay.amazon.com/jp/developer/documentation/lpwa/201953980
    '''
    button_type = models.CharField(
        max_length=20,
        choices=BUTTON_TYPE_CHOICES, default=BUTTON_TYPE_CHOICES[0][0])

    button_color = models.CharField(
        max_length=20,
        choices=BUTTON_COLOR_CHOICES, default=BUTTON_COLOR_CHOICES[0][0])

    button_size = models.CharField(
        max_length=20,
        choices=BUTTON_SIZE_CHOICES, default=BUTTON_SIZE_CHOICES[0][0])

    class Meta:
        abstract = True


class Auth(models.Model):
    auth_scope = models.TextField(null=True, default=None, blank=True)
    auth_popup = models.BooleanField(default=True)

    class Meta:
        abstract = True

    @cached_property
    def auth_options(self):
        return dict(scope=self.auth_scope, popup=self.auth_popup)
