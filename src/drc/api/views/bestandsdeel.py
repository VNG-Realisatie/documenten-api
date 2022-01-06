from rest_framework.parsers import FormParser, MultiPartParser

from drc.api.mixins import UpdateWithoutPartialMixin
from drc.api.permissions import InformationObjectRelatedAuthScopesRequired
from drc.api.scopes import SCOPE_DOCUMENTEN_BIJWERKEN
from drc.api.serializers import BestandsDeelSerializer
from drc.datamodel.models.bestandsdeel import BestandsDeel


class BestandsDeelViewSet(UpdateWithoutPartialMixin, viewsets.GenericViewSet):
    """
    update:
    Upload een bestandsdeel
    """

    queryset = BestandsDeel.objects.all()
    serializer_class = BestandsDeelSerializer
    lookup_field = "uuid"
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (InformationObjectRelatedAuthScopesRequired,)
    required_scopes = {"update": SCOPE_DOCUMENTEN_BIJWERKEN}
