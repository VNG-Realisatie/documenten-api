from collections import OrderedDict

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _

import requests
from rest_framework import serializers
from vng_api_common.models import APICredential
from vng_api_common.tests.urls import reverse

from drc.datamodel.validators import validate_status


class StatusValidator:
    """
    Wrap around drc.datamodel.validate_status to output the errors to the
    correct field.
    """

    def set_context(self, serializer):
        self.instance = getattr(serializer, 'instance', None)

    def __call__(self, attrs: dict):
        try:
            validate_status(
                status=attrs.get('status'),
                ontvangstdatum=attrs.get('ontvangstdatum'),
                instance=self.instance
            )
        except ValidationError as exc:
            raise serializers.ValidationError(exc.error_dict)


class ZaakInformatieObjectValidator:
    """
    Validate that the INFORMATIEOBJECT is already linked to the ZAAK in the ZRC.
    """
    message = _('Het informatieobject is in het ZRC nog niet gerelateerd aan deze zaak.')
    code = 'inconsistent-relation'

    def __call__(self, context: OrderedDict):
        object_url = context['object']
        informatieobject_uuid = str(context['informatieobject'].uuid)

        # Construct the url for the informatieobject
        path = reverse('enkelvoudiginformatieobject-detail', kwargs={
            'version': settings.REST_FRAMEWORK['DEFAULT_VERSION'],
            'uuid': informatieobject_uuid,
        })
        domain = Site.objects.get_current().domain
        protocol = 'https' if settings.IS_HTTPS else 'http'
        informatieobject_url = f'{protocol}://{domain}{path}'

        # dynamic so that it can be mocked in tests easily
        Client = import_string(settings.ZDS_CLIENT_CLASS)
        client = Client.from_url(object_url)
        client.auth = APICredential.get_auth(object_url)
        try:
            zios_for_zaak = client.list('zaakinformatieobject', query_params={
                'zaak': object_url,
                'informatieobject': informatieobject_url
            })
            zios = [zio for zio in zios_for_zaak if informatieobject_uuid in zio['informatieobject']]

        except requests.HTTPError as exc:
            raise serializers.ValidationError(
                exc.args[0],
                code='relation-validation-error'
            ) from exc

        if len(zios) == 0:
            raise serializers.ValidationError(self.message, code=self.code)

class InformatieObjectUniqueValidator:
    """
    Validate that the relation between the object and informatieobject does not
    exist yet in the DRC
    """
    message = _('The fields {field_names} must make a unique set.')
    code = 'unique'

    def __init__(self, remote_resource_field, field: str):
        self.remote_resource_field = remote_resource_field
        self.field = field

    def __call__(self, context: OrderedDict):
        object_url = context['object']
        informatieobject = context['informatieobject']

        # dynamic so that it can be mocked in tests easily
        Client = import_string(settings.ZDS_CLIENT_CLASS)
        client = Client.from_url(object_url)

        oios = informatieobject.objectinformatieobject_set.filter(object=object_url)

        if oios:
            raise serializers.ValidationError(
                self.message.format(
                    field_names=(self.remote_resource_field, self.field)),
                    code=self.code
            )
