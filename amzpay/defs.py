from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property
from amazon_pay.ap_region import regions
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
    mws_auth_token = models.CharField(
        _('MWS Auth Token'), max_length=200)

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
    region = models.CharField(
        _('MWS Endpoint Region'),
        choices=tuple(i for i in regions.items()),
        max_length=50, default='ja')
    currency_code = models.CharField(max_length=50, default='JPY')
    sandbox = models.BooleanField(default=True)
    handle_throttle = models.BooleanField(default=False)

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


class SellerOrder(models.Model):
    order_number = models.CharField(
        _('Seller Order ID'),
        max_length=50, unique=True, null=True, default=None, blank=True)
    amount = models.DecimalField(
        _('Amount'), max_digits=9, decimal_places=2, default=0, blank=True)
    customer = models.TextField(
        _('Customer Information'), null=True, default=None, blank=True)

    class Meta:
        abstract = True


class PayOrder(SellerOrder):
    order_reference_id = models.CharField(
        _('Amazon Pay Order Reference ID'),
        max_length=50, unique=True, null=True, default=None, blank=True)
    state = models.CharField(
        _('Amazon Pay Order State'),
        max_length=20, null=True, default=None, blank=True)
    reason = models.CharField(
        _('Amazon Pay Order State Reason'),
        max_length=30, null=True, default=None, blank=True)
    description = models.TextField(
        _('Amazon Pay Order State Reason Description'),
        null=True, default=None, blank=True)
    created_at = models.DateTimeField(_(u'Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_(u'Updated At'), auto_now=True)

    class Meta:
        abstract = True


class PayAuth(models.Model):
    ''' Authorization
    https://pay.amazon.com/jp/developer/documentation/apireference/201752450
    '''
    auth_number = models.CharField(
        _('Application Authorization Number(ID)'), max_length=32, unique=True)
    authorization_id = models.CharField(
        _('Amazon Pay Authorization ID'),
        max_length=50, unique=True, null=True, default=None, blank=True)
    state = models.CharField(
        _('Amazon Pay Auth State'),
        max_length=20, null=True, default=None, blank=True)
    reason = models.CharField(
        _('Amazon Pay Auth State Reason'),
        max_length=30, null=True, default=None, blank=True)

    amount = models.DecimalField(
        _('Authorization Amount'),
        max_digits=9, decimal_places=2, default=0, blank=True)
    fee = models.DecimalField(
        _('Authroization Fee'),
        max_digits=9, decimal_places=2, default=0, blank=True)
    captured_amount = models.DecimalField(
        _('Captured Amount'),
        max_digits=9, decimal_places=2, default=0, blank=True)
    note = models.TextField(
        _('Seller Authorization Note'), null=True, default=None, blank=True)

    created_at = models.DateTimeField(_(u'Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_(u'Updated At'), auto_now=True)

    class Meta:
        abstract = True


class PayCapture(models.Model):
    ''' Capture:
    https://pay.amazon.com/jp/developer/documentation/apireference/201752040
    '''
    capture_number = models.CharField(
        _('Application Capture Number(ID)'), max_length=32, unique=True)
    capture_id = models.CharField(
        _('Amazon Pay Capture ID'),
        max_length=32, unique=True, null=True, default=None, blank=True)
    state = models.CharField(
        _('Amazon Pay Capture State'),
        max_length=20, unique=True, null=True, default=None, blank=True)
    amount = models.DecimalField(
        _('Capture Amount'),
        max_digits=9, decimal_places=2, default=0, blank=True)
    fee = models.DecimalField(
        _('Capture Fee'),
        max_digits=9, decimal_places=2, default=0, blank=True)
    refund_amount = models.DecimalField(
        _('Refund Amount'),
        max_digits=9, decimal_places=2, default=0, blank=True)
    note = models.TextField(
        _('Seller Capture Note'), null=True, blank=True, default=None)
    descriptor = models.CharField(
        _('Capture Soft Descriptor'),
        max_length=16, null=True, default=None, blank=True)

    created_at = models.DateTimeField(_(u'Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_(u'Updated At'), auto_now=True)

    class Meta:
        abstract = True


class PayRefund(models.Model):
    ''' Refund:
    https://pay.amazon.com/jp/developer/documentation/apireference/201752740
    '''
    refund_number = models.CharField(
        _('Application Refund Number(ID)'), max_length=32, unique=True)
    refund_id = models.CharField(
        _('Amazon Pay Refund ID'),
        max_length=32, unique=True, null=True, default=None, blank=True)
    state = models.CharField(
        _('Amazon Pay Refund State'),
        max_length=20,  null=True, default=None, blank=True)

    amount = models.DecimalField(
        _('Refund Amount'),
        max_digits=9, decimal_places=2, default=0, blank=True)
    fee = models.DecimalField(
        _('Refund Fee'),
        max_digits=9, decimal_places=2, default=0, blank=True)

    note = models.TextField(
        _('Seller Refund Note'), null=True, blank=True, default=None)
    descriptor = models.CharField(
        _('Refund Soft Descriptor'),
        max_length=16, null=True, default=None, blank=True)

    created_at = models.DateTimeField(_(u'Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_(u'Updated At'), auto_now=True)

    class Meta:
        abstract = True


class PayCall(models.Model):
    action = models.CharField(max_length=100)
    success = models.BooleanField(default=False)
    request = models.TextField(default='', blank=True)
    response = models.TextField(default='', blank=True)
    created_at = models.DateTimeField(_(u'Created At'), auto_now_add=True)

    class Meta:
        abstract = True


class PhysicalDestination(models.Model):
    '''
    https://pay.amazon.com/jp/developer/documentation/apireference/201752430
    '''
    Name = models.CharField(max_length=100)             # Customer or Company
    AddressLine1 = models.CharField(max_length=200)
    AddressLine2 = models.CharField(max_length=200)
    AddressLine3 = models.CharField(max_length=200)     # Company Name in JP
    City = models.CharField(max_length=50)              # NOT for JP
    Country = models.CharField(max_length=50)           # NOT for JP
    District = models.CharField(max_length=50)          # NOT for JP
    StateOrRegion = models.CharField(max_length=50)     # prefecture...
    PostalCode = models.CharField(max_length=50)
    CountryCode = models.CharField(max_length=10)
    Phone = models.CharField(max_length=50)

    class Meta:
        abstract = True
