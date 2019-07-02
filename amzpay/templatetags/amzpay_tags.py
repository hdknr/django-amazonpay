from django import template
from django.utils.safestring import mark_safe as _S
from amzpay import utils, api
import json

register = template.Library()


@register.simple_tag(takes_context=False)
def amzpay_include(amzpay, basename, dirname='amzpay', **kwargs):
    template = utils.find_template(dirname, basename)
    return template.render(context=dict(amzpay=amzpay, **kwargs))


@register.simple_tag(takes_context=False)
def amzpay_include_script(amzpay, dirname='amzpay', basename="include.html"):
    template = utils.find_template(dirname, basename)
    return template.render(context=dict(amzpay=amzpay))


@register.simple_tag(takes_context=False)
def amzpay_begin_script(amzpay, address_url, dirname='amzpay', basename="begin.html"):
    template = utils.find_template(dirname, basename)
    return template.render(context=dict(amzpay=amzpay, address_url=address_url))


@register.simple_tag(takes_context=False)
def amzpay_address_script(amzpay, order, dirname='amzpay', basename="address.html"):
    template = utils.find_template(dirname, basename)
    return template.render(context=dict(amzpay=amzpay, order=order))


@register.simple_tag(takes_context=False)
def amzpay_wallet_script(amzpay, dirname='amzpay', basename="wallet.html"):
    template = utils.find_template(dirname, basename)
    return template.render(context=dict(amzpay=amzpay))


@register.filter
def to_amzpay_json(client):
    data = api.serializers.ClientSerializer(client).data
    return _S(json.dumps(data))
