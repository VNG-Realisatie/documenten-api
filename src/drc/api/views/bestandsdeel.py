from django.utils.translation import gettext as _

from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer
from rest_framework import serializers, viewsets
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
@extend_schema(
    responses={
        200: inline_serializer(
            name="CustomResponseForWriteOnlyFields",
            fields={
                "url": serializers.HyperlinkedIdentityField(
                    view_name="bestandsdeel_update"
                ),
                "lock": serializers.CharField(
                    help_text=BestandsDeelSerializer._declared_fields["lock"].help_text,
                ),
                "omvang": serializers.IntegerField(
                    help_text=BestandsDeel.omvang.field.help_text, required=False
                ),
                "inhoud": serializers.FileField(
                    help_text=BestandsDeel.inhoud.field.help_text, required=False
                ),
                "voltooid": serializers.BooleanField(
                    help_text=BestandsDeelSerializer.Meta.extra_kwargs["voltooid"][
                        "help_text"
                    ],
                    required=False,
                ),
                "volgnummer": serializers.IntegerField(
                    help_text=BestandsDeel.volgnummer.field.help_text, required=False
                ),
            },
        )
    }
)
class BestandsDeelViewSet(UpdateWithoutPartialMixin, viewsets.GenericViewSet):
    queryset = BestandsDeel.objects.all()
    serializer_class = BestandsDeelSerializer
    lookup_field = "uuid"
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (InformationObjectRelatedAuthScopesRequired,)
    required_scopes = {"update": SCOPE_DOCUMENTEN_BIJWERKEN}

    swagger_schema = BestandsDeelSchema
