from django.utils.translation import gettext as _

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from vng_api_common.caching.decorators import conditional_retrieve
from vng_api_common.viewsets import CheckQueryParamsMixin

from drc.api.filters import VerzendingFilter
from drc.api.exclusions import ExpansionMixin
from drc.api.scopes import (
    SCOPE_DOCUMENTEN_AANMAKEN,
    SCOPE_DOCUMENTEN_ALLES_LEZEN,
    SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN,
    SCOPE_DOCUMENTEN_BIJWERKEN,
)
from drc.api.serializers import VerzendingSerializer
from drc.datamodel.models import Verzending


@conditional_retrieve()
@extend_schema_view(
    list=extend_schema(
        summary=_("Alle VERZENDINGen opvragen."),
        description=_("Deze lijst kan gefilterd wordt met query-string parameters."),
    ),
    retrieve=extend_schema(
        summary=_("Een specifieke VERZENDING opvragen."),
        description=_("Een specifieke VERZENDING opvragen."),
    ),
    create=extend_schema(
        summary=_("Maak een VERZENDING aan."),
        description=_(
            "Voeg VERZENDINGen toe voor een INFORMATIEOBJECT en een BETROKKENE."
        ),
    ),
    update=extend_schema(
        summary=_("Werk een VERZENDING in zijn geheel bij."),
        description=_("Werk een VERZENDING in zijn geheel bij."),
    ),
    partial_update=extend_schema(
        summary=_("Werk een VERZENDING relatie deels bij."),
        description=_("Werk een VERZENDING relatie deels bij."),
    ),
    destroy=extend_schema(
        summary=_("Verwijder een VERZENDING"),
        description=_("Verwijder een VERZENDING."),
    ),
)
class VerzendingViewSet(
    CheckQueryParamsMixin,
    ExpansionMixin,
    viewsets.ModelViewSet,
):

    global_description = _("Opvragen en bewerken van VERZENDINGen.")

    queryset = Verzending.objects.select_related("informatieobject")
    serializer_class = VerzendingSerializer
    pagination_class = PageNumberPagination
    filterset_class = VerzendingFilter
    lookup_field = "uuid"
    required_scopes = {
        "list": SCOPE_DOCUMENTEN_ALLES_LEZEN,
        "retrieve": SCOPE_DOCUMENTEN_ALLES_LEZEN,
        "create": SCOPE_DOCUMENTEN_AANMAKEN,
        "destroy": SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN,
        "update": SCOPE_DOCUMENTEN_BIJWERKEN,
        "partial_update": SCOPE_DOCUMENTEN_BIJWERKEN,
    }
