from django.db import models
from django.utils.translation import ugettext_lazy as _
from . import defs, methods


class Client(defs.Merchant, defs.App, defs.Conf, methods.Client):

    class Meta:
        verbose_name = ('Amazon Pay Client')
        verbose_name_plural = ('Amazon Pay Clients')
