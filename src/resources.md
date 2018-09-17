# Resources

Dit document beschrijft de (RGBZ-)objecttypen die als resources ontsloten
worden met de beschikbare attributen.


## EnkelvoudigInformatieObject

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_1.0/doc/objecttype/enkelvoudiginformatieobject)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| url |  | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| identificatie | Een binnen een gegeven context ondubbelzinnige referentie naar het INFORMATIEOBJECT. | string | nee | C​R​U​D |
| bronorganisatie | Het RSIN van de Niet-natuurlijk persoon zijnde de organisatie die het informatieobject heeft gecreëerd of heeft ontvangen en als eerste in een samenwerkingsketen heeft vastgelegd. | string | nee | C​R​U​D |
| creatiedatum | Een datum of een gebeurtenis in de levenscyclus van het INFORMATIEOBJECT. | string | ja | C​R​U​D |
| titel | De naam waaronder het INFORMATIEOBJECT formeel bekend is. | string | ja | C​R​U​D |
| vertrouwelijkaanduiding | Aanduiding van de mate waarin het INFORMATIEOBJECT voor de openbaarheid bestemd is. | string | nee | C​R​U​D |
| auteur | De persoon of organisatie die in de eerste plaats verantwoordelijk is voor het creëren van de inhoud van het INFORMATIEOBJECT. | string | ja | C​R​U​D |
| formaat | De code voor de wijze waarop de inhoud van het ENKELVOUDIG INFORMATIEOBJECT is vastgelegd in een computerbestand. | string | nee | C​R​U​D |
| taal | Een taal van de intellectuele inhoud van het ENKELVOUDIG INFORMATIEOBJECT. De waardes komen uit ISO 639-2/B | string | ja | C​R​U​D |
| inhoud |  | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| link | De URL waarmee de inhoud van het INFORMATIEOBJECT op te vragen is. | string | nee | C​R​U​D |
| beschrijving | Een generieke beschrijving van de inhoud van het INFORMATIEOBJECT. | string | nee | C​R​U​D |
| informatieobjecttype | URL naar de INFORMATIEOBJECTTYPE in het ZTC. | string | ja | C​R​U​D |

## ZaakInformatieObject

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_1.0/doc/objecttype/zaakinformatieobject)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| url |  | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| zaak | URL naar de ZAAK in het ZRC. | string | ja | C​R​U​D |
| informatieobject |  | string | ja | C​R​U​D |


* Create, Read, Update, Delete
