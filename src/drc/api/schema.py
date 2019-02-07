from django.conf import settings

from drf_yasg import openapi

description = """Een API om een documentregistratiecomponent te benaderen.

Een informatieobject is een digitaal document voorzien van meta-gegevens.
Informatieobjecten kunnen aan andere objecten zoals zaken en besluiten worden
gerelateerd (maar dat hoeft niet) en kunnen gebruiksrechten hebben.
Gebruiksrechten leggen voorwaarden op aan het gebruik van het informatieobject
(buiten raadpleging). Deze gebruiksrechten worden niet door de API gevalideerd
of gehandhaafd.

De typering van informatieobjecten is in de zaaktypecatalogus (ZTC)
ondergebracht in de vorm van informatieobjecttypen.

**Autorisatie**

Deze API vereist nog geen autorisatie. Je mag wel JWT-tokens gegenereerd door
de [token-tool](https://ref.tst.vng.cloud/tokens/) gebruiken - deze worden
voor nu genegeerd.

**Handige links**

* [Aan de slag](https://ref.tst.vng.cloud/ontwikkelaars/)
* ["Papieren" standaard](https://ref.tst.vng.cloud/standaard/)
"""

info = openapi.Info(
    title="Documentregistratiecomponent (drc) API",
    default_version=settings.API_VERSION,
    description=description,
    contact=openapi.Contact(
        email="support@maykinmedia.nl",
        url="https://github.com/VNG-Realisatie/gemma-zaken"
    ),
    license=openapi.License(name="EUPL 1.2"),
)
