from amazon_pay.client import AmazonPayClient
from django.utils.functional import cached_property


class Client(object):

    @cached_property
    def api(self):
        return AmazonPayClient(
            mws_access_key=self.mws_access_key,
            mws_secret_key=self.mws_secret_key,
            merchant_id=self.merchant_id,
            region=self.region,
            currency_code=self.currency_code,
            sandbox=self.sandbox)

    @cached_property
    def widget(self):
        return ''.join([
            'https://static-fe.payments-amazon.com/OffAmazonPayments/jp',
            '/sandbox' if self.sandbox else '',
            '/lpa/js/Widgets.js',
        ])

    @cached_property
    def scopes(self):
        return " ".join([s.name for s in self.scope_choices.all()])
    
