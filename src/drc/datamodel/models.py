import logging
import uuid as _uuid

from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _

from vng_api_common.constants import ObjectTypes
from vng_api_common.descriptors import GegevensGroepType
from vng_api_common.fields import (
    LanguageField, RSINField, VertrouwelijkheidsAanduidingField
)
from vng_api_common.utils import request_object_attribute
from vng_api_common.validators import alphanumeric_excluding_diacritic

from .constants import (
    ChecksumAlgoritmes, OndertekeningSoorten, RelatieAarden, Statussen
)
from .query import InformatieobjectQuerySet, InformatieobjectRelatedQuerySet
from .validators import validate_status

logger = logging.getLogger(__name__)


class InformatieObject(models.Model):
    uuid = models.UUIDField(
        unique=True, default=_uuid.uuid4,
        help_text='Unieke resource identifier (UUID4)'
    )
    identificatie = models.CharField(
        max_length=40, validators=[alphanumeric_excluding_diacritic],
        default=_uuid.uuid4,
        help_text='Een binnen een gegeven context ondubbelzinnige referentie '
                  'naar het INFORMATIEOBJECT.'
    )
    bronorganisatie = RSINField(
        max_length=9,
        help_text='Het RSIN van de Niet-natuurlijk persoon zijnde de '
                  'organisatie die het informatieobject heeft gecreëerd of '
                  'heeft ontvangen en als eerste in een samenwerkingsketen '
                  'heeft vastgelegd.'
    )
    # TODO: change to read-only?
    creatiedatum = models.DateField(
        help_text='Een datum of een gebeurtenis in de levenscyclus van het '
                  'INFORMATIEOBJECT.'
    )
    titel = models.CharField(
        max_length=200,
        help_text='De naam waaronder het INFORMATIEOBJECT formeel bekend is.'
    )
    vertrouwelijkheidaanduiding = VertrouwelijkheidsAanduidingField(
        blank=True,
        help_text='Aanduiding van de mate waarin het INFORMATIEOBJECT voor de '
                  'openbaarheid bestemd is.'
    )
    auteur = models.CharField(
        max_length=200,
        help_text='De persoon of organisatie die in de eerste plaats '
                  'verantwoordelijk is voor het creëren van de inhoud van het '
                  'INFORMATIEOBJECT.'
    )
    status = models.CharField(
        _("status"), max_length=20, blank=True, choices=Statussen.choices,
        help_text=_("Aanduiding van de stand van zaken van een INFORMATIEOBJECT. "
                    "De waarden 'in bewerking' en 'ter vaststelling' komen niet "
                    "voor als het attribuut `ontvangstdatum` van een waarde is voorzien. "
                    "Wijziging van de Status in 'gearchiveerd' impliceert dat "
                    "het informatieobject een duurzaam, niet-wijzigbaar Formaat dient te hebben.")
    )
    beschrijving = models.TextField(
        max_length=1000, blank=True,
        help_text='Een generieke beschrijving van de inhoud van het '
                  'INFORMATIEOBJECT.'
    )
    ontvangstdatum = models.DateField(
        _("ontvangstdatum"), null=True, blank=True,
        help_text=_("De datum waarop het INFORMATIEOBJECT ontvangen is. Verplicht "
                    "te registreren voor INFORMATIEOBJECTen die van buiten de "
                    "zaakbehandelende organisatie(s) ontvangen zijn. "
                    "Ontvangst en verzending is voorbehouden aan documenten die "
                    "van of naar andere personen ontvangen of verzonden zijn "
                    "waarbij die personen niet deel uit maken van de behandeling "
                    "van de zaak waarin het document een rol speelt.")
    )
    verzenddatum = models.DateField(
        _("verzenddatum"), null=True, blank=True,
        help_text=_("De datum waarop het INFORMATIEOBJECT verzonden is, zoals "
                    "deze op het INFORMATIEOBJECT vermeld is. Dit geldt voor zowel "
                    "inkomende als uitgaande INFORMATIEOBJECTen. Eenzelfde "
                    "informatieobject kan niet tegelijk inkomend en uitgaand zijn. "
                    "Ontvangst en verzending is voorbehouden aan documenten die "
                    "van of naar andere personen ontvangen of verzonden zijn "
                    "waarbij die personen niet deel uit maken van de behandeling "
                    "van de zaak waarin het document een rol speelt.")
    )
    indicatie_gebruiksrecht = models.NullBooleanField(
        _("indicatie gebruiksrecht"), blank=True, default=None,
        help_text=_("Indicatie of er beperkingen gelden aangaande het gebruik van "
                    "het informatieobject anders dan raadpleging. Dit veld mag "
                    "'null' zijn om aan te geven dat de indicatie nog niet bekend is. "
                    "Als de indicatie gezet is, dan kan je de gebruiksrechten die "
                    "van toepassing zijn raadplegen via de `Gebruiksrechten` resource.")
    )

    # signing in some sort of way
    # TODO: De attribuutsoort mag niet van een waarde zijn voorzien
    # als de attribuutsoort ?Status? de waarde ?in bewerking?
    # of ?ter vaststelling? heeft.
    ondertekening_soort = models.CharField(
        _("ondertekeningsoort"), max_length=10, blank=True,
        choices=OndertekeningSoorten.choices,
        help_text=_("Aanduiding van de wijze van ondertekening van het INFORMATIEOBJECT")
    )
    ondertekening_datum = models.DateField(
        _("ondertekeningdatum"), blank=True, null=True,
        help_text=_("De datum waarop de ondertekening van het INFORMATIEOBJECT heeft plaatsgevonden.")
    )

    informatieobjecttype = models.URLField(
        help_text='URL naar de INFORMATIEOBJECTTYPE in het ZTC.'
    )

    objects = InformatieobjectQuerySet.as_manager()

    class Meta:
        verbose_name = 'informatieobject'
        verbose_name_plural = 'informatieobject'
        unique_together = ('bronorganisatie', 'identificatie')
        abstract = True

    def __str__(self) -> str:
        return self.identificatie

    def clean(self):
        super().clean()
        validate_status(status=self.status, ontvangstdatum=self.ontvangstdatum, instance=self)

    ondertekening = GegevensGroepType({
        'soort': ondertekening_soort,
        'datum': ondertekening_datum,
    })

    def unique_representation(self):
        return f"{self.bronorganisatie} - {self.identificatie}"


class EnkelvoudigInformatieObject(InformatieObject):
    # TODO: validate mime types
    formaat = models.CharField(
        max_length=255, blank=True,
        help_text='De code voor de wijze waarop de inhoud van het ENKELVOUDIG '
                  'INFORMATIEOBJECT is vastgelegd in een computerbestand.'
    )
    taal = LanguageField(
        help_text='Een taal van de intellectuele inhoud van het ENKELVOUDIG '
                  'INFORMATIEOBJECT. De waardes komen uit ISO 639-2/B'
    )

    bestandsnaam = models.CharField(
        _("bestandsnaam"), max_length=255, blank=True,
        help_text=_("De naam van het fysieke bestand waarin de inhoud van het "
                    "informatieobject is vastgelegd, inclusief extensie.")
    )
    inhoud = models.FileField(upload_to='uploads/%Y/%m/')
    link = models.URLField(
        max_length=200, blank=True,
        help_text='De URL waarmee de inhoud van het INFORMATIEOBJECT op te '
                  'vragen is.',
    )

    # these fields should not be modified directly, but go through the `integriteit` descriptor
    integriteit_algoritme = models.CharField(
        _("integriteit algoritme"), max_length=20,
        choices=ChecksumAlgoritmes.choices, blank=True,
        help_text=_("Aanduiding van algoritme, gebruikt om de checksum te maken.")
    )
    integriteit_waarde = models.CharField(
        _("integriteit waarde"), max_length=128, blank=True,
        help_text=_("De waarde van de checksum.")
    )
    integriteit_datum = models.DateField(
        _("integriteit datum"), null=True, blank=True,
        help_text=_("Datum waarop de checksum is gemaakt.")
    )

    integriteit = GegevensGroepType({
        'algoritme': integriteit_algoritme,
        'waarde': integriteit_waarde,
        'datum': integriteit_datum,
    })


class Gebruiksrechten(models.Model):
    uuid = models.UUIDField(
        unique=True, default=_uuid.uuid4,
        help_text="Unieke resource identifier (UUID4)"
    )
    informatieobject = models.ForeignKey('EnkelvoudigInformatieObject', on_delete=models.CASCADE)
    omschrijving_voorwaarden = models.TextField(
        _("omschrijving voorwaarden"),
        help_text=_("Omschrijving van de van toepassing zijnde voorwaarden aan "
                    "het gebruik anders dan raadpleging")
    )
    startdatum = models.DateTimeField(
        _("startdatum"),
        help_text=_("Begindatum van de periode waarin de gebruiksrechtvoorwaarden van toepassing zijn. "
                    "Doorgaans is de datum van creatie van het informatieobject de startdatum.")
    )
    einddatum = models.DateTimeField(
        _("startdatum"), blank=True, null=True,
        help_text=_("Einddatum van de periode waarin de gebruiksrechtvoorwaarden van toepassing zijn.")
    )

    objects = InformatieobjectRelatedQuerySet.as_manager()

    class Meta:
        verbose_name = _("gebruiksrecht informatieobject")
        verbose_name_plural = _("gebruiksrechten informatieobject")

    def __str__(self):
        return str(self.informatieobject)

    @transaction.atomic
    def save(self, *args, **kwargs):
        # ensure the indication is set properly on the IO
        if not self.informatieobject.indicatie_gebruiksrecht:
            self.informatieobject.indicatie_gebruiksrecht = True
            self.informatieobject.save()
        super().save(*args, **kwargs)

    @transaction.atomic
    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

        other_gebruiksrechten = self.informatieobject.gebruiksrechten_set.exclude(pk=self.pk)
        if not other_gebruiksrechten.exists():
            self.informatieobject.indicatie_gebruiksrecht = None
            self.informatieobject.save()

    def unique_representation(self):
        return f"({self.informatieobject.unique_representation()}) - {self.omschrijving_voorwaarden}"


class ObjectInformatieObject(models.Model):
    """
    Modelleer een INFORMATIEOBJECT horend bij een OBJECT.

    INFORMATIEOBJECTen zijn bestanden die in het DRC leven. Een collectie van
    (enkelvoudige) INFORMATIEOBJECTen wordt ook als 1 enkele resource ontsloten.
    """
    uuid = models.UUIDField(
        unique=True, default=_uuid.uuid4,
        help_text="Unieke resource identifier (UUID4)"
    )
    informatieobject = models.ForeignKey(
        'EnkelvoudigInformatieObject', on_delete=models.CASCADE
    )
    object = models.URLField(help_text="URL naar het gerelateerde OBJECT.")
    object_type = models.CharField(
        "objecttype", max_length=100,
        choices=ObjectTypes.choices
    )

    objects = InformatieobjectRelatedQuerySet.as_manager()

    class Meta:
        verbose_name = 'Zaakinformatieobject'
        verbose_name_plural = 'Zaakinformatieobjecten'
        unique_together = ('informatieobject', 'object')

    def __str__(self):
        return self.get_title()

    def get_title(self) -> str:
        if self.informatieobject:
            return self.informatieobject.titel

        return '(onbekende titel)'

    def unique_representation(self):
        if not hasattr(self, '_unique_representation'):
            io_id = request_object_attribute(self.object, 'identificatie', self.object_type)
            self._unique_representation = f"({self.informatieobject.unique_representation()}) - {io_id}"
        return self._unique_representation
