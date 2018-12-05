import logging

from django.conf import settings
from django.contrib.sites.models import Site
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.urls import reverse

from zds_client import Client, extract_params, get_operation_url

from drc.datamodel.models import ObjectInformatieObject

logger = logging.getLogger(__name__)


class SyncError(Exception):
    pass


def sync_create(relation: ObjectInformatieObject):
    # build the URL of the informatieobject
    path = reverse('enkelvoudiginformatieobject-detail', kwargs={
        'version': settings.REST_FRAMEWORK['DEFAULT_VERSION'],
        'uuid': relation.informatieobject.uuid,
    })
    domain = Site.objects.get_current().domain
    protocol = 'https' if settings.IS_HTTPS else 'http'
    informatieobject_url = f'{protocol}://{domain}{path}'

    logger.info("Remote object: %s", relation.object)
    logger.info("Informatieobject: %s", informatieobject_url)

    # figure out which remote resource we need to interact with
    resource = f"{relation.object_type}informatieobject"
    client = Client.from_url(relation.object)

    try:
        pattern = get_operation_url(client.schema, f'{resource}_create', pattern_only=True)
    except ValueError as exc:
        raise SyncError("Could not determine remote operation") from exc

    # we enforce in the standard that it's a subresource so that we can do this.
    # The real resource URL is extracted from the ``openapi.yaml`` based on
    # the operation
    params = extract_params(f"{relation.object}/irrelevant", pattern)

    try:
        client.create(resource, {'informatieobject': informatieobject_url}, **params)
    except Exception as exc:
        logger.error("Could not create remote relation", exc_info=1)
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
