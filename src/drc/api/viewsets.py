from rest_framework import mixins, viewsets
from zds_schema.decorators import action_description

from drc.datamodel.models import EnkelvoudigInformatieObject

from .serializers import EnkelvoudigInformatieObjectSerializer


@action_description('create', "Registreer een EnkelvoudigInformatieObject.")
@action_description('retrieve', "Geef de details van een EnkelvoudigInformatieObject.")
class EnkelvoudigInformatieObjectViewSet(mixins.CreateModelMixin,
                                         mixins.RetrieveModelMixin,
                                         viewsets.GenericViewSet):
    queryset = EnkelvoudigInformatieObject.objects.all()
    serializer_class = EnkelvoudigInformatieObjectSerializer
