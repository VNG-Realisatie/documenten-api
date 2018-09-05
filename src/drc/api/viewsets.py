from rest_framework import mixins, viewsets

from drc.datamodel.models import (
    EnkelvoudigInformatieObject, ZaakInformatieObject
)

from .filters import ZaakInformatieObjectFilter
from .serializers import (
    EnkelvoudigInformatieObjectSerializer, ZaakInformatieObjectSerializer
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


class ZaakInformatieObjectViewSet(mixins.CreateModelMixin,
                                  mixins.ListModelMixin,
                                  mixins.RetrieveModelMixin,
                                  viewsets.GenericViewSet):
    """
    Beheer relatie tussen InformatieObject en ZAAK.

    create:
    Registreer een INFORMATIEOBJECT bij een ZAAK.

    retrieve:
    Geef de details van een ZAAKINFORMATIEOBJECT relatie.
    """
    queryset = ZaakInformatieObject.objects.all()
    serializer_class = ZaakInformatieObjectSerializer
    filter_class = ZaakInformatieObjectFilter
    lookup_field = 'uuid'
