import uuid as _uuid

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from privates.fields import PrivateMediaFileField
from vng_api_common.caching import ETagMixin
from vng_api_common.descriptors import GegevensGroepType
from vng_api_common.models import APIMixin

from ..constants import ChecksumAlgoritmes
from .informatieobject import InformatieObject


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
        versies = self.enkelvoudiginformatieobject_set.order_by("-versie", "-pk")
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
        "INFORMATIEOBJECT is vastgelegd. Voorbeeld: `dut`. Zie: "
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
    bestandsomvang = models.BigIntegerField(
        _("bestandsomvang"),
        validators=[MinValueValidator(0)],
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
