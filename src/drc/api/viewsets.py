from rest_framework import mixins, viewsets
from zds_schema.viewsets import CheckQueryParamsMixin

from drc.datamodel.models import (
    EnkelvoudigInformatieObject, Gebruiksrechten, ObjectInformatieObject
)

from .filters import GebruiksrechtenFilter, ObjectInformatieObjectFilter
from .serializers import (
    EnkelvoudigInformatieObjectSerializer, GebruiksrechtenSerializer,
    ObjectInformatieObjectSerializer
)


class EnkelvoudigInformatieObjectViewSet(mixins.CreateModelMixin,
                                         mixins.ListModelMixin,
                                         mixins.RetrieveModelMixin,
                                         mixins.UpdateModelMixin,
                                         viewsets.GenericViewSet):
    """
    Ontsluit ENKELVOUDIG INFORMATIEOBJECTen.

    create:
    Registreer een ENKELVOUDIG INFORMATIEOBJECT.

    **Er wordt gevalideerd op**
    - geldigheid informatieobjecttype URL

    list:
    Geef een lijst van ENKELVOUDIGe INFORMATIEOBJECTen (=documenten).

    De objecten bevatten metadata over de documenten en de downloadlink naar
    de binary data.

    retrieve:
    Geef de details van een ENKELVOUDIG INFORMATIEOBJECT.

    Het object bevat metadata over het informatieobject en de downloadlink naar
    de binary data.

    update:
    Werk een ENKELVOUDIG INFORMATIEOBJECT bij door de volledige resource mee
    te sturen.

    **Er wordt gevalideerd op**
    - geldigheid informatieobjecttype URL

    *TODO*
    - valideer immutable attributes

    partial_update:
    Werk een ENKELVOUDIG INFORMATIEOBJECT bij door enkel de gewijzigde velden
    mee te sturen.

    **Er wordt gevalideerd op**
    - geldigheid informatieobjecttype URL

    *TODO*
    - valideer immutable attributes
    """
    queryset = EnkelvoudigInformatieObject.objects.all()
    serializer_class = EnkelvoudigInformatieObjectSerializer
    lookup_field = 'uuid'


class ObjectInformatieObjectViewSet(CheckQueryParamsMixin,
                                    mixins.CreateModelMixin,
                                    mixins.ListModelMixin,
                                    mixins.RetrieveModelMixin,
                                    mixins.UpdateModelMixin,
                                    viewsets.GenericViewSet):
    """
    Beheer relatie tussen InformatieObject en OBJECT.

    create:
    Registreer een INFORMATIEOBJECT bij een OBJECT. Er worden twee types van
    relaties met andere objecten gerealiseerd:

    * INFORMATIEOBJECT behoort bij [OBJECT] en
    * INFORMATIEOBJECT is vastlegging van [OBJECT].

    **Er wordt gevalideerd op**
    - geldigheid informatieobject URL
    - geldigheid object URL
    - de combinatie informatieobject en object moet uniek zijn

    **Opmerkingen**
    - De registratiedatum wordt door het systeem op 'NU' gezet. De `aardRelatie`
      wordt ook door het systeem gezet.
    - Bij het aanmaken wordt ook in de bron van het OBJECT de gespiegelde
      relatie aangemaakt, echter zonder de relatie-informatie.
    - Titel, beschrijving en registratiedatum zijn enkel relevant als het om een
      object van het type ZAAK gaat (aard relatie "hoort bij").

    list:
    Geef een lijst van relaties tussen INFORMATIEOBJECTen en andere OBJECTen.

    Deze lijst kan gefilterd wordt met querystringparameters.

    retrieve:
    Geef de details van een relatie tussen een INFORMATIEOBJECT en een ander
    OBJECT.

    update:
    Update een INFORMATIEOBJECT bij een OBJECT. Je mag enkel de gegevens
    van de relatie bewerken, en niet de relatie zelf aanpassen.

    **Er wordt gevalideerd op**
    - informatieobject URL, object URL en objectType mogen niet veranderen

    Titel, beschrijving en registratiedatum zijn enkel relevant als het om een
    object van het type ZAAK gaat (aard relatie "hoort bij").

    partial_update:
    Update een INFORMATIEOBJECT bij een OBJECT. Je mag enkel de gegevens
    van de relatie bewerken, en niet de relatie zelf aanpassen.

    **Er wordt gevalideerd op**
    - informatieobject URL, object URL en objectType mogen niet veranderen

    Titel, beschrijving en registratiedatum zijn enkel relevant als het om een
    object van het type ZAAK gaat (aard relatie "hoort bij").
    """
    queryset = ObjectInformatieObject.objects.all()
    serializer_class = ObjectInformatieObjectSerializer
    filterset_class = ObjectInformatieObjectFilter
    lookup_field = 'uuid'


class GebruiksrechtenViewSet(viewsets.ModelViewSet):
    """
    list:
    Geef een lijst van gebruiksrechten horend bij informatieobjecten.

    Er kan gefiltered worden met querystringparameters.

    retrieve:
    Haal de details op van een gebruiksrecht van een informatieobject.

    create:
    Voeg gebruiksrechten toe voor een informatieobject.

    **Opmerkingen**
    - Het toevoegen van gebruiksrechten zorgt ervoor dat de
      `indicatieGebruiksrecht` op het informatieobject op `true` gezet wordt.

    update:
    Werk een gebruiksrecht van een informatieobject bij.

    partial_update:
    Werk een gebruiksrecht van een informatieobject bij.

    destroy:
    Verwijder een gebruiksrecht van een informatieobject.

    **Opmerkingen**
    - Indien het laatste gebruiksrecht van een informatieobject verwijderd wordt,
      dan wordt de `indicatieGebruiksrecht` van het informatieobject op `null`
      gezet.
    """
    queryset = Gebruiksrechten.objects.all()
    serializer_class = GebruiksrechtenSerializer
    filterset_class = GebruiksrechtenFilter
    lookup_field = 'uuid'
