from django.conf import settings
from django.contrib.sites.models import Site
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.urls import reverse

from zds_client import Client

from drc.datamodel.models import ObjectInformatieObject


class SyncError(Exception):
    pass


def sync_create(relation: ObjectInformatieObject):
    resource = f"{relation.object_type}informatieobject"
    path = reverse('enkelvoudiginformatieobject-detail', kwargs={
        'version': settings.REST_FRAMEWORK['DEFAULT_VERSION'],
        'uuid': relation.informatieobject.uuid,
    })
    bits = [
        (settings.FORCE_SCRIPT_NAME or '').strip('/'),
        path.strip('/')
    ]
    full_path = '/'.join(bits)
    domain = Site.objects.get_current().domain

    client = Client.from_url(relation.object, settings.BASE_DIR)
    try:
        client.create(resource, {
            'informatieobject': f'https://{domain}/{full_path}'
        })
    except Exception as exc:
        raise SyncError("Could not create remote relation") from exc


def sync_delete(relation: ObjectInformatieObject):
    raise NotImplementedError


@receiver([post_save, post_delete], sender=ObjectInformatieObject, dispatch_uid='sync.sync_informatieobject_relation')
def sync_informatieobject_relation(sender, instance: ObjectInformatieObject=None, **kwargs):
    signal = kwargs['signal']
    if signal is post_save and kwargs.get('created', False):
        sync_create(instance)
    elif signal is post_delete:
        sync_delete(instance)
