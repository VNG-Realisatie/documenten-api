from django.db import models

from zds_schema.validators import (
    alphanumeric_excluding_diacritic, validate_non_negative_string
)


class InformatieObject(models.Model):
    identificatie = models.CharField(
        max_length=40, help_text='Een binnen een gegeven context ondubbelzinnige referentie naar het INFORMATIEOBJECT.',
        validators=[alphanumeric_excluding_diacritic]
    )
    bronorganisatie = models.CharField(
        max_length=9, validators=[validate_non_negative_string],
        blank=True, help_text='Het RSIN van de Niet-natuurlijk persoon zijnde de organisatie die het informatieobject '
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
    taal = models.CharField(
        max_length=20, help_text='Een taal van de intellectuele inhoud van het ENKELVOUDIG INFORMATIEOBJECT'
    )

    inhoud = models.FileField(upload_to='uploads/%Y/%m/')


class ZaakInformatieObject(models.Model):
    """
    Modelleer een INFORMATIEOBJECT horend bij een ZAAK.

    INFORMATIEOBJECTen zijn bestanden die in het DRC leven. Een collectie van
    (enkelvoudige) INFORMATIEOBJECTen wordt ook als 1 enkele resource ontsloten.
    """
    informatieobject = models.ForeignKey('EnkelvoudigInformatieObject', on_delete=models.CASCADE)
    zaak = models.URLField(help_text="URL naar de ZAAK in het ZRC.")

    class Meta:
        verbose_name = 'Zaakinformatieobject'
        verbose_name_plural = 'Zaakinformatieobjecten'
