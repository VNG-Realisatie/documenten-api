from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from vng_api_common.serializers import GegevensGroepSerializer

from drc.datamodel.models import Verzending


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


class VerzendingSerializer(serializers.HyperlinkedModelSerializer):
    binnenlands_correspondentieadres_verzending = (
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

    buitenlands_correspondentieadres_verzending = (
        BuitenlandsCorrespondentieadresVerzendingSerializer(
            help_text=_(
                "De gegevens van het adres in het buitenland van BETROKKENE, zijnde"
                " afzender of geadresseerde, zoals vermeld in het ontvangen of"
                " verzonden INFORMATIEOBJECT en dat afwijkt van de reguliere"
                " correspondentiegegevens van BETROKKENE."
            ),
        )
    )

    buitenlands_correspondentie_postadres_verzending = (
        BuitenlandsCorrespondentiepostadresVerzendingSerializer(
            help_text=_(
                "De gegevens die tezamen een postbusadres of antwoordnummeradres"
                " vormen van BETROKKENE, zijnde afzender of geadresseerde, zoals"
                " vermeld in het ontvangen of verzonden INFORMATIEOBJECT en dat"
                " afwijkt van de reguliere correspondentiegegevens van BETROKKENE."
            ),
        )
    )

    class Meta:
        model = Verzending
        fields = (
            "uuid",
            "aard_relatie",
            "toelichting",
            "ontvangstdatum",
            "verzenddatum",
            "contact_persoon"
            "contactpersoonnaam"
            "binnenlands_correspondentieadres_verzending"
            "buitenlands_correspondentieadres_verzending"
            "buitenlands_correspondentie_postadres_verzending",
        )
