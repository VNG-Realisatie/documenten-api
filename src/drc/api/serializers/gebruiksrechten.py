from rest_framework import serializers
from vng_api_common.utils import get_help_text
from vng_api_common.validators import IsImmutableValidator

from drc.api.fields import EnkelvoudigInformatieObjectHyperlinkedRelatedField
from drc.datamodel.models.enkelvoudig_informatieobject import (
    EnkelvoudigInformatieObject,
)
from drc.datamodel.models.gebruiksrechten import Gebruiksrechten


class GebruiksrechtenSerializer(serializers.HyperlinkedModelSerializer):
    informatieobject = EnkelvoudigInformatieObjectHyperlinkedRelatedField(
        view_name="enkelvoudiginformatieobject-detail",
        lookup_field="uuid",
        queryset=EnkelvoudigInformatieObject.objects,
        help_text=get_help_text("datamodel.Gebruiksrechten", "informatieobject"),
    )

    class Meta:
        model = Gebruiksrechten
        fields = (
            "url",
            "informatieobject",
            "startdatum",
            "einddatum",
            "omschrijving_voorwaarden",
        )
        extra_kwargs = {
            "url": {"lookup_field": "uuid"},
            "informatieobject": {"validators": [IsImmutableValidator()]},
        }
