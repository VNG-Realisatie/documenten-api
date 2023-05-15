from django.utils.translation import gettext as _

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, serializers, viewsets
from rest_framework.settings import api_settings
from vng_api_common.caching.decorators import conditional_retrieve
from vng_api_common.viewsets import CheckQueryParamsMixin

from drc.api.data_filtering import ListFilterByAuthorizationsMixin
from drc.api.filters import ObjectInformatieObjectFilter
from drc.api.exclusions import ExpansionMixin
from drc.api.permissions import InformationObjectRelatedAuthScopesRequired
from drc.api.scopes import (
    SCOPE_DOCUMENTEN_AANMAKEN,
    SCOPE_DOCUMENTEN_ALLES_LEZEN,
    SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN,
    SCOPE_DOCUMENTEN_BIJWERKEN,
)
from drc.api.serializers import ObjectInformatieObjectSerializer
from drc.api.validators import RemoteRelationValidator
from drc.datamodel.models.object_informatieobject import ObjectInformatieObject


@conditional_retrieve()
@extend_schema_view(
    list=extend_schema(
        summary=_("Alle OBJECT-INFORMATIEOBJECT relaties opvragen."),
        description=_(" Deze lijst kan gefilterd wordt met query-string parameters."),
    ),
    retrieve=extend_schema(
        summary=_("Een specifieke OBJECT-INFORMATIEOBJECT relatie opvragen."),
        description=_("Een specifieke OBJECT-INFORMATIEOBJECT relatie opvragen."),
    ),
    create=extend_schema(
        summary=_("Maak een OBJECT-INFORMATIEOBJECT relatie aan."),
        description=_(
            "**LET OP: Dit endpoint hoor je als consumer niet zelf aan te spreken.**"
            " Andere API's, zoals de Zaken API en de Besluiten API, gebruiken dit"
            " endpoint bij het synchroniseren van relaties."
            " **Er wordt gevalideerd op**"
            " - geldigheid `informatieobject` URL"
            " - de combinatie `informatieobject` en `object` moet uniek zijn"
            " - bestaan van `object` URL"
        ),
    ),
    destroy=extend_schema(
        summary=_("Verwijder een OBJECT-INFORMATIEOBJECT relatie."),
        description=_(
            "**LET OP: Dit endpoint hoor je als consumer niet zelf aan te spreken.**"
            " Andere API's, zoals de Zaken API en de Besluiten API, gebruiken dit"
            " endpoint bij het synchroniseren van relaties."
        ),
    ),
)
class ObjectInformatieObjectViewSet(
    CheckQueryParamsMixin,
    ListFilterByAuthorizationsMixin,
    ExpansionMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.ReadOnlyModelViewSet,
):
    global_description = _(
        "Opvragen en verwijderen van OBJECT-INFORMATIEOBJECT relaties. Het betreft een relatie tussen een willekeurig OBJECT, bijvoorbeeld een ZAAK in de Zaken API, en een INFORMATIEOBJECT."
    )

    queryset = ObjectInformatieObject.objects.all()
    serializer_class = ObjectInformatieObjectSerializer
    filterset_class = ObjectInformatieObjectFilter
    lookup_field = "uuid"
    permission_classes = (InformationObjectRelatedAuthScopesRequired,)
    required_scopes = {
        "list": SCOPE_DOCUMENTEN_ALLES_LEZEN,
        "retrieve": SCOPE_DOCUMENTEN_ALLES_LEZEN,
        "create": SCOPE_DOCUMENTEN_AANMAKEN,
        "destroy": SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN,
        "update": SCOPE_DOCUMENTEN_BIJWERKEN,
        "partial_update": SCOPE_DOCUMENTEN_BIJWERKEN,
    }

    def perform_destroy(self, instance):
        # destroy is only allowed if the remote relation does no longer exist, so check for that
        validator = RemoteRelationValidator()

        try:
            validator(instance)
        except serializers.ValidationError as exc:
            raise serializers.ValidationError(
                {api_settings.NON_FIELD_ERRORS_KEY: exc}, code=exc.detail[0].code
            )
        else:
            super().perform_destroy(instance)
