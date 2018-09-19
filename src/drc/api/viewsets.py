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

    De URL naar het informatieobjecttype wordt gevalideerd op geldigheid.

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
    Beheer relatie tussen InformatieObject en ZAAK.

    create:
    Registreer een INFORMATIEOBJECT bij een ZAAK.

    retrieve:
    Geef de details van een OBJECTINFORMATIEOBJECT relatie.
    """
    queryset = ObjectInformatieObject.objects.all()
    serializer_class = ObjectInformatieObjectSerializer
    filter_class = ObjectInformatieObjectFilter
    lookup_field = 'uuid'
