from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from vng_api_common.caching.decorators import conditional_retrieve
from vng_api_common.viewsets import CheckQueryParamsMixin

from drc.api.filters import VerzendingFilter
from drc.api.scopes import (
    SCOPE_DOCUMENTEN_AANMAKEN,
    SCOPE_DOCUMENTEN_ALLES_LEZEN,
    SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN,
    SCOPE_DOCUMENTEN_BIJWERKEN,
)
from drc.api.serializers import VerzendingSerializer
from drc.datamodel.models import Verzending


@conditional_retrieve()
class VerzendingViewSet(
    CheckQueryParamsMixin,
    viewsets.ModelViewSet,
):
    """
    Opvragen en bewerken van VERZENDINGen.

    create:
    Maak een VERZENDING aan.

    Voeg VERZENDINGen toe voor een INFORMATIEOBJECT en een BETROKKENE.

    list:
    Alle VERZENDINGen opvragen.

    Deze lijst kan gefilterd wordt met query-string parameters.

    retrieve:
    Een specifieke VERZENDING opvragen.

    Een specifieke VERZENDING opvragen.

    update:
    Werk een VERZENDING in zijn geheel bij.

    Werk een VERZENDING in zijn geheel bij.

    partial_update:
    Werk een VERZENDING relatie deels bij.

    Werk een VERZENDING relatie deels bij.

    destroy:
    Verwijder een VERZENDING.
    """

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
