# Resources

Dit document beschrijft de (RGBZ-)objecttypen die als resources ontsloten
worden met de beschikbare attributen.


## EnkelvoudigInformatieObject

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_1.0/doc/objecttype/enkelvoudiginformatieobject)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| url |  | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| identificatie | Een binnen een gegeven context ondubbelzinnige referentie naar het INFORMATIEOBJECT. | string | nee | C​R​U​D |
| bronorganisatie | Het RSIN van de Niet-natuurlijk persoon zijnde de organisatie die het informatieobject heeft gecreëerd of heeft ontvangen en als eerste in een samenwerkingsketen heeft vastgelegd. | string | ja | C​R​U​D |
| creatiedatum | Een datum of een gebeurtenis in de levenscyclus van het INFORMATIEOBJECT. | string | ja | C​R​U​D |
| titel | De naam waaronder het INFORMATIEOBJECT formeel bekend is. | string | ja | C​R​U​D |
| vertrouwelijkheidaanduiding | Aanduiding van de mate waarin het INFORMATIEOBJECT voor de openbaarheid bestemd is. | string | nee | C​R​U​D |
| auteur | De persoon of organisatie die in de eerste plaats verantwoordelijk is voor het creëren van de inhoud van het INFORMATIEOBJECT. | string | ja | C​R​U​D |
| status | Aanduiding van de stand van zaken van een INFORMATIEOBJECT. De waarden &#39;in bewerking&#39; en &#39;ter vaststelling&#39; komen niet voor als het attribuut `ontvangstdatum` van een waarde is voorzien. Wijziging van de Status in &#39;gearchiveerd&#39; impliceert dat het informatieobject een duurzaam, niet-wijzigbaar Formaat dient te hebben. | string | nee | C​R​U​D |
| formaat | De code voor de wijze waarop de inhoud van het ENKELVOUDIG INFORMATIEOBJECT is vastgelegd in een computerbestand. | string | nee | C​R​U​D |
| taal | Een taal van de intellectuele inhoud van het ENKELVOUDIG INFORMATIEOBJECT. De waardes komen uit ISO 639-2/B | string | ja | C​R​U​D |
| bestandsnaam | De naam van het fysieke bestand waarin de inhoud van het informatieobject is vastgelegd, inclusief extensie. | string | nee | C​R​U​D |
| inhoud |  | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| bestandsomvang |  | integer | nee | ~~C~~​R​~~U~~​~~D~~ |
| link | De URL waarmee de inhoud van het INFORMATIEOBJECT op te vragen is. | string | nee | C​R​U​D |
| beschrijving | Een generieke beschrijving van de inhoud van het INFORMATIEOBJECT. | string | nee | C​R​U​D |
| ontvangstdatum | De datum waarop het INFORMATIEOBJECT ontvangen is. Verplicht te registreren voor INFORMATIEOBJECTen die van buiten de zaakbehandelende organisatie(s) ontvangen zijn. Ontvangst en verzending is voorbehouden aan documenten die van of naar andere personen ontvangen of verzonden zijn waarbij die personen niet deel uit maken van de behandeling van de zaak waarin het document een rol speelt. | string | nee | C​R​U​D |
| verzenddatum | De datum waarop het INFORMATIEOBJECT verzonden is, zoals deze op het INFORMATIEOBJECT vermeld is. Dit geldt voor zowel inkomende als uitgaande INFORMATIEOBJECTen. Eenzelfde informatieobject kan niet tegelijk inkomend en uitgaand zijn. Ontvangst en verzending is voorbehouden aan documenten die van of naar andere personen ontvangen of verzonden zijn waarbij die personen niet deel uit maken van de behandeling van de zaak waarin het document een rol speelt. | string | nee | C​R​U​D |
| indicatieGebruiksrecht | Indicatie of er beperkingen gelden aangaande het gebruik van het informatieobject anders dan raadpleging. Dit veld mag &#39;null&#39; zijn om aan te geven dat de indicatie nog niet bekend is. Als de indicatie gezet is, dan kan je de gebruiksrechten die van toepassing zijn raadplegen via de `Gebruiksrechten` resource. | boolean | nee | C​R​U​D |
| informatieobjecttype | URL naar de INFORMATIEOBJECTTYPE in het ZTC. | string | ja | C​R​U​D |
| lock | Hash string, which represents id of the lock | string | nee | C​R​U​D |

## AuditTrail

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_1.0/doc/objecttype/audittrail)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| uuid | Unieke identificatie van de audit regel | string | nee | C​R​U​D |
| bron | De naam van het component waar de wijziging in is gedaan

De mapping van waarden naar weergave is als volgt:

* `AC` - Autorisatiecomponent
* `NRC` - Notificatierouteringcomponent
* `ZRC` - Zaakregistratiecomponent
* `ZTC` - Zaaktypecatalogus
* `DRC` - Documentregistratiecomponent
* `BRC` - Besluitregistratiecomponent | string | ja | C​R​U​D |
| applicatieId | Unieke identificatie van de applicatie, binnen de organisatie | string | nee | C​R​U​D |
| applicatieWeergave | Vriendelijke naam van de applicatie | string | nee | C​R​U​D |
| gebruikersId | Unieke identificatie van de gebruiker die binnen de organisatie herleid kan worden naar een persoon | string | nee | C​R​U​D |
| gebruikersWeergave | Vriendelijke naam van de gebruiker | string | nee | C​R​U​D |
| actie | De uitgevoerde handeling

De bekende waardes voor dit veld zijn hieronder aangegeven,                         maar andere waardes zijn ook toegestaan

De mapping van waarden naar weergave is als volgt:

* `create` - aangemaakt
* `list` - opgehaald
* `retrieve` - opgehaald
* `destroy` - verwijderd
* `update` - bijgewerkt
* `partial_update` - deels bijgewerkt | string | ja | C​R​U​D |
| actieWeergave | Vriendelijke naam van de actie | string | nee | C​R​U​D |
| resultaat | HTTP status code van de API response van de uitgevoerde handeling | integer | ja | C​R​U​D |
| hoofdObject | De URL naar het hoofdobject van een component | string | ja | C​R​U​D |
| resource | Het type resource waarop de actie gebeurde | string | ja | C​R​U​D |
| resourceUrl | De URL naar het object | string | ja | C​R​U​D |
| toelichting | Toelichting waarom de handeling is uitgevoerd | string | nee | C​R​U​D |
| aanmaakdatum | De datum waarop de handeling is gedaan | string | nee | ~~C~~​R​~~U~~​~~D~~ |

## Gebruiksrechten

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_1.0/doc/objecttype/gebruiksrechten)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| url |  | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| informatieobject |  | string | ja | C​R​U​D |
| startdatum | Begindatum van de periode waarin de gebruiksrechtvoorwaarden van toepassing zijn. Doorgaans is de datum van creatie van het informatieobject de startdatum. | string | ja | C​R​U​D |
| einddatum | Einddatum van de periode waarin de gebruiksrechtvoorwaarden van toepassing zijn. | string | nee | C​R​U​D |
| omschrijvingVoorwaarden | Omschrijving van de van toepassing zijnde voorwaarden aan het gebruik anders dan raadpleging | string | ja | C​R​U​D |

## ObjectInformatieObject

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_1.0/doc/objecttype/objectinformatieobject)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| url |  | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| informatieobject |  | string | ja | C​R​U​D |
| object | URL naar het gerelateerde OBJECT. | string | ja | C​R​U​D |
| objectType |  | string | ja | C​R​U​D |
| aardRelatieWeergave |  | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| titel | De naam waaronder het INFORMATIEOBJECT binnen het OBJECT bekend is. | string | nee | C​R​U​D |
| beschrijving | Een op het object gerichte beschrijving van de inhoud vanhet INFORMATIEOBJECT. | string | nee | C​R​U​D |
| registratiedatum | De datum waarop de behandelende organisatie het INFORMATIEOBJECT heeft geregistreerd bij het OBJECT. Geldige waardes zijn datumtijden gelegen op of voor de huidige datum en tijd. | string | nee | ~~C~~​R​~~U~~​~~D~~ |


* Create, Read, Update, Delete
