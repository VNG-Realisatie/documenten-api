from rest_framework import mixins, viewsets
from zds_schema.viewsets import CheckQueryParamsMixin

from drc.datamodel.models import (
    EnkelvoudigInformatieObject, ObjectInformatieObject
)

from .filters import ObjectInformatieObjectFilter
from .serializers import (
    EnkelvoudigInformatieObjectSerializer, ObjectInformatieObjectSerializer
)


class EnkelvoudigInformatieObjectViewSet(mixins.CreateModelMixin,
                                         mixins.ListModelMixin,
                                         mixins.RetrieveModelMixin,
                                         viewsets.GenericViewSet):
    """
    EnkelvoudigInformatieObject resource.

    create:
    Registreer een EnkelvoudigInformatieObject.

    Er wordt gevalideerd op:
    - geldigheid informatieobjecttype URL

    retrieve:
    Geef de details van een EnkelvoudigInformatieObject.
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

    Er wordt gevalideerd op:
    - geldigheid informatieobject URL
    - geldigheid object URL
    - de combinatie informatieobject en object moet uniek zijn

    De registratiedatum wordt door het systeem op 'NU' gezet. De aard_relatie
    wordt ook door het systeem gezet.

    Bij het aanmaken wordt ook in de bron van het OBJECT de gespiegelde
    relatie aangemaakt, echter zonder de relatie-informatie.

    Titel, beschrijving en registratiedatum zijn enkel relevant als het om een
    object van het type ZAAK gaat (aard relatie "hoort bij").

    retrieve:
    Geef de details van een OBJECTINFORMATIEOBJECT relatie.

    update:
    Update een INFORMATIEOBJECT bij een OBJECT. Je mag enkel de gegevens
    van de relatie bewerken, en niet de relatie zelf aanpassen.

    Er wordt gevalideerd op:
    - informatieobject URL, object URL en objectType mogen niet veranderen

    Titel, beschrijving en registratiedatum zijn enkel relevant als het om een
    object van het type ZAAK gaat (aard relatie "hoort bij").
    """
    queryset = ObjectInformatieObject.objects.all()
    serializer_class = ObjectInformatieObjectSerializer
    filterset_class = ObjectInformatieObjectFilter
    lookup_field = 'uuid'
