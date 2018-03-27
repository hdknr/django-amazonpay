from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from social_django.models import UserSocialAuth
from . import defs, methods, querysets


class Scope(defs.Scope):

    class Meta:
        verbose_name = ('Amazon Pay Scope')
        verbose_name_plural = ('Amazon Pay Scopes')

    def __str__(self):
        return self.name


class Client(defs.Merchant, defs.App, defs.Conf,
             defs.Button, defs.Auth, methods.Client):

    scope_choices = models.ManyToManyField(Scope)

    class Meta:
        verbose_name = ('Amazon Pay Client')
        verbose_name_plural = ('Amazon Pay Clients')

    def __str__(self):
        return "{} {}".format(self.merchant_title, self.app_title)


class PayCall(defs.PayCall, methods.PayCall):
    content_type = models.ForeignKey(
        ContentType,
        null=True, default=None, blank=True, on_delete=models.SET_NULL)
    object_id = models.PositiveIntegerField(
        null=True, default=None, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = ('Amazon Pay Call')
        verbose_name_plural = ('Amazon Pay Calls')

    objects = querysets.PayCallQuerySet.as_manager()

    def __str__(self):
        return "{} {}".format(str(self.content_object), self.action)


class PayMixin(object):

    def log_call(self, action, request, response):
        return PayCall.objects.create_for(self, action, request, response)

    def get_last_call(self, *action):
        return PayCall.objects.filter(
            content_type__model=self._meta.model_name,
            object_id=self.id, action__in=action).last()


class PayOrder(defs.PayOrder, methods.PayOrder, PayMixin):
    client = models.ForeignKey(Client, null=True, on_delete=models.SET_NULL)
    social = models.ForeignKey(
        UserSocialAuth, limit_choices_to={'provider': 'amazon'},
        null=True, on_delete=models.SET_NULL)

    order_content_type = models.ForeignKey(
        ContentType,
        null=True, default=None, blank=True, on_delete=models.SET_NULL)
    order_object_id = models.PositiveIntegerField(
        null=True, default=None, blank=True)
    order_object = GenericForeignKey('order_content_type', 'order_object_id')

    objects = querysets.PayOrderQuerySet.as_manager()

    class Meta:
        verbose_name = ('Amazon Pay Order')
        verbose_name_plural = ('Amazon Pay Orders')
        unique_together = [['order_content_type', 'order_object_id']]

    def __str__(self):
        return "{} {}".format(str(self.social), self.order_reference_id or '')


class PayAuth(defs.PayAuth, methods.PayAuth, PayMixin):
    payorder = models.ForeignKey(PayOrder, null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = ('Amazon Pay Authorization')
        verbose_name_plural = ('Amazon Pay Authorizations')

    def __str__(self):
        return "{} {}".format(str(self.payorder), self.authorization_id or '')


class PayCapture(defs.PayCapture, methods.PayCapture, PayMixin):
    payauth = models.ForeignKey(PayAuth, null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = ('Amazon Pay Capture')
        verbose_name_plural = ('Amazon Pay Captures')

    def __str__(self):
        return "{} {}".format(str(self.payauth), self.capture_id or '')


class PayRefund(defs.PayRefund, methods.PayRefund, PayMixin):
    paycapture = models.ForeignKey(
        PayCapture, null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = ('Amazon Pay Refund')
        verbose_name_plural = ('Amazon Pay Refunds')

    def __str__(self):
        return "{} {}".format(str(self.paycapture), self.refund_id or '')
