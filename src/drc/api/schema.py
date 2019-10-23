from collections import OrderedDict

from django.conf import settings

from drf_yasg import openapi
from humanize import naturalsize
from rest_framework import status
from vng_api_common.inspectors.view import HTTP_STATUS_CODE_TITLES, AutoSchema
from vng_api_common.notifications.utils import notification_documentation
from vng_api_common.serializers import FoutSerializer

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

_Nieuw in 1.1.0_

Bestanden kunnen groter zijn dan de minimale die door providers
ondersteund moet worden. De consumer moet dan:

1. Het INFORMATIEOBJECT aanmaken in de API, waarbij de totale bestandsgrootte
   meegestuurd wordt en de inhoud leeggelaten wordt.
   De API antwoordt met een lijst van BESTANDSDEELen, elk met een volgnummer
   en bestandsgrootte. De API lockt tegelijkertijd het INFORMATIEOBJECT.
2. Het bestand opsplitsen: ieder BESTANDSDEEL moet de bestandsgrootte hebben
   zoals dit aangegeven werd in de response bij 1.
3. Voor elk stuk van het bestand de binaire data naar de overeenkomstige
   BESTANDSDEEL-url gestuurd worden, samen met het lock ID.
4. Het INFORMATIEOBJECT unlocken. De provider valideert op dat moment dat alle
   bestandsdelen correct opgestuurd werden, en voegt deze samen tot het
   resulterende bestand.

Het bijwerken van een INFORMATIEOBJECT heeft een gelijkaardig verloop.

De 1.0.x manier van uploaden is ook beschikbaar voor kleine(re) bestanden die
niet gesplitst hoeven te worden.

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

### Notificaties

{notification_documentation(KANAAL_DOCUMENTEN)}

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
        url="https://zaakgerichtwerken.vng.cloud",
    ),
    license=openapi.License(
        name="EUPL 1.2", url="https://opensource.org/licenses/EUPL-1.2"
    ),
)


class EIOAutoSchema(AutoSchema):
    """
    Add the HTTP 413 error response to the schema.

    This is only relevant for endpoints that support file uploads.
    """

    def _get_error_responses(self) -> OrderedDict:
        responses = super()._get_error_responses()

        if self.method not in ["POST", "PUT", "PATCH"]:
            return responses

        status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        fout_schema = self.serializer_to_schema(FoutSerializer())
        responses[status_code] = openapi.Response(
            description=HTTP_STATUS_CODE_TITLES.get(status_code, ""), schema=fout_schema
        )

        return responses
