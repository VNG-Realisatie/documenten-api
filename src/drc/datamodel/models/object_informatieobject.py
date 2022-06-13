import uuid as _uuid

from django.db import models

from vng_api_common.caching import ETagMixin
from vng_api_common.models import APIMixin
from vng_api_common.utils import request_object_attribute

from ..constants import ObjectInformatieObjectTypes
from ..query import InformatieobjectRelatedQuerySet


class ObjectInformatieObject(ETagMixin, APIMixin, models.Model):
    """
    Modelleer een INFORMATIEOBJECT horend bij een OBJECT.

    INFORMATIEOBJECTen zijn bestanden die in het DRC leven. Een collectie van
    (enkelvoudige) INFORMATIEOBJECTen wordt ook als 1 enkele resource ontsloten.
    """

    uuid = models.UUIDField(
        unique=True, default=_uuid.uuid4, help_text="Unieke resource identifier (UUID4)"
    )
    informatieobject = models.ForeignKey(
        "EnkelvoudigInformatieObjectCanonical",
        on_delete=models.CASCADE,
        help_text="URL-referentie naar het INFORMATIEOBJECT.",
    )
    object = models.URLField(
        help_text="URL-referentie naar het gerelateerde OBJECT (in deze of een "
        "andere API).",
        max_length=1000,
    )
    object_type = models.CharField(
        "objecttype",
        max_length=100,
        choices=ObjectInformatieObjectTypes.choices,
        help_text="Het type van het gerelateerde OBJECT.",
    )

    objects = InformatieobjectRelatedQuerySet.as_manager()

    class Meta:
        verbose_name = "Oobject-informatieobject"
        verbose_name_plural = "object-informatieobjecten"
        unique_together = ("informatieobject", "object")

    def __str__(self):
        return self.get_title()

    def get_title(self) -> str:
        if hasattr(self, "titel"):
            return self.titel

        if self.informatieobject_id:
            return self.informatieobject.latest_version.titel

        return "(onbekende titel)"

    def unique_representation(self):
        if not hasattr(self, "_unique_representation"):
            io_id = request_object_attribute(
                self.object, "identificatie", self.object_type
            )
            self._unique_representation = f"({self.informatieobject.latest_version.unique_representation()}) - {io_id}"
        return self._unique_representation
