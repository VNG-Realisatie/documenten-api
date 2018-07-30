import uuid as _uuid

from django.db import models

from zds_schema.fields import LanguageField, RSINField
from zds_schema.validators import alphanumeric_excluding_diacritic


class InformatieObject(models.Model):
    uuid = models.UUIDField(
        unique=True, default=_uuid.uuid4,
        help_text="Unieke resource identifier (UUID4)"
    )
    identificatie = models.CharField(
        max_length=40, help_text='Een binnen een gegeven context ondubbelzinnige referentie naar het INFORMATIEOBJECT.',
        validators=[alphanumeric_excluding_diacritic], default=_uuid.uuid4
    )
    bronorganisatie = RSINField(
        max_length=9, blank=True,
        help_text='Het RSIN van de Niet-natuurlijk persoon zijnde de organisatie die het informatieobject '
                  'heeft gecreëerd of heeft ontvangen en als eerste in een samenwerkingsketen heeft '
                  'vastgelegd.'
    )

    creatiedatum = models.DateField(
        help_text='Een datum of een gebeurtenis in de levenscyclus van het INFORMATIEOBJECT.'
    )
    titel = models.CharField(
        max_length=200, help_text='De naam waaronder het INFORMATIEOBJECT formeel bekend is.'
    )
    auteur = models.CharField(
        max_length=200, help_text='De persoon of organisatie die in de eerste plaats verantwoordelijk '
                                  'is voor het creëren van de inhoud van het INFORMATIEOBJECT.'
    )

    class Meta:
        verbose_name = 'informatieobject'
        verbose_name_plural = 'informatieobject'
        abstract = True

    def __str__(self) -> str:
        return self.identificatie


class EnkelvoudigInformatieObject(InformatieObject):
    formaat = models.CharField(
        max_length=255, blank=True,
        help_text='De code voor de wijze waarop de inhoud van het ENKELVOUDIG '
                  'INFORMATIEOBJECT is vastgelegd in een computerbestand.'
    )
    taal = LanguageField(help_text='Een taal van de intellectuele inhoud van het ENKELVOUDIG INFORMATIEOBJECT')

    inhoud = models.FileField(upload_to='uploads/%Y/%m/')


class ZaakInformatieObject(models.Model):
    """
    Modelleer een INFORMATIEOBJECT horend bij een ZAAK.

    INFORMATIEOBJECTen zijn bestanden die in het DRC leven. Een collectie van
    (enkelvoudige) INFORMATIEOBJECTen wordt ook als 1 enkele resource ontsloten.
    """
    uuid = models.UUIDField(
        unique=True, default=_uuid.uuid4,
        help_text="Unieke resource identifier (UUID4)"
    )
    informatieobject = models.ForeignKey('EnkelvoudigInformatieObject', on_delete=models.CASCADE)
    zaak = models.URLField(help_text="URL naar de ZAAK in het ZRC.")

    class Meta:
        verbose_name = 'Zaakinformatieobject'
        verbose_name_plural = 'Zaakinformatieobjecten'
