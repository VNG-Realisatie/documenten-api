from rest_framework import mixins, viewsets
from vng_api_common.audittrails.viewsets import (
    AuditTrailCreateMixin, AuditTrailDestroyMixin, AuditTrailViewSet,
    AuditTrailViewsetMixin
)
from vng_api_common.notifications.viewsets import (
    NotificationCreateMixin, NotificationViewSetMixin
)
from vng_api_common.viewsets import CheckQueryParamsMixin

from drc.datamodel.models import (
    EnkelvoudigInformatieObject, Gebruiksrechten, ObjectInformatieObject
)

from .audits import AUDIT_DRC
from .data_filtering import ListFilterByAuthorizationsMixin
from .filters import (
    EnkelvoudigInformatieObjectFilter, GebruiksrechtenFilter,
    ObjectInformatieObjectFilter
)
from .kanalen import KANAAL_DOCUMENTEN
from .permissions import (
    InformationObjectAuthScopesRequired,
    InformationObjectRelatedAuthScopesRequired
)
from .scopes import (
    SCOPE_DOCUMENTEN_AANMAKEN, SCOPE_DOCUMENTEN_ALLES_LEZEN,
    SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN, SCOPE_DOCUMENTEN_BIJWERKEN
)
from .serializers import (
    EnkelvoudigInformatieObjectSerializer, GebruiksrechtenSerializer,
    ObjectInformatieObjectSerializer
)


class EnkelvoudigInformatieObjectViewSet(NotificationViewSetMixin,
                                         ListFilterByAuthorizationsMixin,
                                         AuditTrailViewsetMixin,
                                         viewsets.ModelViewSet):
    """
    Ontsluit ENKELVOUDIG INFORMATIEOBJECTen.

    create:
    Registreer een ENKELVOUDIG INFORMATIEOBJECT.

    **Er wordt gevalideerd op**
    - geldigheid informatieobjecttype URL

    list:
    Geef een lijst van ENKELVOUDIGe INFORMATIEOBJECTen (=documenten).

    De objecten bevatten metadata over de documenten en de downloadlink naar
    de binary data.

    retrieve:
    Geef de details van een ENKELVOUDIG INFORMATIEOBJECT.

    Het object bevat metadata over het informatieobject en de downloadlink naar
    de binary data.

    update:
    Werk een ENKELVOUDIG INFORMATIEOBJECT bij door de volledige resource mee
    te sturen.

    **Er wordt gevalideerd op**
    - geldigheid informatieobjecttype URL

    *TODO*
    - valideer immutable attributes

    partial_update:
    Werk een ENKELVOUDIG INFORMATIEOBJECT bij door enkel de gewijzigde velden
    mee te sturen.

    **Er wordt gevalideerd op**
    - geldigheid informatieobjecttype URL

    *TODO*
    - valideer immutable attributes

    destroy:
    Verwijdert een ENKELVOUDIG INFORMATIEOBJECT, samen met alle gerelateerde
    resources binnen deze API.

    **Gerelateerde resources**
    - `ObjectInformatieObject` - alle relaties van het informatieobject
    - `Gebruiksrechten` - alle gebruiksrechten van het informatieobject
    """
    queryset = EnkelvoudigInformatieObject.objects.all()
    serializer_class = EnkelvoudigInformatieObjectSerializer
    filterset_class = EnkelvoudigInformatieObjectFilter
    lookup_field = 'uuid'
    permission_classes = (InformationObjectAuthScopesRequired, )
    required_scopes = {
        'list': SCOPE_DOCUMENTEN_ALLES_LEZEN,
        'retrieve': SCOPE_DOCUMENTEN_ALLES_LEZEN,
        'create': SCOPE_DOCUMENTEN_AANMAKEN,
        'destroy': SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN,
        'update': SCOPE_DOCUMENTEN_BIJWERKEN,
        'partial_update': SCOPE_DOCUMENTEN_BIJWERKEN,
    }
    notifications_kanaal = KANAAL_DOCUMENTEN
    audit = AUDIT_DRC


class ObjectInformatieObjectViewSet(NotificationCreateMixin,
                                    AuditTrailCreateMixin,
                                    AuditTrailDestroyMixin,
                                    CheckQueryParamsMixin,
                                    ListFilterByAuthorizationsMixin,
                                    mixins.CreateModelMixin,
                                    mixins.DestroyModelMixin,
                                    viewsets.ReadOnlyModelViewSet):
    """
    Opvragen en bewerken van Object-Informatieobject relaties.

    create:
    OPGELET: dit endpoint hoor je als client NIET zelf aan te spreken.

    ZRC en BRC gebruiken deze endpoint bij het synchroniseren van relaties.

    Registreer welk(e) INFORMATIEOBJECT(en) een OBJECT kent.

    **Er wordt gevalideerd op**
    - geldigheid informatieobject URL
    - uniek zijn van relatie OBJECT-INFORMATIEOBJECT
    - bestaan van relatie OBJECT-INFORMATIEOBJECT in het ZRC of DRC (waar het
      object leeft)

    list:
    Geef een lijst van relaties tussen OBJECTen en INFORMATIEOBJECTen.

    retrieve:
    Geef een informatieobject terug wat gekoppeld is aan het huidige object

    destroy:
    Verwijder een relatie tussen een object en een informatieobject
    """
    queryset = ObjectInformatieObject.objects.all()
    serializer_class = ObjectInformatieObjectSerializer
    filterset_class = ObjectInformatieObjectFilter
    lookup_field = 'uuid'
    notifications_kanaal = KANAAL_DOCUMENTEN
    notifications_main_resource_key = 'informatieobject'
    permission_classes = (InformationObjectRelatedAuthScopesRequired,)
    required_scopes = {
        'list': SCOPE_DOCUMENTEN_ALLES_LEZEN,
        'retrieve': SCOPE_DOCUMENTEN_ALLES_LEZEN,
        'create': SCOPE_DOCUMENTEN_AANMAKEN,
        'destroy': SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN,
        'update': SCOPE_DOCUMENTEN_BIJWERKEN,
        'partial_update': SCOPE_DOCUMENTEN_BIJWERKEN,
    }
    audit = AUDIT_DRC
    audittrail_main_resource_key = 'informatieobject'

class GebruiksrechtenViewSet(NotificationViewSetMixin,
                             ListFilterByAuthorizationsMixin,
                             AuditTrailViewsetMixin,
                             viewsets.ModelViewSet):
    """
    list:
    Geef een lijst van gebruiksrechten horend bij informatieobjecten.

    Er kan gefiltered worden met querystringparameters.

    retrieve:
    Haal de details op van een gebruiksrecht van een informatieobject.

    create:
    Voeg gebruiksrechten toe voor een informatieobject.

    **Opmerkingen**
    - Het toevoegen van gebruiksrechten zorgt ervoor dat de
      `indicatieGebruiksrecht` op het informatieobject op `true` gezet wordt.

    update:
    Werk een gebruiksrecht van een informatieobject bij.

    partial_update:
    Werk een gebruiksrecht van een informatieobject bij.

    destroy:
    Verwijder een gebruiksrecht van een informatieobject.

    **Opmerkingen**
    - Indien het laatste gebruiksrecht van een informatieobject verwijderd wordt,
      dan wordt de `indicatieGebruiksrecht` van het informatieobject op `null`
      gezet.
    """
    queryset = Gebruiksrechten.objects.all()
    serializer_class = GebruiksrechtenSerializer
    filterset_class = GebruiksrechtenFilter
    lookup_field = 'uuid'
    notifications_kanaal = KANAAL_DOCUMENTEN
    notifications_main_resource_key = 'informatieobject'
    permission_classes = (InformationObjectRelatedAuthScopesRequired,)
    required_scopes = {
        'list': SCOPE_DOCUMENTEN_ALLES_LEZEN,
        'retrieve': SCOPE_DOCUMENTEN_ALLES_LEZEN,
        'create': SCOPE_DOCUMENTEN_AANMAKEN,
        'destroy': SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN,
        'update': SCOPE_DOCUMENTEN_BIJWERKEN,
        'partial_update': SCOPE_DOCUMENTEN_BIJWERKEN,
    }
    audit = AUDIT_DRC
    audittrail_main_resource_key = 'informatieobject'


class EnkelvoudigInformatieObjectAuditTrailViewSet(AuditTrailViewSet):
    """
    Opvragen van Audit trails horend bij een EnkelvoudigInformatieObject.

    list:
    Geef een lijst van AUDITTRAILS die horen bij het huidige EnkelvoudigInformatieObject.

    retrieve:
    Haal de details van een AUDITTRAIL op.
    """
    main_resource_lookup_field = 'enkelvoudiginformatieobject_uuid'
