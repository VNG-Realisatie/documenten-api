from django.utils.translation import gettext as _

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.parsers import FormParser, MultiPartParser

from drc.api.mixins import UpdateWithoutPartialMixin
from drc.api.permissions import InformationObjectRelatedAuthScopesRequired
from drc.api.schema import BestandsDeelSchema
from drc.api.scopes import SCOPE_DOCUMENTEN_BIJWERKEN
from drc.api.serializers import BestandsDeelSerializer
from drc.datamodel.models.bestandsdeel import BestandsDeel


@extend_schema_view(
    update=extend_schema(
        summary=_("Upload een bestandsdeel."),
    ),
)
class BestandsDeelViewSet(UpdateWithoutPartialMixin, viewsets.GenericViewSet):

    queryset = BestandsDeel.objects.all()
    serializer_class = BestandsDeelSerializer
    lookup_field = "uuid"
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (InformationObjectRelatedAuthScopesRequired,)
    required_scopes = {"update": SCOPE_DOCUMENTEN_BIJWERKEN}

    swagger_schema = BestandsDeelSchema
