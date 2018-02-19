from django.db.models import Model, Q
from django.forms.models import model_to_dict
from rest_framework import serializers, fields
from social_django.models import UserSocialAuth
from functools import reduce
import operator
from . import models


class ClientSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Client
        exclude = ['mws_access_key', 'mws_secret_key', 'mws_auth_token',
                   'client_secret']


class PayOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.PayOrder
        exclude = ['social']


    def is_valid(self, raise_exception=False):
        res = super(PayOrderSerializer, self).is_valid(raise_exception=False)
        if not res:
            keys = dict(
                (key, self.initial_data.get(key, None))
                for key in ['order_content_type', 'order_object_id',
                            'reference_id', ])
            obj = keys and self.Meta.model.objects.find_for_keys(**keys)
            if obj:
                self.Meta.model.objects.filter(
                    id=obj.id).update(**self.initial_data)
                self._existing_instance = obj
                return True

        return res

    def save(self, **kwargs):
        request = self.context.get('request', None)
        social = request and request and UserSocialAuth.objects.filter(
                    user=request.user, provider='amazon').first()
        _existing_instance = getattr(self, '_existing_instance', None)

        if _existing_instance:
            self.instance = _existing_instance
            if self.instance.social != social:
                self.instance.save()
            return self.instance

        super(PayOrderSerializer, self).save(social=social, **kwargs)
