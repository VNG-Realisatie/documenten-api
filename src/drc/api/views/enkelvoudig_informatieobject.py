from django.db import transaction
from django.utils.translation import gettext as _

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.settings import api_settings
from sendfile import sendfile
from vng_api_common.audittrails.viewsets import (
    AuditTrailViewSet,
    AuditTrailViewsetMixin,
)
from vng_api_common.caching.decorators import conditional_retrieve
from vng_api_common.notifications.viewsets import NotificationViewSetMixin
from vng_api_common.serializers import FoutSerializer
from vng_api_common.viewsets import CheckQueryParamsMixin

from drc.api.audits import AUDIT_DRC
from drc.api.filters import (
    EnkelvoudigInformatieObjectDetailFilter,
    EnkelvoudigInformatieObjectListFilter,
)
from drc.api.kanalen import KANAAL_DOCUMENTEN
from drc.api.renderers import BinaryFileRenderer
from drc.api.schema import EIOAutoSchema
from drc.api.scopes import (
    SCOPE_DOCUMENTEN_AANMAKEN,
    SCOPE_DOCUMENTEN_ALLES_LEZEN,
    SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN,
    SCOPE_DOCUMENTEN_BIJWERKEN,
    SCOPE_DOCUMENTEN_GEFORCEERD_UNLOCK,
    SCOPE_DOCUMENTEN_LOCK,
)
from drc.api.serializers import (
    EnkelvoudigInformatieObjectCreateLockSerializer,
    EnkelvoudigInformatieObjectSerializer,
    EnkelvoudigInformatieObjectWithLockSerializer,
    LockEnkelvoudigInformatieObjectSerializer,
    UnlockEnkelvoudigInformatieObjectSerializer,
)
from drc.api.views.constants import REGISTRATIE_QUERY_PARAM, VERSIE_QUERY_PARAM
from drc.datamodel.models import EnkelvoudigInformatieObject

from ..data_filtering import ListFilterByAuthorizationsMixin
from ..permissions import InformationObjectAuthScopesRequired


@conditional_retrieve()
class EnkelvoudigInformatieObjectViewSet(
    NotificationViewSetMixin,
    CheckQueryParamsMixin,
    ListFilterByAuthorizationsMixin,
    AuditTrailViewsetMixin,
    viewsets.ModelViewSet,
):
    """
    Opvragen en bewerken van (ENKELVOUDIG) INFORMATIEOBJECTen (documenten).

    create:
    Maak een (ENKELVOUDIG) INFORMATIEOBJECT aan.

    **Er wordt gevalideerd op**
    - geldigheid `informatieobjecttype` URL - de resource moet opgevraagd kunnen
      worden uit de catalogi API en de vorm van een INFORMATIEOBJECTTYPE hebben.
    - publicatie `informatieobjecttype` - `concept` moet `false` zijn

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
    - het `informatieobjecttype` mag niet gewijzigd worden
    - status NIET `definitief`

    partial_update:
    Werk een (ENKELVOUDIG) INFORMATIEOBJECT deels bij.

    Dit creëert altijd een nieuwe versie van het (ENKELVOUDIG) INFORMATIEOBJECT.

    **Er wordt gevalideerd op**
    - correcte `lock` waarde
    - het `informatieobjecttype` mag niet gewijzigd worden
    - status NIET `definitief`

    destroy:
    Verwijder een (ENKELVOUDIG) INFORMATIEOBJECT.

    Verwijder een (ENKELVOUDIG) INFORMATIEOBJECT en alle bijbehorende versies,
    samen met alle gerelateerde resources binnen deze API. Dit is alleen mogelijk
    als er geen OBJECTINFORMATIEOBJECTen relateerd zijn aan het (ENKELVOUDIG)
    INFORMATIEOBJECT.

    **Gerelateerde resources**
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

    queryset = EnkelvoudigInformatieObject.objects.order_by(
        "canonical", "-versie"
    ).distinct("canonical")
    lookup_field = "uuid"
    pagination_class = PageNumberPagination
    permission_classes = (InformationObjectAuthScopesRequired,)

    required_scopes = {
        "list": SCOPE_DOCUMENTEN_ALLES_LEZEN,
        "retrieve": SCOPE_DOCUMENTEN_ALLES_LEZEN,
        "create": SCOPE_DOCUMENTEN_AANMAKEN,
        "destroy": SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN,
        "update": SCOPE_DOCUMENTEN_BIJWERKEN,
        "partial_update": SCOPE_DOCUMENTEN_BIJWERKEN,
        "download": SCOPE_DOCUMENTEN_ALLES_LEZEN,
        "lock": SCOPE_DOCUMENTEN_LOCK,
        "unlock": SCOPE_DOCUMENTEN_LOCK | SCOPE_DOCUMENTEN_GEFORCEERD_UNLOCK,
    }
    notifications_kanaal = KANAAL_DOCUMENTEN
    audit = AUDIT_DRC

    swagger_schema = EIOAutoSchema

    def get_renderers(self):
        if self.action == "download":
            return [BinaryFileRenderer]
        return super().get_renderers()

    @transaction.atomic
    def perform_destroy(self, instance):
        if instance.canonical.objectinformatieobject_set.exists():
            raise serializers.ValidationError(
                {
                    api_settings.NON_FIELD_ERRORS_KEY: _(
                        "All relations to the document must be destroyed before destroying the document"
                    )
                },
                code="pending-relations",
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
        if self.action in ["update", "partial_update"]:
            return EnkelvoudigInformatieObjectWithLockSerializer
        elif self.action == "create":
            return EnkelvoudigInformatieObjectCreateLockSerializer
        return EnkelvoudigInformatieObjectSerializer

    @swagger_auto_schema(
        manual_parameters=[VERSIE_QUERY_PARAM, REGISTRATIE_QUERY_PARAM]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        method="get",
        # see https://swagger.io/docs/specification/2-0/describing-responses/ and
        # https://swagger.io/docs/specification/2-0/mime-types/
        # OAS 3 has a better mechanism: https://swagger.io/docs/specification/describing-responses/
        produces=["application/octet-stream"],
        responses={
            status.HTTP_200_OK: openapi.Response(
                "De binaire bestandsinhoud",
                schema=openapi.Schema(type=openapi.TYPE_FILE),
            ),
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                "Unauthorized", schema=FoutSerializer
            ),
            status.HTTP_403_FORBIDDEN: openapi.Response(
                "Forbidden", schema=FoutSerializer
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                "Not found", schema=FoutSerializer
            ),
            status.HTTP_406_NOT_ACCEPTABLE: openapi.Response(
                "Not acceptable", schema=FoutSerializer
            ),
            status.HTTP_410_GONE: openapi.Response("Gone", schema=FoutSerializer),
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: openapi.Response(
                "Unsupported media type", schema=FoutSerializer
            ),
            status.HTTP_429_TOO_MANY_REQUESTS: openapi.Response(
                "Throttled", schema=FoutSerializer
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(
                "Internal server error", schema=FoutSerializer
            ),
        },
        manual_parameters=[VERSIE_QUERY_PARAM, REGISTRATIE_QUERY_PARAM],
    )
    @action(methods=["get"], detail=True, name="enkelvoudiginformatieobject_download")
    def download(self, request, *args, **kwargs):
        eio = self.get_object()
        return sendfile(
            request,
            eio.inhoud.path,
            attachment=True,
            mimetype="application/octet-stream",
        )

    @swagger_auto_schema(
        request_body=LockEnkelvoudigInformatieObjectSerializer,
        responses={
            status.HTTP_200_OK: LockEnkelvoudigInformatieObjectSerializer,
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                "Bad request", schema=FoutSerializer
            ),
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                "Unauthorized", schema=FoutSerializer
            ),
            status.HTTP_403_FORBIDDEN: openapi.Response(
                "Forbidden", schema=FoutSerializer
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                "Not found", schema=FoutSerializer
            ),
            status.HTTP_406_NOT_ACCEPTABLE: openapi.Response(
                "Not acceptable", schema=FoutSerializer
            ),
            status.HTTP_410_GONE: openapi.Response("Gone", schema=FoutSerializer),
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: openapi.Response(
                "Unsupported media type", schema=FoutSerializer
            ),
            status.HTTP_429_TOO_MANY_REQUESTS: openapi.Response(
                "Throttled", schema=FoutSerializer
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(
                "Internal server error", schema=FoutSerializer
            ),
        },
    )
    @action(detail=True, methods=["post"])
    def lock(self, request, *args, **kwargs):
        eio = self.get_object()
        canonical = eio.canonical
        lock_serializer = LockEnkelvoudigInformatieObjectSerializer(
            canonical, data=request.data
        )
        lock_serializer.is_valid(raise_exception=True)
        lock_serializer.save()
        return Response(lock_serializer.data)

    @swagger_auto_schema(
        request_body=UnlockEnkelvoudigInformatieObjectSerializer,
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response("No content"),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                "Bad request", schema=FoutSerializer
            ),
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                "Unauthorized", schema=FoutSerializer
            ),
            status.HTTP_403_FORBIDDEN: openapi.Response(
                "Forbidden", schema=FoutSerializer
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                "Not found", schema=FoutSerializer
            ),
            status.HTTP_406_NOT_ACCEPTABLE: openapi.Response(
                "Not acceptable", schema=FoutSerializer
            ),
            status.HTTP_410_GONE: openapi.Response("Gone", schema=FoutSerializer),
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: openapi.Response(
                "Unsupported media type", schema=FoutSerializer
            ),
            status.HTTP_429_TOO_MANY_REQUESTS: openapi.Response(
                "Throttled", schema=FoutSerializer
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(
                "Internal server error", schema=FoutSerializer
            ),
        },
    )
    @action(detail=True, methods=["post"])
    def unlock(self, request, *args, **kwargs):
        eio = self.get_object()
        eio.canonical
        # check if it's a force unlock by administrator
        force_unlock = False
        if self.request.jwt_auth.has_auth(
            scopes=SCOPE_DOCUMENTEN_GEFORCEERD_UNLOCK,
            informatieobjecttype=eio.informatieobjecttype,
            vertrouwelijkheidaanduiding=eio.vertrouwelijkheidaanduiding,
        ):
            force_unlock = True

        unlock_serializer = UnlockEnkelvoudigInformatieObjectSerializer(
            eio, data=request.data, context={"force_unlock": force_unlock}
        )
        unlock_serializer.is_valid(raise_exception=True)
        unlock_serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


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

    main_resource_lookup_field = "enkelvoudiginformatieobject_uuid"
