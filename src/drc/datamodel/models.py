import logging
import uuid as _uuid

from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _

from privates.fields import PrivateMediaFileField
from vng_api_common.caching import ETagMixin
from vng_api_common.constants import ObjectTypes
from vng_api_common.descriptors import GegevensGroepType
from vng_api_common.fields import RSINField, VertrouwelijkheidsAanduidingField
from vng_api_common.models import APIMixin
from vng_api_common.utils import (
    generate_unique_identification,
    request_object_attribute,
)
from vng_api_common.validators import alphanumeric_excluding_diacritic

from .constants import ChecksumAlgoritmes, OndertekeningSoorten, Statussen
from .query import InformatieobjectQuerySet, InformatieobjectRelatedQuerySet
from .validators import validate_status

logger = logging.getLogger(__name__)


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


class EnkelvoudigInformatieObjectCanonical(models.Model):
    """
    Indicates the identity of a document
    """

    lock = models.CharField(
        default="",
        blank=True,
        max_length=100,
        help_text=_("Hash string, which represents id of the lock"),
    )

    def __str__(self):
        return str(self.latest_version)

    @property
    def latest_version(self):
        versies = self.enkelvoudiginformatieobject_set.order_by("-versie")
        return versies.first()

    @property
    def complete_upload(self) -> bool:
        empty_parts = self.bestandsdelen.filter(inhoud="")
        return empty_parts.count() == 0

    @property
    def empty_bestandsdelen(self) -> bool:
        empty_parts = self.bestandsdelen.filter(inhoud="")
        return empty_parts.count() == self.bestandsdelen.count()


class EnkelvoudigInformatieObject(ETagMixin, APIMixin, InformatieObject):
    """
    Stores the content of a specific version of an
    EnkelvoudigInformatieObjectCanonical

    The model is split into two parts to support versioning, now a single
    `EnkelvoudigInformatieObjectCanonical` can exist with multiple different
    `EnkelvoudigInformatieObject`\s, which can be retrieved by filtering
    """

    canonical = models.ForeignKey(
        EnkelvoudigInformatieObjectCanonical, on_delete=models.CASCADE
    )
    uuid = models.UUIDField(
        default=_uuid.uuid4, help_text="Unieke resource identifier (UUID4)"
    )

    # NOTE: Don't validate but rely on externally maintened list of Media Types
    # and that consumers know what they're doing. This prevents updating the
    # API specification on every Media Type that is added.
    formaat = models.CharField(
        max_length=255,
        blank=True,
        help_text='Het "Media Type" (voorheen "MIME type") voor de wijze waarop'
        "de inhoud van het INFORMATIEOBJECT is vastgelegd in een "
        "computerbestand. Voorbeeld: `application/msword`. Zie: "
        "https://www.iana.org/assignments/media-types/media-types.xhtml",
    )
    taal = models.CharField(
        max_length=3,
        help_text="Een ISO 639-2/B taalcode waarin de inhoud van het "
        "INFORMATIEOBJECT is vastgelegd. Voorbeeld: `nld`. Zie: "
        "https://www.iso.org/standard/4767.html",
    )

    bestandsnaam = models.CharField(
        _("bestandsnaam"),
        max_length=255,
        blank=True,
        help_text=_(
            "De naam van het fysieke bestand waarin de inhoud van het "
            "informatieobject is vastgelegd, inclusief extensie."
        ),
    )
    bestandsomvang = models.PositiveIntegerField(
        _("bestandsomvang"),
        null=True,
        help_text=_("Aantal bytes dat de inhoud van INFORMATIEOBJECT in beslag neemt."),
    )

    inhoud = PrivateMediaFileField(upload_to="uploads/%Y/%m/")

    link = models.URLField(
        max_length=200,
        blank=True,
        help_text="De URL waarmee de inhoud van het INFORMATIEOBJECT op te "
        "vragen is.",
    )

    # these fields should not be modified directly, but go through the `integriteit` descriptor
    integriteit_algoritme = models.CharField(
        _("integriteit algoritme"),
        max_length=20,
        choices=ChecksumAlgoritmes.choices,
        blank=True,
        help_text=_("Aanduiding van algoritme, gebruikt om de checksum te maken."),
    )
    integriteit_waarde = models.CharField(
        _("integriteit waarde"),
        max_length=128,
        blank=True,
        help_text=_("De waarde van de checksum."),
    )
    integriteit_datum = models.DateField(
        _("integriteit datum"),
        null=True,
        blank=True,
        help_text=_("Datum waarop de checksum is gemaakt."),
    )

    integriteit = GegevensGroepType(
        {
            "algoritme": integriteit_algoritme,
            "waarde": integriteit_waarde,
            "datum": integriteit_datum,
        }
    )

    versie = models.PositiveIntegerField(
        default=1,
        help_text=_(
            "Het (automatische) versienummer van het INFORMATIEOBJECT. Deze begint bij 1 als het "
            "INFORMATIEOBJECT aangemaakt wordt."
        ),
    )
    begin_registratie = models.DateTimeField(
        auto_now=True,
        help_text=_(
            "Een datumtijd in ISO8601 formaat waarop deze versie van het INFORMATIEOBJECT is aangemaakt of "
            "gewijzigd."
        ),
    )

    class Meta:
        unique_together = ("uuid", "versie")


class Gebruiksrechten(ETagMixin, models.Model):
    uuid = models.UUIDField(
        unique=True, default=_uuid.uuid4, help_text="Unieke resource identifier (UUID4)"
    )
    informatieobject = models.ForeignKey(
        "EnkelvoudigInformatieObjectCanonical",
        on_delete=models.CASCADE,
        help_text="URL-referentie naar het INFORMATIEOBJECT.",
    )
    omschrijving_voorwaarden = models.TextField(
        _("omschrijving voorwaarden"),
        help_text=_(
            "Omschrijving van de van toepassing zijnde voorwaarden aan "
            "het gebruik anders dan raadpleging"
        ),
    )
    startdatum = models.DateTimeField(
        _("startdatum"),
        help_text=_(
            "Begindatum van de periode waarin de gebruiksrechtvoorwaarden van toepassing zijn. "
            "Doorgaans is de datum van creatie van het informatieobject de startdatum."
        ),
    )
    einddatum = models.DateTimeField(
        _("startdatum"),
        blank=True,
        null=True,
        help_text=_(
            "Einddatum van de periode waarin de gebruiksrechtvoorwaarden van toepassing zijn."
        ),
    )

    objects = InformatieobjectRelatedQuerySet.as_manager()

    class Meta:
        verbose_name = _("gebruiksrecht informatieobject")
        verbose_name_plural = _("gebruiksrechten informatieobject")

    def __str__(self):
        return str(self.informatieobject.latest_version)

    @transaction.atomic
    def save(self, *args, **kwargs):
        informatieobject_versie = self.informatieobject.latest_version
        # ensure the indication is set properly on the IO
        if not informatieobject_versie.indicatie_gebruiksrecht:
            informatieobject_versie.indicatie_gebruiksrecht = True
            informatieobject_versie.save()
        super().save(*args, **kwargs)

    @transaction.atomic
    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        informatieobject = self.informatieobject
        other_gebruiksrechten = informatieobject.gebruiksrechten_set.exclude(pk=self.pk)
        if not other_gebruiksrechten.exists():
            informatieobject_versie = self.informatieobject.latest_version
            informatieobject_versie.indicatie_gebruiksrecht = None
            informatieobject_versie.save()

    def unique_representation(self):
        informatieobject = self.informatieobject.latest_version
        return f"({informatieobject.unique_representation()}) - {self.omschrijving_voorwaarden}"


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
        "andere API)."
    )
    object_type = models.CharField(
        "objecttype",
        max_length=100,
        choices=ObjectTypes.choices,
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


class BestandsDeel(models.Model):
    uuid = models.UUIDField(
        unique=True, default=_uuid.uuid4, help_text="Unieke resource identifier (UUID4)"
    )
    informatieobject = models.ForeignKey(
        "EnkelvoudigInformatieObjectCanonical",
        on_delete=models.CASCADE,
        related_name="bestandsdelen",
    )
    volgnummer = models.PositiveIntegerField(
        help_text=_("Een volgnummer dat de volgorde van de bestandsdelen aangeeft.")
    )
    omvang = models.PositiveIntegerField(
        help_text=_("De grootte van dit specifieke bestandsdeel.")
    )
    inhoud = PrivateMediaFileField(
        upload_to="part-uploads/%Y/%m/",
        blank=True,
        help_text=_("De (binaire) bestandsinhoud van dit specifieke bestandsdeel."),
    )

    class Meta:
        verbose_name = "bestands deel"
        verbose_name_plural = "bestands delen"
        unique_together = ("informatieobject", "volgnummer")

    def unique_representation(self):
        return f"({self.informatieobject.latest_version.unique_representation()}) - {self.volgnummer}"

    @property
    def voltooid(self) -> bool:
        return bool(self.inhoud.name)
