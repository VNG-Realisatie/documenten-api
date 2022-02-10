import binascii
from base64 import b64decode

from django.core.exceptions import ValidationError
from django.utils.http import urlencode
from django.utils.translation import gettext_lazy as _

from drf_extra_fields.fields import Base64FileField
from privates.storages import PrivateMediaFileSystemStorage
from rest_framework import serializers
from rest_framework.reverse import reverse


class AnyFileType:
    def __contains__(self, item):
        return True


class AnyBase64File(Base64FileField):
    ALLOWED_TYPES = AnyFileType()

    def __init__(self, view_name: str = None, *args, **kwargs):
        self.view_name = view_name
        super().__init__(*args, **kwargs)

    def get_file_extension(self, filename, decoded_file):
        return "bin"

    def to_internal_value(self, base64_data):
        try:
            return super().to_internal_value(base64_data)
        except Exception:
            try:
                b64decode(base64_data)
            except binascii.Error as e:
                if str(e) == "Incorrect padding":
                    raise ValidationError(
                        _("The provided base64 data has incorrect padding"),
                        code="incorrect-base64-padding",
                    )
                raise ValidationError(str(e), code="invalid-base64")
            except TypeError as exc:
                raise ValidationError(str(exc))

    def to_representation(self, file):
        is_private_storage = isinstance(file.storage, PrivateMediaFileSystemStorage)

        if not is_private_storage or self.represent_in_base64:
            return super().to_representation(file)

        # if there is no associated file link is not returned
        try:
            file.file
        except ValueError:
            return None

        assert (
            self.view_name
        ), "You must pass the `view_name` kwarg for private media fields"

        model_instance = file.instance
        request = self.context.get("request")

        url_field = self.parent.fields["url"]
        lookup_field = url_field.lookup_field
        kwargs = {lookup_field: getattr(model_instance, lookup_field)}
        url = reverse(self.view_name, kwargs=kwargs, request=request)

        # Retrieve the correct version to construct the download url that
        # points to the content of that version
        instance = self.parent.instance
        # in case of pagination instance can be a list object
        if isinstance(instance, list):
            instance = instance[0]

        if hasattr(instance, "versie"):
            versie = instance.versie
        else:
            versie = instance.get(uuid=kwargs["uuid"]).versie
        query_string = urlencode({"versie": versie})
        return f"{url}?{query_string}"


class EnkelvoudigInformatieObjectHyperlinkedRelatedField(
    serializers.HyperlinkedRelatedField
):
    """
    Custom field to construct the url for models that have a ForeignKey to
    `EnkelvoudigInformatieObject`

    Needed because the canonical `EnkelvoudigInformatieObjectCanonical` no longer stores
    the uuid, but the `EnkelvoudigInformatieObject`\s related to it do
    store the uuid
    """

    def get_url(self, obj, view_name, request, format):
        obj_latest_version = obj.latest_version
        return super().get_url(obj_latest_version, view_name, request, format)

    def get_object(self, view_name, view_args, view_kwargs):
        lookup_value = view_kwargs[self.lookup_url_kwarg]
        lookup_kwargs = {self.lookup_field: lookup_value}
        try:
            return (
                self.get_queryset()
                .filter(**lookup_kwargs)
                .order_by("-versie")
                .first()
                .canonical
            )
        except (TypeError, AttributeError):
            self.fail("does_not_exist")
