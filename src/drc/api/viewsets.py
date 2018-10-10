from rest_framework import mixins, viewsets

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


class ObjectInformatieObjectViewSet(mixins.CreateModelMixin,
                                    mixins.ListModelMixin,
                                    mixins.RetrieveModelMixin,
                                    viewsets.GenericViewSet):
    """
    Beheer relatie tussen InformatieObject en OBJECT.

    create:
    Registreer een INFORMATIEOBJECT bij een OBJECT.

    Er wordt gevalideerd op:
    - geldigheid informatieobject URL
    - geldigheid object URL
    - registratiedatum is verplicht indien het een object van het type ZAAK
      betreft
    - de registratiedatum mag niet in de toekomst liggen
    - de combinatie informatieobject en object moet uniek zijn

    Bij het aanmaken wordt ook in de bron van het OBJECT de gespiegelde
    relatie aangemaakt, echter zonder de relatie-informatie.

    Titel, beschrijving en registratiedatum worden genegeneerd als het om een
    object van het type BESLUIT gaat.

    retrieve:
    Geef de details van een OBJECTINFORMATIEOBJECT relatie.
    """
    queryset = ObjectInformatieObject.objects.all()
    serializer_class = ObjectInformatieObjectSerializer
    filter_class = ObjectInformatieObjectFilter
    lookup_field = 'uuid'
