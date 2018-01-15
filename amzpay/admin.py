from django.contrib import admin
from . import models


@admin.register(models.Client)
class ClientAdmin(admin.ModelAdmin):
    list_filter = ['region', 'sandbox']
    list_display = [
        'id', 'merchant_title', 'app_title', 'sandbox', 'currency_code',
        'region', ]
    readonly_fields = ['widget_url']

    def widget_url(self, obj):
        return obj.widget
