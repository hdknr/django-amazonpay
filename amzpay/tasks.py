from django.dispatch import receiver
from django.db.models.signals import post_save
from . import models


@receiver(post_save, sender=models.Client)
def on_client_saved(sender, instance, created=False, **kwargs):
    if instance.is_default:
        models.Client.objects.exclude(id=instance.id).update(is_default=False)