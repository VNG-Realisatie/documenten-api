from django.utils.translation import gettext_lazy as _

from drf_writable_nested import NestedCreateMixin, NestedUpdateMixin
from rest_framework import serializers
from vng_api_common.serializers import GegevensGroepSerializer, NestedGegevensGroepMixin
from vng_api_common.utils import get_help_text

from drc.api.fields import EnkelvoudigInformatieObjectHyperlinkedRelatedField
from drc.datamodel.models import Verzending
from drc.datamodel.models.enkelvoudig_informatieobject import (
    EnkelvoudigInformatieObject,
)


class BinnenlandsCorrespondentieadresVerzendingSerializer(GegevensGroepSerializer):
    class Meta:
        model = Verzending
        gegevensgroep = "binnenlands_correspondentieadres_verzending"


class BuitenlandsCorrespondentieadresVerzendingSerializer(GegevensGroepSerializer):
    class Meta:
        model = Verzending
        gegevensgroep = "buitenlands_correspondentieadres_verzending"


class BuitenlandsCorrespondentiepostadresVerzendingSerializer(GegevensGroepSerializer):
    class Meta:
        model = Verzending
        gegevensgroep = "buitenlands_correspondentiepostadres_verzending"


class VerzendingSerializer(
    NestedGegevensGroepMixin,
    NestedCreateMixin,
    NestedUpdateMixin,
    serializers.HyperlinkedModelSerializer,
):
    informatieobject = EnkelvoudigInformatieObjectHyperlinkedRelatedField(
        view_name="enkelvoudiginformatieobject-detail",
        lookup_field="uuid",
        queryset=EnkelvoudigInformatieObject.objects,
        help_text=get_help_text("datamodel.Verzending", "informatieobject"),
    )

    afwijkend_binnenlands_correspondentieadres_verzending = (
        BinnenlandsCorrespondentieadresVerzendingSerializer(
            required=False,
            help_text=_(
                "Het correspondentieadres, betreffende een adresseerbaar object,"
                " van de BETROKKENE, zijnde afzender of geadresseerde, zoals vermeld"
                " in het ontvangen of verzonden INFORMATIEOBJECT indien dat afwijkt"
                " van het reguliere binnenlandse correspondentieadres van BETROKKENE."
            ),
            source="binnenlands_correspondentieadres_verzending",
        )
    )

    afwijkend_buitenlands_correspondentieadres_verzending = (
        BuitenlandsCorrespondentieadresVerzendingSerializer(
            help_text=_(
                "De gegevens van het adres in het buitenland van BETROKKENE, zijnde"
                " afzender of geadresseerde, zoals vermeld in het ontvangen of"
                " verzonden INFORMATIEOBJECT en dat afwijkt van de reguliere"
                " correspondentiegegevens van BETROKKENE."
            ),
            source="buitenlands_correspondentieadres_verzending",
        )
    )

    afwijkend_correspondentie_posteadres_verzending = (
        BuitenlandsCorrespondentiepostadresVerzendingSerializer(
            help_text=_(
                "De gegevens die tezamen een postbusadres of antwoordnummeradres"
                " vormen van BETROKKENE, zijnde afzender of geadresseerde, zoals"
                " vermeld in het ontvangen of verzonden INFORMATIEOBJECT en dat"
                " afwijkt van de reguliere correspondentiegegevens van BETROKKENE."
            ),
            source="buitenlands_correspondentiepostadres_verzending",
        )
    )

    class Meta:
        model = Verzending
        fields = (
            "url",
            "betrokkene",
            "informatieobject",
            "aard_relatie",
            "toelichting",
            "ontvangstdatum",
            "verzenddatum",
            "contact_persoon",
            "contactpersoonnaam",
            "afwijkend_binnenlands_correspondentieadres_verzending",
            "afwijkend_buitenlands_correspondentieadres_verzending",
            "afwijkend_correspondentie_posteadres_verzending",
        )

        extra_kwargs = {
            "url": {"lookup_field": "uuid", "read_only": True},
        }
