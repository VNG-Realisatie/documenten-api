===========
Wijzigingen
===========

0.6.10 (2018-12-13)
==================

Bump Django and urllib

* urllib3<=1.22 has a CVE
* use latest patch release of Django 2.0

0.6.9 (2018-12-11)
==================

Small bugfixes

* Fixed validator using newer gemma-zds-client
* Fixed reverting the ``ObjectInformatieObject`` creation if the remote relation
  cannot be created to prevent inconsistency
* Fixed url-to-object resolution in filter params when hosted on a subpath
* Fixed validation of mismatching ``object`` and ``objectType`` when relating
  a document to an object
* Added a name for the session cookie to preserve sessions on the same domain
  between components.
* Added missing Api-Version header
* Added missing Location header to OAS


0.6.0 (2018-11-27)
==================

Stap naar volwassenere API

* Update naar recente zds-schema versie
* HTTP 400 errors op onbekende/invalide filter-parameters
* Docker container beter te customizen via environment variables

Breaking change
---------------

De ``Authorization`` headers is veranderd van formaat. In plaats van ``<jwt>``
is het nu ``Bearer <jwt>`` geworden.

0.5.3 (2018-11-26)
==================

Updated to zds-schema 0.14.0 to handle JWT decoding issues properly

0.5.2 (2018-11-22)
==================

DSO API-srategie fix

Foutberichten bevatten een ``type`` key. De waarde van deze key begint niet
langer incorrect met ``"URI: "``.


0.5.1 (2018-11-21)
==================

Fix missing auth configuration from 0.5.0

0.5.0 (2018-11-21)
==================

Autorisatie-feature release

* Maak authenticated calls naar ZTC en ZRC
* Voeg JWT client/secret management toe
* Opzet credentialstore om URLs te kunnen valideren met auth/autz
* Support toevoegd om direct OAS 3.0 te serven op
  ``http://localhost:8000/api/v1/schema/openapi.yaml?v=3``. Zonder querystring
  parameter krijg je Swagger 2.0.

0.4.5 (2018-11-16)
==================

Added CORS-headers

0.4.4 (2018-11-05)
==================

Toevoeging van ``aardRelatie`` aan ``ObjectInformatieObject`` resource

* ``aardRelatie`` (``hoort_bij``, ``legt_vast``) toegevoegd
* implementatie waarbij ``aardRelatie`` gezet wordt op basis van ``objectType``

0.3.3 (2018-10-24)
==================

Tweaks aan ``ObjectInformatieObject`` resource

* ``registratiedatum`` wordt door het systeem gegenereerd en is read-only
* wijzigen van relatie (``object``, ``informatieobject`` en ``objectType``) is
  niet toegestaan

0.3.2 (2018-10-23)
==================

Fix openapi schema

* Onderscheid tussen request body & response body is nu duidelijk

0.3.1 (2018-10-19)
==================

Fixes in omgang met informatieobjectrelaties

* Serializer aangepast naar runtime gedrag. De relatie informatieobject-besluit
  heeft geen relatiegegevens. Deze worden nu ook genegeerd.
* Update van ZDS-client met betere logging.
* Nieuwe setting/envvar ``IS_HTTPS`` om URL-constructie van eigen resources
  robuuster te maken. Dit was voordien gebaseerd op de ``DEBUG`` setting.
* Concurrency in application server ingeschakeld


0.3.0 (2018-10-03)
==================

Herwerking van informatieobjectrelaties.

* Mogelijke foutantwoorden in OAS 3.0 spec opgenomen
* Validatie toegevoegd op ``informatieobjecttype`` URL
* Licentie toegevoegd (Boris van Hoytema <boris@publiccode.net>)
* Datamodel & API aangepast op generieke relatie tussen ``InformatieObject``
  en gerelateerd object (zie hieronder)
* Synchronisatie-actie gebouwd van DRC naar xRC zodat de relatie aan beide
  kanten bekend is.

**De volgende aanpassingen zijn backwards-incompatible**:

* endpoints ``/zaakinformatieobjecten/...`` zijn verdwenen en vervangen door
  ``/objectinformatieobjecten``
* ``registratiedatum`` is een nieuw, verplicht veld bij een
  ``ObjectInformatieObject``
* ``objectType`` is een nieuw, verplicht veld bij een ``ObjectInformatieObject``


0.2.3 (2018-08-20)
==================

Uitbreiding API spec

* verduidelijking oorsprong taal enum (ISO 639-2/B)
* ``InformatieObject`` velden toegevoegd:
    * ``link``
    * ``beschrijving``
    * ``informatieobjecttype``
* Filter toegevoegd aan ``ZaakInformatieObject`` voor zaak en informatieobject

0.2.2 (2018-08-15)
==================

OAS 3.0 spec bijgewerkt voor VNG-Realisatie/gemma-zaken#169

* toevoeging van vertrouwelijkheidsaanduidding
* standardisering van formaat om taal te specificeren

0.2.1 (2018-07-25)
==================

LIST operations toegevoegd aan DRC

* ``GET /api/v1/enkelvoudige-informatieobjecten`` geeft nu een lijst van
  resources terug
* ``GET /api/v1/zaakinformatieobjecten`` geeft nu een lijst van resources
  terug

Daarnaast is er ook een schema validator toegevoegd.

0.2.0 (2018-07-25)
==================

Gebruik UUIDs in de API urls in plaats van database primary keys

0.1.6 (2018-07-04)
==================

* Dev tooling
* Documentation update
* Project hygiene improved
