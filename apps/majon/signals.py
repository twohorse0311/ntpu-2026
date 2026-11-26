from django.db import transaction
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .cache import invalidate_room_list
from .models import Room


def invalidate_after_commit(owner_ids):
    owner_ids = {owner_id for owner_id in owner_ids if owner_id is not None}
    transaction.on_commit(lambda: [invalidate_room_list(owner_id) for owner_id in owner_ids])


@receiver(pre_save, sender=Room, dispatch_uid="majon.room.capture_previous_owner")
def capture_previous_owner(sender, instance, **kwargs):
    if not instance.pk:
        instance._previous_owner_id = None
        return
    instance._previous_owner_id = sender.objects.filter(pk=instance.pk).values_list(
        "owner_id", flat=True
    ).first()


@receiver(post_save, sender=Room, dispatch_uid="majon.room.invalidate_saved_list")
def invalidate_saved_room_list(sender, instance, **kwargs):
    invalidate_after_commit({getattr(instance, "_previous_owner_id", None), instance.owner_id})


@receiver(post_delete, sender=Room, dispatch_uid="majon.room.invalidate_deleted_list")
def invalidate_deleted_room_list(sender, instance, **kwargs):
    invalidate_after_commit({instance.owner_id})
