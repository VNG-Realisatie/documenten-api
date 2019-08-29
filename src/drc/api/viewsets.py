from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.settings import api_settings
from sendfile import sendfile
from vng_api_common.audittrails.viewsets import (
    AuditTrailCreateMixin, AuditTrailDestroyMixin, AuditTrailViewSet,
    AuditTrailViewsetMixin
)
from vng_api_common.notifications.viewsets import (
    NotificationCreateMixin, NotificationDestroyMixin,
    NotificationViewSetMixin
)
from vng_api_common.serializers import FoutSerializer
from vng_api_common.viewsets import CheckQueryParamsMixin

from drc.datamodel.models import (
    EnkelvoudigInformatieObject, Gebruiksrechten, ObjectInformatieObject
)

from .audits import AUDIT_DRC
from .data_filtering import ListFilterByAuthorizationsMixin
from .filters import (
    EnkelvoudigInformatieObjectDetailFilter,
    EnkelvoudigInformatieObjectListFilter, GebruiksrechtenFilter,
    ObjectInformatieObjectFilter
)
from .kanalen import KANAAL_DOCUMENTEN
from .permissions import (
    InformationObjectAuthScopesRequired,
    InformationObjectRelatedAuthScopesRequired
)
from .schema import EIOAutoSchema
from .scopes import (
    SCOPE_DOCUMENTEN_AANMAKEN, SCOPE_DOCUMENTEN_ALLES_LEZEN,
    SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN, SCOPE_DOCUMENTEN_BIJWERKEN,
    SCOPE_DOCUMENTEN_GEFORCEERD_UNLOCK, SCOPE_DOCUMENTEN_LOCK
)
from .serializers import (
    EnkelvoudigInformatieObjectSerializer,
    EnkelvoudigInformatieObjectWithLockSerializer, GebruiksrechtenSerializer,
    LockEnkelvoudigInformatieObjectSerializer,
    ObjectInformatieObjectSerializer,
    UnlockEnkelvoudigInformatieObjectSerializer
)
from .validators import RemoteRelationValidator

# Openapi query parameters for version querying
VERSIE_QUERY_PARAM = openapi.Parameter(
    'versie',
    openapi.IN_QUERY,
    description='Het (automatische) versienummer van het INFORMATIEOBJECT.',
    type=openapi.TYPE_INTEGER
)
REGISTRATIE_QUERY_PARAM = openapi.Parameter(
    'registratieOp',
    openapi.IN_QUERY,
    description='Een datumtijd in ISO8601 formaat. De versie van het INFORMATIEOBJECT die qua `begin_registratie` het '
                'kortst hiervoor zit wordt opgehaald.',
    type=openapi.TYPE_STRING
)


class EnkelvoudigInformatieObjectViewSet(NotificationViewSetMixin,
                                         ListFilterByAuthorizationsMixin,
                                         AuditTrailViewsetMixin,
                                         viewsets.ModelViewSet):
    """
    Opvragen en bewerken van (ENKELVOUDIG) INFORMATIEOBJECTen (documenten).

    create:
    Maak een (ENKELVOUDIG) INFORMATIEOBJECT aan.

    **Er wordt gevalideerd op**
    - geldigheid `informatieobjecttype` URL

    list:
    Alle (ENKELVOUDIGe) INFORMATIEOBJECTen opvragen.

    Deze lijst kan gefilterd wordt met query-string parameters.

    De objecten bevatten metadata over de documenten en de downloadlink
    (`inhoud`) naar de binary data. Alleen de laatste versie van elk
    (ENKELVOUDIG) INFORMATIEOBJECT wordt getoond. Specifieke versies kunnen
    alleen

    retrieve:
    Een specifiek (ENKELVOUDIG) INFORMATIEOBJECT opvragen.

    Het object bevat metadata over het document en de downloadlink (`inhoud`)
    naar de binary data. Dit geeft standaard de laatste versie van het
    (ENKELVOUDIG) INFORMATIEOBJECT. Specifieke versies kunnen middels
    query-string parameters worden opgevraagd.

    update:
    Werk een (ENKELVOUDIG) INFORMATIEOBJECT in zijn geheel bij.

    Dit creëert altijd een nieuwe versie van het (ENKELVOUDIG) INFORMATIEOBJECT.

    **Er wordt gevalideerd op**
    - correcte `lock` waarde
    - geldigheid `informatieobjecttype` URL

    *TODO*
    - valideer immutable attributes

    partial_update:
    Werk een (ENKELVOUDIG) INFORMATIEOBJECT deels bij.

    Dit creëert altijd een nieuwe versie van het (ENKELVOUDIG) INFORMATIEOBJECT.

    **Er wordt gevalideerd op**
    - correcte `lock` waarde
    - geldigheid `informatieobjecttype` URL

    *TODO*
    - valideer immutable attributes

    destroy:
    Verwijder een (ENKELVOUDIG) INFORMATIEOBJECT.

    Verwijder een (ENKELVOUDIG) INFORMATIEOBJECT en alle bijbehorende versies,
    samen met alle gerelateerde resources binnen deze API.

    **Gerelateerde resources**
    - OBJECT-INFORMATIEOBJECT
    - GEBRUIKSRECHTen
    - audit trail regels

    download:
    Download de binaire data van het (ENKELVOUDIG) INFORMATIEOBJECT.

    Download de binaire data van het (ENKELVOUDIG) INFORMATIEOBJECT.

    lock:
    Vergrendel een (ENKELVOUDIG) INFORMATIEOBJECT.

    Voert een "checkout" uit waardoor het (ENKELVOUDIG) INFORMATIEOBJECT
    vergrendeld wordt met een `lock` waarde. Alleen met deze waarde kan het
    (ENKELVOUDIG) INFORMATIEOBJECT bijgewerkt (`PUT`, `PATCH`) en weer
    ontgrendeld worden.

    unlock:
    Ontgrendel een (ENKELVOUDIG) INFORMATIEOBJECT.

    Heft de "checkout" op waardoor het (ENKELVOUDIG) INFORMATIEOBJECT
    ontgrendeld wordt.
    """
    queryset = EnkelvoudigInformatieObject.objects.order_by('canonical', '-versie').distinct('canonical')
    lookup_field = 'uuid'
    pagination_class = PageNumberPagination
    permission_classes = (InformationObjectAuthScopesRequired, )
    required_scopes = {
        'list': SCOPE_DOCUMENTEN_ALLES_LEZEN,
        'retrieve': SCOPE_DOCUMENTEN_ALLES_LEZEN,
        'create': SCOPE_DOCUMENTEN_AANMAKEN,
        'destroy': SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN,
        'update': SCOPE_DOCUMENTEN_BIJWERKEN,
        'partial_update': SCOPE_DOCUMENTEN_BIJWERKEN,
        'download': SCOPE_DOCUMENTEN_ALLES_LEZEN,
        'lock': SCOPE_DOCUMENTEN_LOCK,
        'unlock': SCOPE_DOCUMENTEN_LOCK | SCOPE_DOCUMENTEN_GEFORCEERD_UNLOCK
    }
    notifications_kanaal = KANAAL_DOCUMENTEN
    audit = AUDIT_DRC

    swagger_schema = EIOAutoSchema

    @transaction.atomic
    def perform_destroy(self, instance):
        if instance.canonical.objectinformatieobject_set.exists():
            raise serializers.ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: _(
                    "All relations to the document must be destroyed before destroying the document"
                )},
                code="pending-relations"
            )

        super().perform_destroy(instance.canonical)

    @property
    def filterset_class(self):
        """
        To support filtering by versie and registratieOp for detail view
        """
        if self.detail:
            return EnkelvoudigInformatieObjectDetailFilter
        return EnkelvoudigInformatieObjectListFilter

    def get_serializer_class(self):
        """
        To validate that a lock id is sent only with PUT and PATCH operations
        """
        if getattr(self, 'action', None) in ['update', 'partial_update']:
            return EnkelvoudigInformatieObjectWithLockSerializer
        return EnkelvoudigInformatieObjectSerializer

    @swagger_auto_schema(
        manual_parameters=[
            VERSIE_QUERY_PARAM,
            REGISTRATIE_QUERY_PARAM
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        method='get',
        # see https://swagger.io/docs/specification/2-0/describing-responses/ and
        # https://swagger.io/docs/specification/2-0/mime-types/
        # OAS 3 has a better mechanism: https://swagger.io/docs/specification/describing-responses/
        produces=["application/octet-stream"],
        responses={
            status.HTTP_200_OK: openapi.Response(
                "De binaire bestandsinhoud",
                schema=openapi.Schema(type=openapi.TYPE_FILE)
            ),
            status.HTTP_401_UNAUTHORIZED: openapi.Response("Unauthorized", schema=FoutSerializer),
            status.HTTP_403_FORBIDDEN: openapi.Response("Forbidden", schema=FoutSerializer),
            status.HTTP_404_NOT_FOUND: openapi.Response("Not found", schema=FoutSerializer),
            status.HTTP_406_NOT_ACCEPTABLE: openapi.Response("Not acceptable", schema=FoutSerializer),
            status.HTTP_410_GONE: openapi.Response("Gone", schema=FoutSerializer),
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: openapi.Response("Unsupported media type", schema=FoutSerializer),
            status.HTTP_429_TOO_MANY_REQUESTS: openapi.Response("Throttled", schema=FoutSerializer),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response("Internal server error", schema=FoutSerializer),
        },
        manual_parameters=[
            VERSIE_QUERY_PARAM,
            REGISTRATIE_QUERY_PARAM
        ]
    )
    @action(methods=['get'], detail=True, name='enkelvoudiginformatieobject_download')
    def download(self, request, *args, **kwargs):
        eio = self.get_object()
        return sendfile(
            request,
            eio.inhoud.path,
            attachment=True,
            mimetype='application/octet-stream'
        )

    @swagger_auto_schema(
        request_body=LockEnkelvoudigInformatieObjectSerializer,
        responses={
            status.HTTP_200_OK: LockEnkelvoudigInformatieObjectSerializer,
            status.HTTP_400_BAD_REQUEST: openapi.Response("Bad request", schema=FoutSerializer),
            status.HTTP_401_UNAUTHORIZED: openapi.Response("Unauthorized", schema=FoutSerializer),
            status.HTTP_403_FORBIDDEN: openapi.Response("Forbidden", schema=FoutSerializer),
            status.HTTP_404_NOT_FOUND: openapi.Response("Not found", schema=FoutSerializer),
            status.HTTP_406_NOT_ACCEPTABLE: openapi.Response("Not acceptable", schema=FoutSerializer),
            status.HTTP_410_GONE: openapi.Response("Gone", schema=FoutSerializer),
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: openapi.Response("Unsupported media type", schema=FoutSerializer),
            status.HTTP_429_TOO_MANY_REQUESTS: openapi.Response("Throttled", schema=FoutSerializer),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response("Internal server error", schema=FoutSerializer),
        }
    )
    @action(detail=True, methods=['post'])
    def lock(self, request, *args, **kwargs):
        eio = self.get_object()
        canonical = eio.canonical
        lock_serializer = LockEnkelvoudigInformatieObjectSerializer(canonical, data=request.data)
        lock_serializer.is_valid(raise_exception=True)
        lock_serializer.save()
        return Response(lock_serializer.data)

    @swagger_auto_schema(
        request_body=UnlockEnkelvoudigInformatieObjectSerializer,
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response("No content"),
            status.HTTP_400_BAD_REQUEST: openapi.Response("Bad request", schema=FoutSerializer),
            status.HTTP_401_UNAUTHORIZED: openapi.Response("Unauthorized", schema=FoutSerializer),
            status.HTTP_403_FORBIDDEN: openapi.Response("Forbidden", schema=FoutSerializer),
            status.HTTP_404_NOT_FOUND: openapi.Response("Not found", schema=FoutSerializer),
            status.HTTP_406_NOT_ACCEPTABLE: openapi.Response("Not acceptable", schema=FoutSerializer),
            status.HTTP_410_GONE: openapi.Response("Gone", schema=FoutSerializer),
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: openapi.Response("Unsupported media type", schema=FoutSerializer),
            status.HTTP_429_TOO_MANY_REQUESTS: openapi.Response("Throttled", schema=FoutSerializer),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response("Internal server error", schema=FoutSerializer),
        }
    )
    @action(detail=True, methods=['post'])
    def unlock(self, request, *args, **kwargs):
        eio = self.get_object()
        canonical = eio.canonical
        # check if it's a force unlock by administrator
        force_unlock = False
        if self.request.jwt_auth.has_auth(
            scopes=SCOPE_DOCUMENTEN_GEFORCEERD_UNLOCK,
            informatieobjecttype=eio.informatieobjecttype,
            vertrouwelijkheidaanduiding=eio.vertrouwelijkheidaanduiding
        ):
            force_unlock = True

        unlock_serializer = UnlockEnkelvoudigInformatieObjectSerializer(
            canonical,
            data=request.data,
            context={'force_unlock': force_unlock}
        )
        unlock_serializer.is_valid(raise_exception=True)
        unlock_serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ObjectInformatieObjectViewSet(NotificationCreateMixin,
                                    NotificationDestroyMixin,
                                    AuditTrailCreateMixin,
                                    AuditTrailDestroyMixin,
                                    CheckQueryParamsMixin,
                                    ListFilterByAuthorizationsMixin,
                                    mixins.CreateModelMixin,
                                    mixins.DestroyModelMixin,
                                    viewsets.ReadOnlyModelViewSet):
    """
    Opvragen en verwijderen van OBJECT-INFORMATIEOBJECT relaties.

    Het betreft een relatie tussen een willekeurig OBJECT, bijvoorbeeld een
    ZAAK in de Zaken API, en een INFORMATIEOBJECT.

    create:
    Maak een OBJECT-INFORMATIEOBJECT relatie aan.

    **LET OP: Dit endpoint hoor je als consumer niet zelf aan te spreken.**

    Andere API's, zoals de Zaken API en de Besluiten API, gebruiken dit
    endpoint bij het synchroniseren van relaties.

    **Er wordt gevalideerd op**
    - geldigheid `informatieobject` URL
    - de combinatie `informatieobject` en `object` moet uniek zijn
    - bestaan van `object` URL

    list:
    Alle OBJECT-INFORMATIEOBJECT relaties opvragen.

    Deze lijst kan gefilterd wordt met query-string parameters.

    retrieve:
    Een specifieke OBJECT-INFORMATIEOBJECT relatie opvragen.

    Een specifieke OBJECT-INFORMATIEOBJECT relatie opvragen.

    destroy:
    Verwijder een OBJECT-INFORMATIEOBJECT relatie.

    **LET OP: Dit endpoint hoor je als consumer niet zelf aan te spreken.**

    Andere API's, zoals de Zaken API en de Besluiten API, gebruiken dit
    endpoint bij het synchroniseren van relaties.
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

    def perform_destroy(self, instance):
        # destroy is only allowed if the remote relation does no longer exist, so check for that
        validator = RemoteRelationValidator()

        try:
            validator(instance)
        except serializers.ValidationError as exc:
            raise serializers.ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: exc
            }, code=exc.detail[0].code)
        else:
            super().perform_destroy(instance)


class GebruiksrechtenViewSet(NotificationViewSetMixin,
                             ListFilterByAuthorizationsMixin,
                             AuditTrailViewsetMixin,
                             viewsets.ModelViewSet):
    """
    Opvragen en bewerken van GEBRUIKSRECHTen bij een INFORMATIEOBJECT.

    create:
    Maak een GEBRUIKSRECHT aan.

    Voeg GEBRUIKSRECHTen toe voor een INFORMATIEOBJECT.

    **Opmerkingen**
      - Het toevoegen van gebruiksrechten zorgt ervoor dat de
        `indicatieGebruiksrecht` op het informatieobject op `true` gezet wordt.

    list:
    Alle GEBRUIKSRECHTen opvragen.

    Deze lijst kan gefilterd wordt met query-string parameters.

    retrieve:
    Een specifieke GEBRUIKSRECHT opvragen.

    Een specifieke GEBRUIKSRECHT opvragen.

    update:
    Werk een GEBRUIKSRECHT in zijn geheel bij.

    Werk een GEBRUIKSRECHT in zijn geheel bij.

    partial_update:
    Werk een GEBRUIKSRECHT relatie deels bij.

    Werk een GEBRUIKSRECHT relatie deels bij.

    destroy:
    Verwijder een GEBRUIKSRECHT.

    **Opmerkingen**
      - Indien het laatste GEBRUIKSRECHT van een INFORMATIEOBJECT verwijderd
        wordt, dan wordt de `indicatieGebruiksrecht` van het INFORMATIEOBJECT op
        `null` gezet.
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
    Opvragen van de audit trail regels.

    list:
    Alle audit trail regels behorend bij het INFORMATIEOBJECT.

    Alle audit trail regels behorend bij het INFORMATIEOBJECT.

    retrieve:
    Een specifieke audit trail regel opvragen.

    Een specifieke audit trail regel opvragen.
    """
    main_resource_lookup_field = 'enkelvoudiginformatieobject_uuid'
