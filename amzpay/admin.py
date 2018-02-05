from django.contrib import admin
from django import forms
from . import models


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
