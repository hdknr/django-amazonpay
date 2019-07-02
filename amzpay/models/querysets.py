from django.db import models
from django.contrib.contenttypes.models import ContentType
from social_django.models import UserSocialAuth
from amzpay import encoders


class PayOrderQuerySet(models.QuerySet):

    def find_for_keys(self, order_content_type, order_object_id, order_reference_id):
        return self.filter(
            models.Q(order_reference_id=order_reference_id) |
            (models.Q(order_content_type=order_content_type) & models.Q(order_object_id=order_object_id))    # NOQA
        ).first()

    def find_for(self, order_object):
        ct = ContentType.objects.get_for_model(order_object)
        return self.filter(
            order_content_type=ct, order_object_id=order_object.id).first()

    def get_or_create_for(self, client, user,
                          order_object, order_reference_id, order_number):
        return self.find_for(order_object) or self.create(
            client=client,
            social=UserSocialAuth.objects.filter(user=user, provider='amazon').first(),  # NOQA
            order_object=order_object,
            order_reference_id=order_reference_id,
            order_number=order_number,
        )


class PayCallQuerySet(models.QuerySet):

    def create_for(self, parent, action, request_dict, response_obj):
        return self.create(
            content_object=parent, action=action,
            success=response_obj.success,
            request=encoders.to_json(request_dict),
            response=response_obj.to_json())
