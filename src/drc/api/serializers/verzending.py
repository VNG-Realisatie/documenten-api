from django.utils.translation import gettext_lazy as _

from drf_writable_nested import NestedCreateMixin, NestedUpdateMixin
from rest_framework import serializers
from vng_api_common.serializers import GegevensGroepSerializer, NestedGegevensGroepMixin
from vng_api_common.utils import get_help_text

from drc.api.fields import EnkelvoudigInformatieObjectHyperlinkedRelatedField
from drc.api.validators import OnlyOneAddressValidator
from drc.datamodel.models import Verzending
from drc.datamodel.models.enkelvoudig_informatieobject import (
    EnkelvoudigInformatieObject,
)


class BinnenlandsCorrespondentieadresVerzendingSerializer(GegevensGroepSerializer):
    class Meta:
        model = Verzending
        gegevensgroep = "binnenlands_correspondentieadres"


class BuitenlandsCorrespondentieadresVerzendingSerializer(GegevensGroepSerializer):
    class Meta:
        model = Verzending
        gegevensgroep = "buitenlands_correspondentieadres"


class BuitenlandsCorrespondentiepostadresVerzendingSerializer(GegevensGroepSerializer):
    class Meta:
        model = Verzending
        gegevensgroep = "correspondentie_postadres"


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

    binnenlands_correspondentieadres = (
        BinnenlandsCorrespondentieadresVerzendingSerializer(
            required=False,
            help_text=_(
                "Het correspondentieadres, betreffende een adresseerbaar object,"
                " van de BETROKKENE, zijnde afzender of geadresseerde, zoals vermeld"
                " in het ontvangen of verzonden INFORMATIEOBJECT indien dat afwijkt"
                " van het reguliere binnenlandse correspondentieadres van BETROKKENE."
            ),
        )
    )

    buitenlands_correspondentieadres = (
        BuitenlandsCorrespondentieadresVerzendingSerializer(
            required=False,
            help_text=_(
                "De gegevens van het adres in het buitenland van BETROKKENE, zijnde"
                " afzender of geadresseerde, zoals vermeld in het ontvangen of"
                " verzonden INFORMATIEOBJECT en dat afwijkt van de reguliere"
                " correspondentiegegevens van BETROKKENE."
            ),
        )
    )

    correspondentie_postadres = BuitenlandsCorrespondentiepostadresVerzendingSerializer(
        required=False,
        help_text=_(
            "De gegevens die tezamen een postbusadres of antwoordnummeradres"
            " vormen van BETROKKENE, zijnde afzender of geadresseerde, zoals"
            " vermeld in het ontvangen of verzonden INFORMATIEOBJECT en dat"
            " afwijkt van de reguliere correspondentiegegevens van BETROKKENE."
        ),
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
            "binnenlands_correspondentieadres",
            "buitenlands_correspondentieadres",
            "correspondentie_postadres",
        )

        extra_kwargs = {
            "url": {"lookup_field": "uuid", "read_only": True},
        }
        validators = [OnlyOneAddressValidator()]
