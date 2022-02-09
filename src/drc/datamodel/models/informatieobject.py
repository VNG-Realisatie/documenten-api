from django.db import models
from django.utils.translation import ugettext_lazy as _

from vng_api_common.descriptors import GegevensGroepType
from vng_api_common.fields import RSINField, VertrouwelijkheidsAanduidingField
from vng_api_common.utils import generate_unique_identification
from vng_api_common.validators import alphanumeric_excluding_diacritic

from ..constants import OndertekeningSoorten, Statussen
from ..query import InformatieobjectQuerySet
from ..validators import validate_status


class InformatieObject(models.Model):
    identificatie = models.CharField(
        max_length=40,
        validators=[alphanumeric_excluding_diacritic],
        blank=True,
        default="",
        help_text="Een binnen een gegeven context ondubbelzinnige referentie "
        "naar het INFORMATIEOBJECT.",
    )
    bronorganisatie = RSINField(
        max_length=9,
        help_text="Het RSIN van de Niet-natuurlijk persoon zijnde de "
        "organisatie die het informatieobject heeft gecreëerd of "
        "heeft ontvangen en als eerste in een samenwerkingsketen "
        "heeft vastgelegd.",
    )
    # TODO: change to read-only?
    creatiedatum = models.DateField(
        help_text="Een datum of een gebeurtenis in de levenscyclus van het "
        "INFORMATIEOBJECT."
    )
    titel = models.CharField(
        max_length=200,
        help_text="De naam waaronder het INFORMATIEOBJECT formeel bekend is.",
    )
    vertrouwelijkheidaanduiding = VertrouwelijkheidsAanduidingField(
        blank=True,
        help_text="Aanduiding van de mate waarin het INFORMATIEOBJECT voor de "
        "openbaarheid bestemd is.",
    )
    auteur = models.CharField(
        max_length=200,
        help_text="De persoon of organisatie die in de eerste plaats "
        "verantwoordelijk is voor het creëren van de inhoud van het "
        "INFORMATIEOBJECT.",
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        blank=True,
        choices=Statussen.choices,
        help_text=_(
            "Aanduiding van de stand van zaken van een INFORMATIEOBJECT. "
            "De waarden 'in bewerking' en 'ter vaststelling' komen niet "
            "voor als het attribuut `ontvangstdatum` van een waarde is voorzien. "
            "Wijziging van de Status in 'gearchiveerd' impliceert dat "
            "het informatieobject een duurzaam, niet-wijzigbaar Formaat dient te hebben."
        ),
    )
    beschrijving = models.TextField(
        max_length=1000,
        blank=True,
        help_text="Een generieke beschrijving van de inhoud van het "
        "INFORMATIEOBJECT.",
    )
    ontvangstdatum = models.DateField(
        _("ontvangstdatum"),
        null=True,
        blank=True,
        help_text=_(
            "De datum waarop het INFORMATIEOBJECT ontvangen is. Verplicht "
            "te registreren voor INFORMATIEOBJECTen die van buiten de "
            "zaakbehandelende organisatie(s) ontvangen zijn. "
            "Ontvangst en verzending is voorbehouden aan documenten die "
            "van of naar andere personen ontvangen of verzonden zijn "
            "waarbij die personen niet deel uit maken van de behandeling "
            "van de zaak waarin het document een rol speelt."
        ),
    )
    verzenddatum = models.DateField(
        _("verzenddatum"),
        null=True,
        blank=True,
        help_text=_(
            "De datum waarop het INFORMATIEOBJECT verzonden is, zoals "
            "deze op het INFORMATIEOBJECT vermeld is. Dit geldt voor zowel "
            "inkomende als uitgaande INFORMATIEOBJECTen. Eenzelfde "
            "informatieobject kan niet tegelijk inkomend en uitgaand zijn. "
            "Ontvangst en verzending is voorbehouden aan documenten die "
            "van of naar andere personen ontvangen of verzonden zijn "
            "waarbij die personen niet deel uit maken van de behandeling "
            "van de zaak waarin het document een rol speelt."
        ),
    )
    indicatie_gebruiksrecht = models.NullBooleanField(
        _("indicatie gebruiksrecht"),
        blank=True,
        default=None,
        help_text=_(
            "Indicatie of er beperkingen gelden aangaande het gebruik van "
            "het informatieobject anders dan raadpleging. Dit veld mag "
            "`null` zijn om aan te geven dat de indicatie nog niet bekend is. "
            "Als de indicatie gezet is, dan kan je de gebruiksrechten die "
            "van toepassing zijn raadplegen via de GEBRUIKSRECHTen resource."
        ),
    )

    # signing in some sort of way
    # TODO: De attribuutsoort mag niet van een waarde zijn voorzien
    # als de attribuutsoort ?Status? de waarde ?in bewerking?
    # of ?ter vaststelling? heeft.
    ondertekening_soort = models.CharField(
        _("ondertekeningsoort"),
        max_length=10,
        blank=True,
        choices=OndertekeningSoorten.choices,
        help_text=_(
            "Aanduiding van de wijze van ondertekening van het INFORMATIEOBJECT"
        ),
    )
    ondertekening_datum = models.DateField(
        _("ondertekeningdatum"),
        blank=True,
        null=True,
        help_text=_(
            "De datum waarop de ondertekening van het INFORMATIEOBJECT heeft plaatsgevonden."
        ),
    )

    informatieobjecttype = models.URLField(
        help_text=_(
            "URL-referentie naar het INFORMATIEOBJECTTYPE (in de " "Catalogi API)."
        )
    )

    objects = InformatieobjectQuerySet.as_manager()

    IDENTIFICATIE_PREFIX = "DOCUMENT"

    class Meta:
        verbose_name = "informatieobject"
        verbose_name_plural = "informatieobject"
        unique_together = ("bronorganisatie", "identificatie")
        abstract = True

    def __str__(self) -> str:
        return self.identificatie

    def save(self, *args, **kwargs):
        if not self.identificatie:
            self.identificatie = generate_unique_identification(self, "creatiedatum")
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        validate_status(
            status=self.status, ontvangstdatum=self.ontvangstdatum, instance=self
        )

    ondertekening = GegevensGroepType(
        {"soort": ondertekening_soort, "datum": ondertekening_datum}
    )

    def unique_representation(self):
        return f"{self.bronorganisatie} - {self.identificatie}"
