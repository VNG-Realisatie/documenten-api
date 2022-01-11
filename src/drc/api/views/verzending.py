from rest_framework import viewsets
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
    TODO
    """

    queryset = Verzending.objects.all()
    serializer_class = VerzendingSerializer
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
