import uuid as _uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from zds_schema.constants import ObjectTypes
from zds_schema.fields import (
    LanguageField, RSINField, VertrouwelijkheidsAanduidingField
)
from zds_schema.validators import alphanumeric_excluding_diacritic

from .constants import ChecksumAlgoritmes, RelatieAarden


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
    creatiedatum = models.DateField(
        help_text='Een datum of een gebeurtenis in de levenscyclus van het '
                  'INFORMATIEOBJECT.'
    )
    titel = models.CharField(
        max_length=200,
        help_text='De naam waaronder het INFORMATIEOBJECT formeel bekend is.'
    )
    vertrouwelijkaanduiding = VertrouwelijkheidsAanduidingField(
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
    beschrijving = models.TextField(
        max_length=1000, blank=True,
        help_text='Een generieke beschrijving van de inhoud van het '
                  'INFORMATIEOBJECT.'
    )

    informatieobjecttype = models.URLField(
        help_text='URL naar de INFORMATIEOBJECTTYPE in het ZTC.'
    )

    class Meta:
        verbose_name = 'informatieobject'
        verbose_name_plural = 'informatieobject'
        abstract = True

    def __str__(self) -> str:
        return self.identificatie


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

    def _get_integriteit(self):
        return {
            'algoritme': self.integriteit_algoritme,
            'waarde': self.integriteit_waarde,
            'datum': self.integriteit_datum,
        }

    def _set_integriteit(self, integrity: dict):
        # it may be empty
        if not integrity:
            self.integriteit_algoritme = ''
            self.integriteit_waarde = ''
            self.integriteit_datum = None
            return

        self.integriteit_algoritme = integrity['algoritme']
        self.integriteit_waarde = integrity['waarde']
        self.integriteit_datum = integrity['datum']

        assert self.integriteit_algoritme, "Empty algorithm not allowed"
        assert self.integriteit_waarde, "Empty checksum value not allowed"
        assert self.integriteit_datum, "Empty date not allowed"

    integriteit = property(_get_integriteit, _set_integriteit)


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
    aard_relatie = models.CharField(
        "aard relatie", max_length=20,
        choices=RelatieAarden.choices
    )

    # relatiegegevens
    titel = models.CharField(
        "titel", max_length=200, blank=True,
        help_text="De naam waaronder het INFORMATIEOBJECT binnen het OBJECT bekend is."
    )
    beschrijving = models.TextField(
        "beschrijving", blank=True,
        help_text="Een op het object gerichte beschrijving van de inhoud van"
                  "het INFORMATIEOBJECT."
    )
    registratiedatum = models.DateTimeField(
        "registratiedatum", auto_now_add=True,
        help_text="De datum waarop de behandelende organisatie het "
                  "INFORMATIEOBJECT heeft geregistreerd bij het OBJECT. "
                  "Geldige waardes zijn datumtijden gelegen op of voor de "
                  "huidige datum en tijd."
    )

    class Meta:
        verbose_name = 'Zaakinformatieobject'
        verbose_name_plural = 'Zaakinformatieobjecten'
        unique_together = ('informatieobject', 'object')

    def __str__(self):
        return self.get_title()

    def save(self, *args, **kwargs):
        # override to set aard_relatie
        self.aard_relatie = RelatieAarden.from_object_type(self.object_type)
        super().save(*args, **kwargs)

    def get_title(self) -> str:
        if self.titel:
            return self.titel

        if self.informatieobject_id:
            return self.informatieobject.titel

        return '(onbekende titel)'
