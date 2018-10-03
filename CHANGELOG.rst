===========
Wijzigingen
===========

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
