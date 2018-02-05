from django.db import models
from django.utils.translation import ugettext_lazy as _
from . import defs, methods


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
