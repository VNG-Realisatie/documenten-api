from django.db import transaction
from django.http.response import Http404
from django.shortcuts import get_list_or_404, get_object_or_404
from django.utils import dateparse, timezone
from django.utils.translation import ugettext_lazy as _

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.settings import api_settings
from sendfile import sendfile
from vng_api_common.audittrails.viewsets import (
    AuditTrailCreateMixin, AuditTrailDestroyMixin, AuditTrailViewSet,
    AuditTrailViewsetMixin
)
from vng_api_common.filters import Backend
from vng_api_common.notifications.viewsets import (
    NotificationCreateMixin, NotificationDestroyMixin,
    NotificationViewSetMixin
)
from vng_api_common.serializers import FoutSerializer
from vng_api_common.viewsets import CheckQueryParamsMixin

from drc.datamodel.models import (
    EnkelvoudigInformatieObject, EnkelvoudigInformatieObjectCanonical,
    Gebruiksrechten, ObjectInformatieObject
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
    description='Het versienummer van het `EnkelvoudigInformatieObject` dat opgehaald moet worden',
    type=openapi.TYPE_INTEGER
)
REGISTRATIE_QUERY_PARAM = openapi.Parameter(
    'registratieOp',
    openapi.IN_QUERY,
    description='Een datumtijd in ISO8601 formaat, de `EnkelvoudigInformatieObject` versie die qua begin_registratie het kortst hiervoor zit wordt opgehaald',
    type=openapi.TYPE_STRING
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
    Geef een lijst van de laatste versies van ENKELVOUDIGe INFORMATIEOBJECTen
    (=documenten).


    De objecten bevatten metadata over de documenten en de downloadlink naar
    de binary data.

    retrieve:
    Geef de details van de laatste versie ENKELVOUDIG INFORMATIEOBJECT.

    Het object bevat metadata over het informatieobject en de downloadlink naar
    de binary data.

    Er kan gefiltered worden met querystringparameters.

    update:
    Maak een nieuwe versie van een ENKELVOUDIG INFORMATIEOBJECT aan door de
    volledige resource mee te sturen.

    **Er wordt gevalideerd op**
    - geldigheid informatieobjecttype URL

    *TODO*
    - valideer immutable attributes

    partial_update:
    Maak een nieuwe versie van een ENKELVOUDIG INFORMATIEOBJECT aan door enkel
    de gewijzigde velden mee te sturen.

    **Er wordt gevalideerd op**
    - geldigheid informatieobjecttype URL

    *TODO*
    - valideer immutable attributes

    destroy:
    Verwijdert een ENKELVOUDIG INFORMATIEOBJECT en alle bijbehorende versies,
    samen met alle gerelateerde resources binnen deze API.

    **Gerelateerde resources**
    - `ObjectInformatieObject` - alle relaties van het informatieobject
    - `Gebruiksrechten` - alle gebruiksrechten van het informatieobject
    """
    queryset = EnkelvoudigInformatieObject.objects.order_by('canonical', '-versie').distinct('canonical')
    lookup_field = 'uuid'
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
        if self.action == 'update' or self.action == 'partial_update':
            return EnkelvoudigInformatieObjectWithLockSerializer
        return EnkelvoudigInformatieObjectSerializer

    def get_queryset(self):
        """
        Haal de meest recente versie van elk `EnkelvoudigInformatieObject` op
        """
        qs = super().get_queryset()
        return qs.order_by('canonical', '-versie').distinct('canonical')

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
    Verwijder een relatie tussen een object en een informatieobject.
    OPGELET: dit endpoint hoor je als client NIET zelf aan te spreken, dit moet
    gedaan worden door het ZRC/BRC
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
