import uuid as _uuid

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from rest_framework.exceptions import APIException
from vng_api_common.caching.models import ETagMixin
from vng_api_common.descriptors import GegevensGroepType

from ..constants import AfzenderTypes, PostAdresTypes
from ..validators import validate_postal_code


# gebaseerd op https://www.gemmaonline.nl/index.php/Rgbz_2.0/doc/relatieklasse/verzending
class Verzending(ETagMixin, models.Model):
    uuid = models.UUIDField(
        unique=True,
        default=_uuid.uuid4,
        help_text="Unieke resource identifier (UUID4)",
    )

    betrokkene = models.URLField(
        _("betrokkene"),
        help_text=_(
            "URL-referentie naar de betrokkene waarvan het informatieobject is"
            " ontvangen of waaraan dit is verzonden."
        ),
    )

    informatieobject = models.ForeignKey(
        "EnkelvoudigInformatieObjectCanonical",
        verbose_name=_("informatieobject"),
        help_text=_(
            "URL-referentie naar het informatieobject dat is ontvangen of verzonden."
        ),
        on_delete=models.CASCADE,
        related_name="verzendingen",
    )

    aard_relatie = models.CharField(
        _("aard relatie"),
        max_length=255,
        choices=AfzenderTypes.choices,
        help_text=_(
            "Omschrijving van de aard van de relatie van de BETROKKENE tot het"
            " INFORMATIEOBJECT."
        ),
    )

    toelichting = models.CharField(
        _("toelichting"),
        max_length=200,
        help_text=_("Verduidelijking van de afzender- of geadresseerde-relatie."),
        blank=True,
    )

    ontvangstdatum = models.DateField(
        _("ontvangstdatum"),
        help_text=_(
            "De datum waarop het INFORMATIEOBJECT ontvangen is. Verplicht te"
            " registreren voor INFORMATIEOBJECTen die van buiten de zaakbehandelende"
            " organisatie(s) ontvangen zijn. Ontvangst en verzending is voorbehouden"
            " aan documenten die van of naar andere personen ontvangen of verzonden"
            " zijn waarbij die personen niet deel uit maken van de behandeling van"
            " de zaak waarin het document een rol speelt. Vervangt het gelijknamige"
            " attribuut uit Informatieobject. Verplicht gevuld wanneer aardRelatie"
            " de waarde 'afzender' heeft."
        ),
        blank=True,
        null=True,
    )

    verzenddatum = models.DateField(
        _("verzenddatum"),
        help_text=_(
            "De datum waarop het INFORMATIEOBJECT verzonden is, zoals deze"
            " op het INFORMATIEOBJECT vermeld is. Dit geldt voor zowel inkomende"
            " als uitgaande INFORMATIEOBJECTen. Eenzelfde informatieobject kan"
            " niet tegelijk inkomend en uitgaand zijn. Ontvangst en verzending"
            " is voorbehouden aan documenten die van of naar andere personen"
            " ontvangen of verzonden zijn waarbij die personen niet deel uit"
            " maken van de behandeling van de zaak waarin het document een rol"
            " speelt. Vervangt het gelijknamige attribuut uit Informatieobject."
            " Verplicht gevuld wanneer aardRelatie de waarde 'geadresseerde' heeft."
        ),
        blank=True,
        null=True,
    )

    contact_persoon = models.URLField(
        _("contactpersoon"),
        help_text=_(
            "URL-referentie naar de persoon die als aanspreekpunt fungeert voor"
            " de BETROKKENE inzake het ontvangen of verzonden INFORMATIEOBJECT."
        ),
        max_length=1000,
    )
    contactpersoonnaam = models.CharField(
        _("contactpersoonnaam"),
        help_text=_(
            "De opgemaakte naam van de persoon die als aanspreekpunt fungeert voor"
            "de BETROKKENE inzake het ontvangen of verzonden INFORMATIEOBJECT."
        ),
        max_length=40,
        blank=True,
    )

    binnenlands_correspondentieadres_huisletter = models.CharField(
        _("huisletter"),
        help_text=(
            "Een door of namens het bevoegd gemeentelijk orgaan ten aanzien van een"
            " adresseerbaar object toegekende toevoeging aan een huisnummer in de"
            " vorm van een alfanumeriek teken."
        ),
        max_length=1,
        blank=True,
    )
    binnenlands_correspondentieadres_huisnummer = models.PositiveIntegerField(
        _("huisnummer"),
        help_text=(
            "Een door of namens het bevoegd gemeentelijk orgaan ten aanzien van"
            " een adresseerbaar object toegekende nummering."
        ),
        validators=[MinValueValidator(1), MaxValueValidator(99999)],
        blank=True,
        null=True,
    )
    binnenlands_correspondentieadres_huisnummer_toevoeging = models.CharField(
        _("huisnummer toevoeging"),
        help_text=(
            "Een door of namens het bevoegd gemeentelijk orgaan ten aanzien van"
            " een adresseerbaar object toegekende nadere toevoeging aan een huisnummer"
            " of een combinatie van huisnummer en huisletter."
        ),
        max_length=4,
        blank=True,
    )
    binnenlands_correspondentieadres_naam_openbare_ruimte = models.CharField(
        _("naam openbare ruimte"),
        help_text=(
            "Een door het bevoegde gemeentelijke orgaan aan een GEMEENTELIJKE "
            " OPENBARE RUIMTE toegekende benaming."
        ),
        max_length=80,
        blank=True,
    )
    binnenlands_correspondentieadres_postcode = models.CharField(
        _("postcode"),
        max_length=6,
        validators=[validate_postal_code],
        help_text=_(
            "De door TNT Post vastgestelde code behorende bij een bepaalde combinatie"
            " van een naam van een woonplaats, naam van een openbare ruimte en een huisnummer."
        ),
        blank=True,
    )
    binnenlands_correspondentieadres_woonplaats = models.CharField(
        _("woonplaatsnaam"),
        help_text=(
            "De door het bevoegde gemeentelijke orgaan aan een WOONPLAATS toegekende"
            " benaming."
        ),
        max_length=80,
        blank=True,
    )
    binnenlands_correspondentieadres = GegevensGroepType(
        {
            "huisletter": binnenlands_correspondentieadres_huisletter,
            "huisnummer": binnenlands_correspondentieadres_huisnummer,
            "huisnummer_toevoeging": binnenlands_correspondentieadres_huisnummer_toevoeging,
            "naam_openbare_ruimte": binnenlands_correspondentieadres_naam_openbare_ruimte,
            "postcode": binnenlands_correspondentieadres_postcode,
            "woonplaatsnaam": binnenlands_correspondentieadres_woonplaats,
        },
        required=False,
        optional=(
            "huisletter",
            "huisnummer_toevoeging",
            "postcode",
        ),
    )

    buitenlands_correspondentieadres_adres_buitenland_1 = models.CharField(
        _("adres buitenland 1"),
        max_length=35,
        help_text=_(
            "Het eerste deel dat behoort bij het afwijkend buitenlandse correspondentieadres"
            " van de betrokkene in zijn/haar rol bij de zaak."
        ),
        blank=True,
    )
    buitenlands_correspondentieadres_adres_buitenland_2 = models.CharField(
        _("adres buitenland 2"),
        max_length=35,
        help_text=_(
            "Het tweede deel dat behoort bij het afwijkend buitenlandse correspondentieadres"
            " van de betrokkene in zijn/haar rol bij de zaak."
        ),
        blank=True,
    )
    buitenlands_correspondentieadres_adres_buitenland_3 = models.CharField(
        _("adres buitenland 3"),
        max_length=35,
        help_text=_(
            "Het derde deel dat behoort bij het afwijkend buitenlandse correspondentieadres"
            " van de betrokkene in zijn/haar rol bij de zaak."
        ),
        blank=True,
    )
    buitenlands_correspondentieadres_land_postadres = models.URLField(
        _("land postadres"),
        help_text=_(
            "Het LAND dat behoort bij het afwijkend buitenlandse correspondentieadres"
            " van de betrokkene in zijn/haar rol bij de zaak."
        ),
        blank=True,
    )
    buitenlands_correspondentieadres = GegevensGroepType(
        {
            "adres_buitenland_1": buitenlands_correspondentieadres_adres_buitenland_1,
            "adres_buitenland_2": buitenlands_correspondentieadres_adres_buitenland_2,
            "adres_buitenland_3": buitenlands_correspondentieadres_adres_buitenland_3,
            "land_postadres": buitenlands_correspondentieadres_land_postadres,
        },
        required=False,
        optional=(
            "adres_buitenland2",
            "adres_buitenland3",
        ),
    )

    buitenlands_correspondentiepostadres_postbus_of_antwoord_nummer = models.PositiveIntegerField(
        _("postbus-of antwoordnummer"),
        validators=[MinValueValidator(1), MaxValueValidator(9999)],
        help_text=_(
            "De numerieke aanduiding zoals deze door de Nederlandse PTT is vastgesteld"
            " voor postbusadressen en antwoordnummeradressen."
        ),
        blank=True,
        null=True,
    )
    buitenlands_correspondentiepostadres_postadres_postcode = models.CharField(
        _("postadres postcode"),
        max_length=6,
        validators=[validate_postal_code],
        help_text=_(
            "De officiële Nederlandse PTT codering, bestaande uit een numerieke"
            " woonplaatscode en een alfabetische lettercode."
        ),
        blank=True,
    )
    buitenlands_correspondentiepostadres_postadrestype = models.CharField(
        _("postadrestype"),
        max_length=255,
        choices=PostAdresTypes.choices,
        help_text=_("Aanduiding van het soort postadres."),
        blank=True,
    )
    buitenlands_correspondentiepostadres_woonplaats = models.CharField(
        _("woonplaatsnaam"),
        max_length=80,
        help_text=_(
            "De door het bevoegde gemeentelijke orgaan aan een WOONPLAATS toegekende"
            " benaming."
        ),
        blank=True,
    )
    correspondentie_postadres = GegevensGroepType(
        {
            "post_bus_of_antwoordnummer": buitenlands_correspondentiepostadres_postbus_of_antwoord_nummer,
            "postadres_postcode": buitenlands_correspondentiepostadres_postadres_postcode,
            "postadres_type": buitenlands_correspondentiepostadres_postadrestype,
            "woonplaatsnaam": buitenlands_correspondentiepostadres_woonplaats,
        },
        required=False,
    )

    def __str__(self):
        return _("Verzending %(uuid)s") % {"uuid": str(self.uuid)}

    class Meta:
        verbose_name = _("Verzending")
        verbose_name_plural = _("Verzendingen")

    def save(self, *args, **kwargs):
        if (
            sum(
                [
                    self.check_gegevensgroep_contains_content(
                        self.binnenlands_correspondentieadres
                    ),
                    self.check_gegevensgroep_contains_content(
                        self.correspondentie_postadres
                    ),
                    self.check_gegevensgroep_contains_content(
                        self.buitenlands_correspondentieadres
                    ),
                ]
            )
            != 1
            and self.id
        ):
            raise APIException(
                "verzending must contain precisely one correspondentieadres",
                code="invalid-amount",
            )
        super().save(*args, **kwargs)

    def check_gegevensgroep_contains_content(self, gegevensgroep):
        for value in gegevensgroep.values():
            if value != "" and value != None:
                return True
        return False
