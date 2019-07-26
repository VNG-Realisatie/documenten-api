from django.conf import settings

from humanize import naturalsize
from drf_yasg import openapi

from .kanalen import KANAAL_DOCUMENTEN

min_upload_size = naturalsize(settings.MIN_UPLOAD_SIZE, binary=True)

description = f"""Een API om een documentregistratiecomponent (DRC) te benaderen.

In een documentregistratiecomponent worden INFORMATIEOBJECTen opgeslagen. Een
INFORMATIEOBJECT is een digitaal document voorzien van meta-gegevens.
INFORMATIEOBJECTen kunnen aan andere objecten zoals zaken en besluiten worden
gerelateerd (maar dat hoeft niet) en kunnen gebruiksrechten hebben.

GEBRUIKSRECHTEN leggen voorwaarden op aan het gebruik van het INFORMATIEOBJECT
(buiten raadpleging). Deze GEBRUIKSRECHTEN worden niet door de API gevalideerd
of gehandhaafd.

De typering van INFORMATIEOBJECTen is in de Catalogi API (ZTC) ondergebracht in
de vorm van INFORMATIEOBJECTTYPEn.

**Uploaden van bestanden**

Binnen deze API bestaan een aantal endpoints die binaire data ontvangen, al
dan niet base64-encoded. Webservers moeten op deze endpoints een minimale
request body size van {min_upload_size} ondersteunen. Dit omvat de JSON van de
metadata EN de base64-encoded bestandsdata. Hou hierbij rekening met de
overhead van base64, die ongeveer 33% bedraagt in worst-case scenario's. Dit
betekent dat bij een limiet van 4GB het bestand maximaal ongeveer 3GB groot
mag zijn.

**Afhankelijkheden**

Deze API is afhankelijk van:

* Catalogi API
* Notificaties API
* Autorisaties API *(optioneel)*
* Zaken API *(optioneel)*

**Autorisatie**

Deze API vereist autorisatie. Je kan de
[token-tool](https://zaken-auth.vng.cloud/) gebruiken om JWT-tokens te
genereren.

**Notificaties**

Deze API publiceert notificaties op het kanaal `{KANAAL_DOCUMENTEN.label}`.

**Handige links**

* [Documentatie](https://zaakgerichtwerken.vng.cloud/standaard)
* [Zaakgericht werken](https://zaakgerichtwerken.vng.cloud)
"""

info = openapi.Info(
    title=f"{settings.PROJECT_NAME} API",
    default_version=settings.API_VERSION,
    description=description,
    contact=openapi.Contact(
        email="standaarden.ondersteuning@vng.nl",
        url="https://zaakgerichtwerken.vng.cloud"
    ),
    license=openapi.License(
        name="EUPL 1.2",
        url='https://opensource.org/licenses/EUPL-1.2'
    ),
)
