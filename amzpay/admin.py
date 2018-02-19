from django.contrib import admin
from django import forms
from django.contrib.contenttypes.admin import GenericStackedInline

from . import models, utils, encoders


class Mixin(object):

    def admin_url(self, obj):
        return utils.render('''<a href="{{u}}">{{i}}</a>''',
            u=utils.admin_change_url(obj), i=obj)


class ClientForm(forms.ModelForm):
    class Meta:
        model = models.Client
        exclude = []

    def save(self, *args, **kwargs):
        self.instance.auth_scope = ' '.join([
            s.name for s in self.cleaned_data.get('scope_choices', [])])
        return super(ClientForm, self).save(*args, **kwargs)


@admin.register(models.Client)
class ClientAdmin(admin.ModelAdmin):
    form = ClientForm
    list_filter = ['region', 'sandbox']
    list_display = [
        'id', 'merchant_title', 'app_title', 'sandbox', 'currency_code',
        'region', ]
    readonly_fields = ['widget_url', 'auth_scope']

    def widget_url(self, obj):
        return obj.widget


@admin.register(models.Scope)
class ScopeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', ]


class CallMixin(Mixin):
    exclude = ['content_object', 'request', 'response']
    readonly_fields = [
        'admin_url', 'action', 'success',
        'request_json', 'response_json', 'created_at']

    def request_json(self, obj):
        o = encoders.to_yaml(
            obj.request_object,
            allow_unicode=True, default_flow_style=False)
        return utils.render('''<pre>{{ o|safe }}</pre>''', o=o)

    def response_json(self, obj):
        o = encoders.to_yaml(
            obj.response_object,
            allow_unicode=True, default_flow_style=False)
        return utils.render('''<pre>{{ o|safe }}</pre>''', o=o)


class PayCallInline(GenericStackedInline, CallMixin):
    model = models.PayCall
    extra = 0
    exclude = CallMixin.exclude
    readonly_fields = [
        'admin_url', 'success', 'action', 'request_json', 'response_json']

class PayCaptureInline(admin.StackedInline, Mixin):
    model = models.PayCapture
    extra = 0
    readonly_fields = [
        'admin_url',
        'capture_number', 'capture_id', 'state',
        'amount', 'fee', 'refund_amount', 'note', 'descriptor']
    exclude = ['']


@admin.register(models.PayAuth)
class PayAuthAdmin(admin.ModelAdmin):
    inlines = [PayCaptureInline, PayCallInline]
    list_display = [
        'id', 'payorder', 'auth_number', 'authorization_id',
        'state', 'reason', 'amount', 'fee', 'captured_amount',
        'updated_at']
    raw_id_fields = ['payorder']
    readonly_fields =['created_at', 'updated_at']


class PayAuthInline(admin.StackedInline, Mixin):
    model = models.PayAuth
    extra = 0
    exclude = ['']
    readonly_fields = [
        'admin_url',
        'auth_number', 'authorization_id', 'state', 'reason', 'amount', 'fee',
        'captured_amount', 'note']


@admin.register(models.PayOrder)
class PayOrderAdmin(admin.ModelAdmin):
    inlines = [PayAuthInline, PayCallInline]
    list_display = [
        'id', 'order_reference_id', 'social', 'order_object',
        'amount', 'state', 'reason', 'updated_at']
    raw_id_fields = ['social', ]
    readonly_fields =[
        'order_object_admin_url', 'latest_detail', 'created_at', 'updated_at']

    def order_object_admin_url(self, obj):
        return utils.render('''<a href="{{u}}">{{i}}</a>''',
            u=utils.admin_change_url(obj.order_object), i=obj.order_object)

    def latest_detail(self, obj):
        o = encoders.to_yaml(
            obj.latest.response_object,
            allow_unicode=True, default_flow_style=False)
        return utils.render('''<pre>{{ o|safe }}</pre>''', o=o)


@admin.register(models.PayCall)
class PayCallAdmin(admin.ModelAdmin, CallMixin):
    list_display = ['id', 'admin_url', 'action', 'success', 'created_at']
    list_filter =  ['action', 'success']
    exclude = CallMixin.exclude + ['content_type', 'object_id']
    readonly_fields = CallMixin.readonly_fields

    def admin_url(self, obj):
        return obj.content_object and utils.render(
            '''<a href="{{u}}">{{i}}</a>''',
            u=utils.admin_change_url(obj.content_object), i=obj.content_object)


@admin.register(models.PayCapture)
class PayCaptureAdmin(admin.ModelAdmin):
    inlines = [PayCallInline]
    list_display = [
        'id', 'payauth', 'capture_number', 'capture_id',
        'amount', 'descriptor', 'updated_at']
    raw_id_fields = ['payauth']
    readonly_fields =['created_at', 'updated_at']


@admin.register(models.PayRefund)
class PayRefundAdmin(admin.ModelAdmin):
    inlines = [PayCallInline]
    list_display = [
        'id', 'paycapture', 'refund_number', 'refund_id',
        'amount', 'fee', 'descriptor', 'updated_at']
    raw_id_fields = ['paycapture']
    readonly_fields =['created_at', 'updated_at']
