===========
Wijzigingen
===========

1.0.0-rc1 (2019-07-18)
======================

Release candidate tag

* Bumped to vng-api-common 1.0.0
* Bumped version numbers to 1.0.0-rc
* Changed ``dut`` into ``nld`` for correct language identifier in tests
* Added ``EnkelvoudigInformatieObject.versie`` and
  ``EnkelvoudigInformatieObject.beginRegitratie`` attributes
* Fixed attibutes showing as snake_case in API docs instead of camelCase

0.17.0 (2019-07-15)
===================

More updates towards release candidate

* Updated docs
* Changed ``taal`` attribute into a 3-char string field instead of an enum
* Turned all enum values into ``snake_case`` for consistency between APIs
* Bumped to latest vng-api-common

0.16.0 (2019-07-11)
===================

Updates towards release candidate

* Use human readable auto-generated document identifications
* Improved admin usability
* Improved documentation of ``EnkelvoudigInformatieObject.inhoud`` attribute
* Build ``develop`` docker images for test environment
* Documented ``EnkelvoudigInformatieObject.formaat`` - needs to be a MIME-type
* Improved OAS consistency
* Added management command to migrate to new domains

Breaking changes
----------------

* Added pagination to ``EnkelvoudigInformatieObject`` list endpoint

0.15.4 (2019-07-02)
===================

Added more logging to debug SSL issues

0.15.3 (2019-07-02)
===================

Bugfixes

* Enabled /api/v1/callbacks webhook endpoint
* Fixed SSL detection behind reverse proxy, causing ZaakinformatieObject
  create to fail because of bad resource URLs

0.15.2 (2019-07-02)
===================

Added a data migration to handle the flattened ZTC urls.

0.15.1 (2019-07-01)
===================

Fixed bug in docker start script preventing fixtures from being loaded.

0.15.0 (2019-06-28)
===================

Small feature release

* Added ``EnkelvoudigInformatieObject.locked`` to indicate if an EIO is locked
  or not. This boolean is consumed by ZRC validation.
* Adapted tests for explicit OAS 3.x checks so that no OAS 2.x is served
  anymore

0.14.0 (2019-06-18)
===================

Second release towards release candidate

* Added support for a minimal plugin system
* Added versioning of ``EnkelvoudigInformatieObject``:
    * endpoints support ``versie`` and ``registratieOp`` querystring params
      (mutually exclusive)
    * if not provided, the most recent version is returned
* Update (API schema) translations

Breaking changes
----------------

* ``EnkelvoudigInformatieObject`` can no longer be deleted if there are still
  related ``ObjectInformatieObject`` instances.
* ``ObjectInformatieObject`` can no longer be deleted if the remote, canonical
  relation still exists. This means that you need to destroy
  ``ZaakInformatieObject``/``BesluitInformatieObject`` first, which triggers
  the destruction of ``ObjectInformatieObject`` and then finally you can destroy
  the ``EnkelvoudigInformatieObject``. Requires ZRC >= 0.17.0 and BRC >= 0.11.3

0.13.2 (2019-06-13)
===================

Small QoL fixes

* Added audit-trail related tests
* Added ability to load fixtures during startup
* Make sendfile backend configurable through envvar

0.13.1 (2019-06-05)
===================

Forgot to enable view-config view

0.13.0 (2019-06-05)
===================

First release towards a release candidate

* added ``download`` operation/endpoint to the API spec
* added authorization to the download of actual binary files
  (``EnkelvoudigInformatieObject.inhoud``)
* 🔒 replaced the file storage with private media storage
* Added locking and unlocking of documents
* Added unlock-override mechanism for administrators
* Updated to latest Django 2.2 (LTS)

Breaking changes
----------------

* ``ObjectInformatieObject`` is no longer the primary relation, it is now
  created by ZRC/BRC instead of directly by consumers
* ``ObjectInformatieObject`` no longer contains the relation information
  specific to the ``objectType``
* 🐋 Added nginx to the stack to facilitate sendfile download acceleration.
  Existing deployments directly connecting to uwsgi need to put nginx in front
* ``EnkelvoudingInformatieObject`` can no longer be updated (``patch``,
  ``put``) without providing a lock ID, requiring you to lock it *before*
  updating

0.12.1 (2019-05-22)
===================

Update API-spec - forgotten after 0.12.0

0.12.0 (2019-05-22)
===================

Authorizations V2 and audit trail release - breaking changes!

* Authorizations are checked against authorizations component (AC), use the
  token tool to configure these.
* Added scopes for actions/resources that were not protected yet
* Renamed scopes for consistency and brevity, the ``zds.scopes`` prefix is
  dropped.
* changed ``invalid-params`` to ``invalidParams`` in validation errors,
  following KP-API strategy
* Added audit trails on documents (``informatieobject``)
* Added unique-representation for resources
* Bumped dependency versions to latest security releases

0.11.0 (2019-04-18)
===================

Added filtering to ``EnkelvoudingInformatieObject`` resource

* Filter on ``bronorganisatie`` (RSIN)
* Filter on ``identificatie``

Both are exact matches.

0.10.0 (2019-04-16)
===================

API-lab release

* Improved homepage layout, using vng-api-common boilerplate
* Bumped to latest bugfix release of gemma-zds-client

Breaking changes
----------------

* Flattened the ``kenmerken`` in notifications sent from a list of objects with
  one key-value to a single object with multiple key-value pairs.
  Requires the NC to be at version 0.4.0 or higher.

  Old:

  .. code-block:: json

  {
    "kenmerken": [
      {"key1": "value1"},
      {"key2": "value2"},
    ]
  }

  New:

  .. code-block:: json

  {
    "kenmerken": {
      "key1": "value1",
      "key2": "value2",
    }
  }

* Removed the zds-schema compatibility. Upgrade to 0.9.1 first if you haven't
  done so yet.

0.9.1 (2019-04-04)
==================

vng-api-common notifications bugfixes

0.9.0 (2019-04-04)
==================

Feature release for notifications

New features
------------

* added notifications machinery. Configure the NC to use in the admin and then
  run ``python src/manage.py register_kanaal`` to register the notifications
  exchange and be able to publish events.
* added notifications documentation.

Breaking changes
----------------

* renamed ``EnkelvoudigInformatieObject.vertrouwelijkaanduiding`` to
  ``EnkelvoudigInformatieObject.vertrouwelijkheidaanduiding``
* replaced zds-schema with vng-api-common. Run
  ``python src/manage.py migrate_from_zds_schema`` on existing installs to
  complete the migration.

Misc
----

* added URL to EUPL 1.2 license in API spec
* added contributing guidelines
* removed some unused sample templates

0.8.3 (2019-03-05)
==================

Bugfix release

* Fixed #40 -- the required gemma-zds-client version had a bug leading to
  double slashes in generated URLs, thereby breaking the
  ``ObjectInformatieObject`` sync operation

0.8.2 (2019-03-05)
==================

Security release

* Bumped version of Django to latest security release

0.8.1 (2019-02-27)
==================

Fix operation -> scopes mapping

* Enforced required scopes
* Ensured scopes end up in OAS

0.8.0 (2019-02-27)
==================

Archiving feature release

* added support for ``DELETE`` requests to ``EnkelvoudigInformatieObject``
  resource
* added support for ``DELETE`` requests to ``ObjectInformatieObject`` resource

0.7.1 (2019-02-07)
==================

Documentation improvements

* #620 - improve API documentation
* Bump Django and zds-schema to new patch versions
* Ship non-api documentation in Docker image

0.7.0 (2019-01-30)
==================

API maturity release

* Attributes added (#549)
    * ``EnkelvoudingInformatieObject.bestandsomvang`` (read-only)
    * ``EnkelvoudingInformatieObject.bestandsnaam`` (NOT as a group attribute)
    * ``EnkelvoudingInformatieObject.integriteit`` as nested object, possible
      checksum algorithm values are defined in enum
    * ``EnkelvoudingInformatieObject.ontvangstdatum``
    * ``EnkelvoudingInformatieObject.verzenddatum``
    * ``EnkelvoudingInformatieObject.indicatieGebruiksrecht`` - values ``null``
      and ``false`` are writable, for ``true`` you need to leverage the
      ``Gebruiksrechten`` resource
    * ``EnkelvoudingInformatieObject.ondertekening`` as nested object
    * ``EnkelvoudingInformatieObject.status`` with business logic and interaction
      with ``ontvangstdatum``
* (Partial) updates enabled for ``EnkelvoudingInformatieObject``
* Added ``Gebruiksrechten`` resource with interaction on ``indicatieGebruiksrecht``
* Updated to latest zds-schema version

0.6.10 (2018-12-13)
===================

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
