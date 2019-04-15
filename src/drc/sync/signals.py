import logging
import requests

from django.conf import settings
from django.contrib.sites.models import Site
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.urls import reverse

from vng_api_common.models import APICredential
from zds_client import Client, extract_params, get_operation_url

from drc.datamodel.models import ObjectInformatieObject

logger = logging.getLogger(__name__)


class SyncError(Exception):
    pass


def sync(relation: ObjectInformatieObject, operation: str):
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
    client.auth = APICredential.get_auth(relation.object)

    try:
        pattern = get_operation_url(client.schema, f'{resource}_{operation}', pattern_only=True)
    except ValueError as exc:
        raise SyncError("Could not determine remote operation") from exc

    if operation == 'create':
        # we enforce in the standard that it's a subresource so that we can do this.
        # The real resource URL is extracted from the ``openapi.yaml`` based on
        # the operation
        params = extract_params(f"{relation.object}/irrelevant", pattern)
    elif operation == 'delete':
        # Retrieve the url of the relation between the object and the
        # InformatieObject that must be deleted
        response = requests.get(f"{relation.object}/informatieobjecten")
        for relatie in response.json():
            if str(relation.informatieobject.uuid) in relatie['informatieobject']:
                relation_url = relatie['url']
                break
        params = extract_params(f"{relation.object}/irrelevant/{relation_url}", pattern)

    try:
        operation_function = getattr(client, operation)
        if operation == 'create':
            operation_function(resource, {'informatieobject': informatieobject_url}, **params)
        elif operation == 'delete':
            operation_function(resource, **params)
    except Exception as exc:
        logger.error(f"Could not {operation} remote relation", exc_info=1)
        raise SyncError(f"Could not {operation} remote relation") from exc


def sync_create(relation: ObjectInformatieObject):
    sync(relation, 'create')


def sync_delete(relation: ObjectInformatieObject):
    sync(relation, 'delete')


@receiver([post_save, post_delete], sender=ObjectInformatieObject, dispatch_uid='sync.sync_informatieobject_relation')
def sync_informatieobject_relation(sender, instance: ObjectInformatieObject=None, **kwargs):
    signal = kwargs['signal']
    if signal is post_save and kwargs.get('created', False):
        sync_create(instance)
    elif signal is post_delete:
        sync_delete(instance)
