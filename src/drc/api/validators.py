from collections import OrderedDict

from django.conf import settings
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _

from rest_framework import exceptions, serializers
from rest_framework.exceptions import ValidationError
from vng_api_common.models import APICredential
from vng_api_common.validators import ResourceValidator
from zds_client import ClientError

from drc.datamodel.models import ObjectInformatieObject
from drc.datamodel.validators import validate_status

from .auth import get_zrc_auth
from .utils import get_absolute_url


class OneAddressValidator:
    """
    Class to validate that only one address is send with each request and only one address is assiociated with each Verzending within the database.
    """

    def set_context(self, serializer):
        self.instance = getattr(serializer, "instance", None)

    def __call__(self, attrs: dict):
        self.set_attrs_addresses(attrs)
        empty_attrs = not any(
            (
                self.attrs_binnenlands_not_empty,
                self.attrs_buitenlands_not_empty,
                self.attrs_postadres_not_empty,
            )
        )

        invalid_amount = (
            sum(
                (
                    self.attrs_binnenlands_not_empty,
                    self.attrs_buitenlands_not_empty,
                    self.attrs_postadres_not_empty,
                )
            )
            != 1
        )

        if self.instance:
            self.set_instance_addresses()
            # attrs_instance_mismatch = sum([
            #     self.attrs_binnenlands_not_empty != self.instance_binnenlands_not_empty and not self.attrs_binnenlands_to_be_removed,
            #     self.attrs_postadres_not_empty != self.instance_postadres_not_empty and not self.attrs_postadres_to_be_removed,
            #     self.attrs_buitenlands_not_empty != self.instance_buitenlands_not_empty and not self.attrs_buitenlands_to_be_removed,
            # ])
            attrs_instance_mismatch = any(
                [
                    self.attrs_binnenlands_not_empty
                    != self.instance_binnenlands_not_empty,
                    self.attrs_postadres_not_empty != self.instance_postadres_not_empty,
                    self.attrs_buitenlands_not_empty
                    != self.instance_buitenlands_not_empty,
                ]
            )
            print(attrs)
            if empty_attrs:
                return

            if invalid_amount or attrs_instance_mismatch:
                self.raise_validation_error()

        elif attrs:
            if invalid_amount:
                self.raise_validation_error()

    def raise_validation_error(self):
        raise ValidationError(
            detail=_("Verzending must contain precisely one correspondentieadress"),
            code="invalid-address",
        )

    def check_content(self, gegevensgroep: dict) -> bool:
        return any(value for value in gegevensgroep.values())

    def set_attrs_addresses(self, attrs: dict):

        self.attrs_binnenlands_to_be_removed = (
            attrs.get("binnenlands_correspondentieadres", False) == {}
        )

        self.attrs_postadres_to_be_removed = (
            attrs.get("correspondentie_postadres", False) == {},
        )

        self.attrs_buitenlands_to_be_removed = (
            attrs.get("buitenlands_correspondentieadres", False) == {},
        )

        self.attrs_binnenlands_not_empty = self.check_content(
            attrs.get("binnenlands_correspondentieadres", {})
        )
        self.attrs_postadres_not_empty = self.check_content(
            attrs.get("correspondentie_postadres", {})
        )

        self.attrs_buitenlands_not_empty = self.check_content(
            attrs.get("buitenlands_correspondentieadres", {})
        )

    def set_instance_addresses(self):
        self.instance_binnenlands_not_empty = self.check_content(
            self.instance.binnenlands_correspondentieadres
        )
        self.instance_postadres_not_empty = self.check_content(
            self.instance.correspondentie_postadres
        )
        self.instance_buitenlands_not_empty = self.check_content(
            self.instance.buitenlands_correspondentieadres
        )


class StatusValidator:
    """
    Wrap around drc.datamodel.validate_status to output the errors to the
    correct field.
    """

    def set_context(self, serializer):
        self.instance = getattr(serializer, "instance", None)

    def __call__(self, attrs: dict):
        try:
            validate_status(
                status=attrs.get("status"),
                ontvangstdatum=attrs.get("ontvangstdatum"),
                instance=self.instance,
            )
        except ValidationError as exc:
            raise serializers.ValidationError(exc.error_dict)


class ObjectInformatieObjectValidator:
    """
    Validate that the INFORMATIEOBJECT is already linked to the OBJECT in the remote component.
    """

    message = _(
        "Het informatieobject is in het {component} nog niet gerelateerd aan het object."
    )
    code = "inconsistent-relation"

    def __call__(self, context: OrderedDict):
        object_url = context["object"]
        informatieobject_uuid = str(context["informatieobject"].latest_version.uuid)
        object_type = context["object_type"]

        informatieobject_url = get_absolute_url(
            "enkelvoudiginformatieobject-detail", uuid=informatieobject_uuid
        )

        # dynamic so that it can be mocked in tests easily
        Client = import_string(settings.ZDS_CLIENT_CLASS)
        client = Client.from_url(object_url)
        client.auth = APICredential.get_auth(object_url)
        try:
            if object_type == "zaak":
                resource = "zaakinformatieobject"
                component = "ZRC"
                oas_schema = settings.ZRC_API_SPEC
            elif object_type == "besluit":
                resource = "besluitinformatieobject"
                component = "BRC"
                oas_schema = settings.BRC_API_SPEC

            try:
                ResourceValidator(
                    object_type.capitalize(),
                    oas_schema,
                    get_auth=get_zrc_auth,
                    headers={"Accept-Crs": "EPSG:4326"},
                )(object_url)
            except exceptions.ValidationError as exc:
                raise serializers.ValidationError(
                    {"object": exc.detail}, code=ResourceValidator.code
                )

            oios = client.list(
                resource,
                query_params={
                    object_type: object_url,
                    "informatieobject": informatieobject_url,
                },
            )

        except ClientError as exc:
            raise serializers.ValidationError(
                exc.args[0], code="relation-validation-error"
            ) from exc

        if len(oios) == 0:
            raise serializers.ValidationError(
                self.message.format(component=component), code=self.code
            )


class RemoteRelationValidator:
    message = _(
        "The canonical remote relation still exists, this relation cannot be deleted."
    )
    code = "remote-relation-exists"

    def __call__(self, object_informatie_object: ObjectInformatieObject):
        object_url = object_informatie_object.object

        informatieobject_url = get_absolute_url(
            "enkelvoudiginformatieobject-detail",
            uuid=object_informatie_object.informatieobject.latest_version.uuid,
        )

        Client = import_string(settings.ZDS_CLIENT_CLASS)
        client = Client.from_url(object_url)
        client.auth = APICredential.get_auth(object_url)

        resource = f"{object_informatie_object.object_type}informatieobject"

        try:
            relations = client.list(
                resource,
                query_params={
                    object_informatie_object.object_type: object_url,
                    "informatieobject": informatieobject_url,
                },
            )
        except ClientError as exc:
            raise serializers.ValidationError(
                exc.args[0], code="relation-lookup-error"
            ) from exc

        if len(relations) >= 1:
            raise serializers.ValidationError(self.message, code=self.code)


class InformatieObjectUniqueValidator:
    """
    Validate that the relation between the object and informatieobject does not
    exist yet in the DRC
    """

    message = _("The fields {field_names} must make a unique set.")
    code = "unique"

    def __init__(self, remote_resource_field, field: str):
        self.remote_resource_field = remote_resource_field
        self.field = field

    def __call__(self, context: OrderedDict):
        object_url = context["object"]
        informatieobject = context["informatieobject"]

        oios = informatieobject.objectinformatieobject_set.filter(object=object_url)

        if oios:
            field_names = (self.remote_resource_field, self.field)
            raise serializers.ValidationError(
                detail=self.message.format(field_names=field_names), code=self.code
            )
