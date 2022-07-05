## Notificaties
## Berichtkenmerken voor Documenten API

Kanalen worden typisch per component gedefinieerd. Producers versturen berichten op bepaalde kanalen,
consumers ontvangen deze. Consumers abonneren zich via een notificatiecomponent (zoals <a href="https://notificaties-api.vng.cloud/api/v1/schema/" rel="nofollow">https://notificaties-api.vng.cloud/api/v1/schema/</a>) op berichten.

Hieronder staan de kanalen beschreven die door deze component gebruikt worden, met de kenmerken bij elk bericht.

De architectuur van de notificaties staat beschreven op <a href="https://github.com/VNG-Realisatie/notificaties-api" rel="nofollow">https://github.com/VNG-Realisatie/notificaties-api</a>.


### documenten

**Kanaal**
`documenten`

**Main resource**

`enkelvoudiginformatieobject`



**Kenmerken**

* `bronorganisatie`: Het RSIN van de Niet-natuurlijk persoon zijnde de organisatie die het informatieobject heeft gecreëerd of heeft ontvangen en als eerste in een samenwerkingsketen heeft vastgelegd.
* `informatieobjecttype`: URL-referentie naar het INFORMATIEOBJECTTYPE (in de Catalogi API).
* `vertrouwelijkheidaanduiding`: Aanduiding van de mate waarin het INFORMATIEOBJECT voor de openbaarheid bestemd is.

**Resources en acties**


* <code>enkelvoudiginformatieobject</code>: create, update, destroy

* <code>gebruiksrechten</code>: create, update, destroy, create, update, destroy


