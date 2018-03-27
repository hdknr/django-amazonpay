from django.utils.functional import cached_property
from django.contrib.contenttypes.models import ContentType
from social_django.models import UserSocialAuth
from amazon_pay.client import AmazonPayClient
from django.utils import timezone
from . import defs, encoders
from .utils import (
    value_from_response as _VR,
    value_from_dict as _VD,
    datekey,
)


def new_number(prefix, salt=None, length=32):
    key = datekey(salt=salt)
    number = "{}-{}".format(prefix, key)
    return number[:length]


class Client(object):

    @cached_property
    def api(self):
        return AmazonPayClient(
            mws_access_key=self.mws_access_key,
            mws_secret_key=self.mws_secret_key,
            merchant_id=self.merchant_id,
            region=self.region,
            currency_code=self.currency_code,
            handle_throttle=self.handle_throttle,
            sandbox=self.sandbox)

    @cached_property
    def widget(self):
        return ''.join([
            'https://static-fe.payments-amazon.com/OffAmazonPayments/jp',
            '/sandbox' if self.sandbox else '',
            '/lpa/js/Widgets.js',
        ])


class PayOrder(object):
    '''
    OrderReferenceDetails:
    - https://pay.amazon.com/jp/developer/documentation/apireference/201752660

    OrderReferenceAttributes:
    - https://pay.amazon.com/jp/developer/documentation/apireference/201752640

    OrderReferenceStatus:
    - https://pay.amazon.com/jp/developer/documentation/apireference/201752680

    OrderTotal:
    - https://pay.amazon.com/jp/developer/documentation/apireference/201752700

    SellerOrderAttributes:
    - https://pay.amazon.com/jp/developer/documentation/apireference/201752790

    Constraint(error information):
    - https://pay.amazon.com/jp/developer/documentation/apireference/201752600

    Destination:
    - https://pay.amazon.com/jp/developer/documentation/apireference/201752620

    Address:
    - https://pay.amazon.com/jp/developer/documentation/apireference/201752430
    '''
    @cached_property
    def api(self):
        return self.client.api

    @cached_property
    def store_name(self):
        return self.client.merchant_name

    @cached_property
    def detail(self):
        return encoders.from_json(self.latest.response_object)

    @cached_property
    def latest(self):
        return self.get_last_call(
            'get_order_reference_details', 'set_order_reference_details')

    def update_status(self, response):
        # Update State and Reason
        state = _VR(response, 'OrderReferenceStatus')
        self.state = state.get('State', None)
        self.reason = state.get('ReasonCode', None)
        self.description = state.get('ReasonDescription', None)
        self.save()

    def get_detail(self):
        '''API: GetOrderReferenceDetails
        - https://pay.amazon.com/jp/developer/documentation/apireference/201751970
        - https://github.com/amzn/amazon-pay-sdk-python/blob/master/amazon_pay/client.py#L759
        '''
        request = dict(
            amazon_order_reference_id=self.order_reference_id,
            # address_consent_token=self.social.access_token,       # optional
            mws_auth_token=self.client.mws_auth_token, )

        response = self.api.get_order_reference_details(**request)

        call = self.log_call('get_order_reference_details', request, response)

        if response.success:
            # Update State and Reason
            self.update_status(response)

        return call

    def set_detail(self, note='', customer=''):
        '''API: SetOrderReferenceDetails
        - https://pay.amazon.com/jp/developer/documentation/apireference/201751960
        - https://github.com/amzn/amazon-pay-sdk-python/blob/master/amazon_pay/client.py#L570
        '''
        request = dict(
            amazon_order_reference_id=self.order_reference_id,
            order_total=self.amount,                # OrderReferenceAttributes
            seller_note=note,                       # OrderReferenceAttributes
            seller_order_id=self.order_number,      # SellerOrderAttributes
            store_name=self.store_name,             # SellerOrderAttributes
            custom_information=customer)            # SellerOrderAttributes

        response = self.api.set_order_reference_details(**request)

        call = self.log_call('set_order_reference_details', request, response)

        if response.success:
            # Update State and Reason
            self.update_status(response)

        return call

    def confirm(self):
        '''API: ConfirmOrderReference
        https://pay.amazon.com/jp/developer/documentation/apireference/201751980
        '''
        request = dict(amazon_order_reference_id=self.order_reference_id)
        response = self.api.confirm_order_reference(**request)
        call = self.log_call('confirm_order_reference', request, response)
        return call

    def close(self, reason="close"):
        '''API: CloseOrderReference
        https://pay.amazon.com/jp/developer/documentation/apireference/201752000                # NOQA
        https://github.com/amzn/amazon-pay-sdk-python/blob/master/amazon_pay/client.py#L866     # NOQA
        '''
        request = dict(
            amazon_order_reference_id=self.order_reference_id,
            closure_reason=reason,
            merchant_id=self.client.merchant_id,
            mws_auth_token=self.client.mws_auth_token, )
        response = self.api.close_order_reference(**request)
        call = self.log_call('close_order_reference', request, response)
        return call

    @cached_property
    def destination(self):
        '''
        https://pay.amazon.com/jp/developer/documentation/apireference/201752660
        https://pay.amazon.com/jp/developer/documentation/apireference/201752620
        '''
        data = _VD(
            self.latest.response_object,
            'GetOrderReferenceDetailsResponse',
            'GetOrderReferenceDetailsResult',
            'OrderReferenceDetails', 'Destination')

        if data.get('DestinationType', None) == 'Physical':
            return data.get('PhysicalDestination', {})

    def create_auth(self, note='', auth_number=None):
        '''Create Amazon Pay Authorization'''
        auth_number = auth_number or new_number('A')
        return self.payauth_set.create(
            amount=self.amount,
            note=note,
            auth_number=auth_number)


class PayAuth(object):
    '''
    AuthorizationDetails:
    - https://pay.amazon.com/jp/developer/documentation/apireference/201752450

    Price:
    - https://pay.amazon.com/jp/developer/documentation/apireference/201752720

    Status:
    - https://pay.amazon.com/jp/developer/documentation/apireference/201752820
    '''
    @cached_property
    def client(self):
        return self.payorder.client

    @cached_property
    def latest(self):
        return self.get_last_call('authorize', 'get_authorization_details')

    def update_status(self, response):
        self.authorization_id = _VR(response, 'AmazonAuthorizationId')
        self.state = _VR(response, 'AuthorizationStatus', 'State')
        self.reason = _VR(response, 'AuthorizationStatus', 'ReasonCode')
        self.captured_amount = _VR(response, 'CapturedAmount', 'Amount')
        self.fee = _VR(response, 'AuthorizationFee', 'Amount')
        self.save()

    def authorize(self):
        '''API: Authorize '''
        request = dict(
            amazon_order_reference_id=self.payorder.order_reference_id,
            authorization_reference_id=self.auth_number,
            authorization_amount=self.payorder.amount,
            seller_authorization_note=self.note,
            transaction_timeout=0,
            capture_now=False)

        response = self.client.api.authorize(**request)

        call = self.log_call('authorize', request, response)

        if response.success:
            self.update_status(response)

        return call

    def get_detail(self):
        '''API: GetAuthorizationDetails'''
        request = dict(amazon_authorization_id=self.authorization_id)
        response = self.client.api.get_authorization_details(**request)
        call = self.log_call('get_authorization_details', request, response)

        if response.success:
            self.update_status(response)

        return call

    def close(self, reason=''):
        '''API: CloseAuthorization
        https://pay.amazon.com/jp/developer/documentation/apireference/201752070
        '''
        request = dict(
            amazon_authorization_id=self.authorization_id,
            closure_reason=reason)

        response = self.client.api.close_authorization(**request)
        call = self.log_call('close_authorization', request, response)
        return call

    def create_capture(self, capture_number=None):
        capture_number = capture_number or new_number('C')
        return self.paycapture_set.create(
            amount=self.amount,
            capture_number=capture_number)


class PayCapture(object):
    '''
    CaptureDetails:
    - https://pay.amazon.com/jp/developer/documentation/apireference/201752580

    Price:
    - https://pay.amazon.com/jp/developer/documentation/apireference/201752720

    Status:
    - https://pay.amazon.com/jp/developer/documentation/apireference/201752820
    '''

    @cached_property
    def client(self):
        return self.payauth.payorder.client

    @cached_property
    def latest(self):
        return self.get_last_call('get_capture_details', 'capture')

    def update_status(self, response):
        self.capture_id = _VR(response, 'AmazonCaptureId')
        self.state = _VR(response, 'CaptureStatus', 'State')
        self.amount = _VR(response, 'CaptureAmount', 'Amount')
        self.fee = _VR(response, 'CaptureFee', 'Amount')
        self.refund_amount = _VR(response, 'RefundedAmount', 'Amount')
        self.save()

    def capture(self):
        '''API
        https://pay.amazon.com/jp/developer/documentation/apireference/201752040
        '''
        request = dict(
            amazon_authorization_id=self.payauth.authorization_id,
            capture_reference_id=self.capture_number,
            capture_amount=self.amount)
        response = self.client.api.capture(**request)

        call = self.log_call('capture', request, response)

        # Update
        if response.success:
            self.update_status(response)

        return call

    def get_detail(self):
        '''API:GetCaptureDetails
        https://pay.amazon.com/jp/developer/documentation/apireference/201752060                # NOQA
        https://github.com/amzn/amazon-pay-sdk-python/blob/master/amazon_pay/client.py#L1169    # NOQA
        '''
        request = dict(amazon_capture_id=self.capture_id)
        response = self.client.api.get_capture_details(**request)
        call = self.log_call('get_capture_details', request, response)

        if response.success:
            self.update_status(response)

        return call

    def create_refund(
            self, amount=None, note=None, descriptor=None, refund_number=None):
        refund_number = refund_number or new_number('R')
        amount = amount or self.amount
        return self.payrefund_set.create(
            amount=self.amount,
            refund_number=refund_number, note=note, descriptor=descriptor)


class PayRefund(object):
    '''
    RefundDetails:
    - https://pay.amazon.com/jp/developer/documentation/apireference/201752740

    Price:
    - https://pay.amazon.com/jp/developer/documentation/apireference/201752720

    Status:
    - https://pay.amazon.com/jp/developer/documentation/apireference/201752820
    '''

    @cached_property
    def client(self):
        return self.paycapture.payauth.payorder.client

    @cached_property
    def latest(self):
        return self.get_last_call('get_refund_details')

    def refund(self):
        '''API : Refund
        https://pay.amazon.com/jp/developer/documentation/apireference/201752080
        https://github.com/amzn/amazon-pay-sdk-python/blob/master/amazon_pay/client.py#L1232
        '''
        request = dict(
            amazon_capture_id=self.paycapture.capture_id,
            refund_reference_id=self.refund_number,
            refund_amount=self.amount,
            seller_refund_note=self.note,
            soft_descriptor=self.descriptor)

        response = self.client.api.refund(**request)

        call = self.log_call('refund', request, response)

        # Update
        if response.success:
            self.refund_id = _VR(response, 'AmazonRefundId')
            self.amount = _VR(response, 'RefundAmount', 'Amount')
            self.fee = _VR(response, 'FeeRefunded', 'Amount')
            self.state = _VR(response, 'RefundStatus', 'State')
            self.save()

        return call

    def get_detail(self):
        '''API: GetRefundDetails
        https://github.com/amzn/amazon-pay-sdk-python/blob/master/amazon_pay/client.py#L1293    # NOQA
        '''
        request = dict(amazon_refund_id=self.refund_id)
        response = self.client.api.get_refund_details(**request)
        call = self.log_call('get_refund_details', request, response)

        if response.success:
            self.amount = _VR(response, 'RefundAmount', 'Amount')
            self.fee = _VR(response, 'FeeRefunded', 'Amount')
            self.state = _VR(response, 'RefundStatus', 'State')
            self.save()

        return call



class OrderObjectMixin(object):

    @cached_property
    def order_instance(self):
        ct = ContentType.objects.get_for_model(self)
        return {'order_content_type': ct.id, 'order_object_id': self.id}

    @cached_property
    def payorder(self):
        from .models import PayOrder
        return PayOrder.objects.find_for(self)

    def amzpay_request(self, **kwargs):
        return self.payorder.set_detail()

    def amzpay_confirm(self, **kwargs):
        self.payorder.confirm()
        return self.payorder.get_detail()

    def amzpay_autorize(self):
        return self.payorder.create_auth().authorize()


class PayCall(object):

    @cached_property
    def request_object(self):
        return encoders.from_json(self.request)

    @cached_property
    def response_object(self):
        return encoders.from_json(self.response)

    @cached_property
    def request_yaml(self):
        return encoders.to_yaml(
            self.request_object,
            allow_unicode=True, default_flow_style=False)

    @cached_property
    def response_yaml(self):
        return encoders.to_yaml(
            self.response_object,
            allow_unicode=True, default_flow_style=False)
