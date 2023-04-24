from django.utils.translation import gettext as _

from drf_spectacular.utils import extend_schema, extend_schema_view
from notifications_api_common.viewsets import NotificationViewSetMixin
from rest_framework import viewsets
from vng_api_common.audittrails.viewsets import AuditTrailViewsetMixin
from vng_api_common.caching.decorators import conditional_retrieve
from vng_api_common.viewsets import CheckQueryParamsMixin

from drc.api.audits import AUDIT_DRC
from drc.api.data_filtering import ListFilterByAuthorizationsMixin
from drc.api.filters import GebruiksrechtenFilter
from drc.api.inclusions import InclusionsMixin
from drc.api.kanalen import KANAAL_DOCUMENTEN
from drc.api.permissions import InformationObjectRelatedAuthScopesRequired
from drc.api.scopes import (
    SCOPE_DOCUMENTEN_AANMAKEN,
    SCOPE_DOCUMENTEN_ALLES_LEZEN,
    SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN,
    SCOPE_DOCUMENTEN_BIJWERKEN,
)
from drc.api.serializers import GebruiksrechtenSerializer
from drc.datamodel.models.gebruiksrechten import Gebruiksrechten


@conditional_retrieve()
@extend_schema_view(
    list=extend_schema(
        summary=_("Alle GEBRUIKSRECHTen opvragen."),
        description=_("Deze lijst kan gefilterd wordt met query-string parameters."),
    ),
    retrieve=extend_schema(
        summary=_("Een specifieke GEBRUIKSRECHT opvragen."),
        description=_("Een specifieke GEBRUIKSRECHT opvragen."),
    ),
    create=extend_schema(
        summary=_("Maak een GEBRUIKSRECHT aan."),
        description=_(
            "Voeg GEBRUIKSRECHTen toe voor een INFORMATIEOBJECT."
            "  \n**Opmerkingen**\n"
            "   - Het toevoegen van gebruiksrechten zorgt ervoor dat de"
            "  `indicatieGebruiksrecht` op het informatieobject op `true` gezet wordt."
        ),
    ),
    destroy=extend_schema(
        summary=_("Verwijder een GEBRUIKSRECHT."),
        description=_(
            "\n**Opmerkingen**\n"
            "  - Indien het laatste GEBRUIKSRECHT van een INFORMATIEOBJECT verwijderd"
            "  wordt, dan wordt de `indicatieGebruiksrecht` van het INFORMATIEOBJECT op"
            "`null` gezet."
        ),
    ),
    update=extend_schema(
        summary=_("Werk een GEBRUIKSRECHT in zijn geheel bij."),
        description=_("Werk een GEBRUIKSRECHT in zijn geheel bij."),
    ),
    partial_update=extend_schema(
        summary=_("Werk een GEBRUIKSRECHT relatie deels bij."),
        description=_("Werk een GEBRUIKSRECHT relatie deels bij."),
    ),
)
class GebruiksrechtenViewSet(
    NotificationViewSetMixin,
    CheckQueryParamsMixin,
    ListFilterByAuthorizationsMixin,
    AuditTrailViewsetMixin,
    InclusionsMixin,
    viewsets.ModelViewSet,
):
    global_description = _(
        "Opvragen en bewerken van GEBRUIKSRECHTen bij een INFORMATIEOBJECT."
    )

    queryset = Gebruiksrechten.objects.all()
    serializer_class = GebruiksrechtenSerializer
    filterset_class = GebruiksrechtenFilter
    lookup_field = "uuid"
    notifications_kanaal = KANAAL_DOCUMENTEN
    notifications_main_resource_key = "informatieobject"
    permission_classes = (InformationObjectRelatedAuthScopesRequired,)
    required_scopes = {
        "list": SCOPE_DOCUMENTEN_ALLES_LEZEN,
        "retrieve": SCOPE_DOCUMENTEN_ALLES_LEZEN,
        "create": SCOPE_DOCUMENTEN_AANMAKEN,
        "destroy": SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN,
        "update": SCOPE_DOCUMENTEN_BIJWERKEN,
        "partial_update": SCOPE_DOCUMENTEN_BIJWERKEN,
    }
    audit = AUDIT_DRC
    audittrail_main_resource_key = "informatieobject"
