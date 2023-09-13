from django.db import transaction
from django.utils.translation import gettext as _

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from notifications_api_common.viewsets import NotificationViewSetMixin
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
from vng_api_common.caching import conditional_retrieve
from vng_api_common.search import SearchMixin
from vng_api_common.serializers import FoutSerializer
from vng_api_common.viewsets import CheckQueryParamsMixin

from drc.api.audits import AUDIT_DRC
from drc.api.data_filtering import ListFilterByAuthorizationsMixin
from drc.api.exclusions import EXPAND_QUERY_PARAM, ExpandFieldValidator, ExpansionMixin
from drc.api.filters import (
    EnkelvoudigInformatieObjectDetailFilter,
    EnkelvoudigInformatieObjectListFilter,
)
from drc.api.kanalen import KANAAL_DOCUMENTEN
from drc.api.permissions import InformationObjectAuthScopesRequired
from drc.api.renderers import BinaryFileRenderer
from drc.api.schema import EIOAutoSchema
from drc.api.scopes import (
    SCOPE_DOCUMENTEN_AANMAKEN,
    SCOPE_DOCUMENTEN_ALLES_LEZEN,
    SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN,
    SCOPE_DOCUMENTEN_BIJWERKEN,
    SCOPE_DOCUMENTEN_GEFORCEERD_BIJWERKEN,
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
from drc.api.serializers.enkelvoudig_informatieobject import (
    EIOZoekSerializer,
    SchemaEIOSerializer,
)
from drc.api.views.constants import REGISTRATIE_QUERY_PARAM, VERSIE_QUERY_PARAM
from drc.datamodel.models import EnkelvoudigInformatieObject

PATH_PARAMETER_NAME = "enkelvoudiginformatieobject_uuid"
PATH_PARAMETER_DESCRIPTION = "Unieke resource identifier (UUID4)"


@conditional_retrieve()
@extend_schema_view(
    list=extend_schema(
        summary=_("Alle (ENKELVOUDIGe) INFORMATIEOBJECTen opvragen."),
        description=_(
            "Deze lijst kan gefilterd wordt met query-string parameters. \n"
            "De objecten bevatten metadata over de documenten en de downloadlink "
            "(`inhoud`) naar de binary data. Alleen de laatste versie van elk"
            "(ENKELVOUDIG) INFORMATIEOBJECT wordt getoond. Specifieke versies kunnen "
            "alleen"
        ),
    ),
    retrieve=extend_schema(
        summary=_("Een specifiek (ENKELVOUDIG) INFORMATIEOBJECT opvragen."),
        description=_(
            " Het object bevat metadata over het document en de downloadlink (`inhoud`)"
            " naar de binary data. Dit geeft standaard de laatste versie van het "
            "(ENKELVOUDIG) INFORMATIEOBJECT. Specifieke versies kunnen middels "
            "query-string parameters worden opgevraagd."
        ),
    ),
    create=extend_schema(
        summary=_("Maak een (ENKELVOUDIG) INFORMATIEOBJECT aan."),
        description=_(
            "**Er wordt gevalideerd op** \n"
            " - geldigheid `informatieobjecttype` URL - de resource moet opgevraagd kunnen "
            "worden uit de catalogi API en de vorm van een INFORMATIEOBJECTTYPE hebben. \n"
            "- publicatie `informatieobjecttype` - `concept` moet `false` zijn"
        ),
    ),
    update=extend_schema(
        summary=_("Werk een (ENKELVOUDIG) INFORMATIEOBJECT in zijn geheel bij."),
        description=_(
            "Dit creëert altijd een nieuwe versie van het (ENKELVOUDIG) INFORMATIEOBJECT. \n"
            " \n**Er wordt gevalideerd op**\n"
            "- correcte `lock` waarde\n"
            "- status NIET `definitief`"
        ),
    ),
    partial_update=extend_schema(
        summary=_("Werk een (ENKELVOUDIG) INFORMATIEOBJECT deels bij."),
        description=_(
            "Dit creëert altijd een nieuwe versie van het (ENKELVOUDIG) INFORMATIEOBJECT. \n"
            "\n**Er wordt gevalideerd op**\n"
            " - correcte `lock` waarde\n"
            " - status NIET `definitief`"
        ),
    ),
    destroy=extend_schema(
        summary=_("Verwijder een (ENKELVOUDIG) INFORMATIEOBJECT."),
        description=_(
            "Verwijder een (ENKELVOUDIG) INFORMATIEOBJECT en alle bijbehorende versies,"
            " samen met alle gerelateerde resources binnen deze API. Dit is alleen mogelijk"
            " als er geen OBJECTINFORMATIEOBJECTen relateerd zijn aan het (ENKELVOUDIG) INFORMATIEOBJECT.\n"
            "\n**Gerelateerde resources**\n"
            "- GEBRUIKSRECHTen\n"
            "- audit trail regels"
        ),
    ),
    download=extend_schema(
        summary=_("Download de binaire data van het (ENKELVOUDIG) INFORMATIEOBJECT."),
        description=_(
            "Download de binaire data van het (ENKELVOUDIG) INFORMATIEOBJECT."
        ),
    ),
    lock=extend_schema(
        summary=_("Vergrendel een (ENKELVOUDIG) INFORMATIEOBJECT."),
        description=_(
            "Voert een 'checkout' uit waardoor het (ENKELVOUDIG) INFORMATIEOBJECT"
            "vergrendeld wordt met een `lock` waarde. Alleen met deze waarde kan het"
            "(ENKELVOUDIG) INFORMATIEOBJECT bijgewerkt (`PUT`, `PATCH`) en weer"
            "ontgrendeld worden."
        ),
    ),
    unlock=extend_schema(
        summary=_("Ontgrendel een (ENKELVOUDIG) INFORMATIEOBJECT."),
        description=_(
            "Heft de 'checkout' op waardoor het (ENKELVOUDIG) INFORMATIEOBJECT"
            "ontgrendeld wordt."
        ),
    ),
)
class EnkelvoudigInformatieObjectViewSet(
    NotificationViewSetMixin,
    CheckQueryParamsMixin,
    SearchMixin,
    ListFilterByAuthorizationsMixin,
    AuditTrailViewsetMixin,
    ExpandFieldValidator,
    ExpansionMixin,
    viewsets.ModelViewSet,
):
    global_description = _(
        "Opvragen en bewerken van (ENKELVOUDIG) INFORMATIEOBJECTen (documenten)."
    )
    queryset = EnkelvoudigInformatieObject.objects.order_by(
        "canonical", "-versie"
    ).distinct("canonical")
    lookup_field = "uuid"
    pagination_class = PageNumberPagination
    search_input_serializer_class = EIOZoekSerializer
    serializer_class = EnkelvoudigInformatieObjectSerializer
    permission_classes = (InformationObjectAuthScopesRequired,)
    required_scopes = {
        "list": SCOPE_DOCUMENTEN_ALLES_LEZEN,
        "retrieve": SCOPE_DOCUMENTEN_ALLES_LEZEN,
        "_zoek": SCOPE_DOCUMENTEN_ALLES_LEZEN,
        "create": SCOPE_DOCUMENTEN_AANMAKEN,
        "destroy": SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN,
        "update": SCOPE_DOCUMENTEN_BIJWERKEN | SCOPE_DOCUMENTEN_GEFORCEERD_BIJWERKEN,
        "partial_update": SCOPE_DOCUMENTEN_BIJWERKEN
        | SCOPE_DOCUMENTEN_GEFORCEERD_BIJWERKEN,
        "download": SCOPE_DOCUMENTEN_ALLES_LEZEN,
        "lock": SCOPE_DOCUMENTEN_LOCK,
        "unlock": SCOPE_DOCUMENTEN_LOCK | SCOPE_DOCUMENTEN_GEFORCEERD_UNLOCK,
    }
    notifications_kanaal = KANAAL_DOCUMENTEN
    audit = AUDIT_DRC

    swagger_schema = EIOAutoSchema

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.action in ["update", "partial_update"]:
            instance = self.get_object()
            force_bijwerken = False
            if self.request.jwt_auth.has_auth(
                scopes=SCOPE_DOCUMENTEN_GEFORCEERD_BIJWERKEN,
                informatieobjecttype=instance.informatieobjecttype,
                vertrouwelijkheidaanduiding=instance.vertrouwelijkheidaanduiding,
            ):
                force_bijwerken = True
            context.update({"force_bijwerken": force_bijwerken})

        return context

    def get_renderers(self):
        if self.action == "download":
            return [BinaryFileRenderer]
        return super().get_renderers()

    @extend_schema(
        summary=_("Voer een zoekopdracht uit op (ENKELVOUDIG) INFORMATIEOBJECTen."),
        description=_(
            "Zoeken/filteren gaat normaal via de `list` operatie, deze is echter niet geschikt voor zoekopdrachten met UUIDs."
        ),
    )
    @action(methods=("post",), detail=False)
    def _zoek(self, request, *args, **kwargs):
        search_input = self.get_search_input()
        queryset = self.filter_queryset(self.get_queryset())
        for name, value in search_input.items():
            queryset = queryset.filter(**{name: value})

        return self.get_search_output(queryset)

    _zoek.is_search_action = True

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
        if instance.canonical.lock:
            raise serializers.ValidationError(
                {"field_error": _("Locked objects cannot be destroyed")},
                code="destroy-locked",
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

    def get_serializer_class(self, *args, **kwargs):
        """
        To validate that a lock id is sent only with PUT and PATCH operations
        """
        if self.action in ["update", "partial_update"]:
            return EnkelvoudigInformatieObjectWithLockSerializer
        if self.action == "create":
            return EnkelvoudigInformatieObjectCreateLockSerializer
        return EnkelvoudigInformatieObjectSerializer

    @extend_schema(
        parameters=[VERSIE_QUERY_PARAM, REGISTRATIE_QUERY_PARAM, EXPAND_QUERY_PARAM],
        responses=SchemaEIOSerializer,
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        responses=SchemaEIOSerializer,
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    @extend_schema(
        # see https://swagger.io/docs/specification/2-0/describing-responses/ and
        # https://swagger.io/docs/specification/2-0/mime-types/
        # OAS 3 has a better mechanism: https://swagger.io/docs/specification/describing-responses/
        methods=["get"],
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description=_("De binaire bestandsinhoud"),
                response=OpenApiTypes.BINARY,
            ),
            status.HTTP_401_UNAUTHORIZED: FoutSerializer,
            status.HTTP_403_FORBIDDEN: FoutSerializer,
            status.HTTP_404_NOT_FOUND: FoutSerializer,
            status.HTTP_406_NOT_ACCEPTABLE: FoutSerializer,
            status.HTTP_410_GONE: FoutSerializer,
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: FoutSerializer,
            status.HTTP_429_TOO_MANY_REQUESTS: FoutSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: FoutSerializer,
        },
        parameters=[VERSIE_QUERY_PARAM, REGISTRATIE_QUERY_PARAM],
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

    @extend_schema(
        request=LockEnkelvoudigInformatieObjectSerializer,
        responses={
            status.HTTP_200_OK: LockEnkelvoudigInformatieObjectSerializer,
            status.HTTP_400_BAD_REQUEST: FoutSerializer,
            status.HTTP_401_UNAUTHORIZED: FoutSerializer,
            status.HTTP_403_FORBIDDEN: FoutSerializer,
            status.HTTP_404_NOT_FOUND: FoutSerializer,
            status.HTTP_406_NOT_ACCEPTABLE: FoutSerializer,
            status.HTTP_410_GONE: FoutSerializer,
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: FoutSerializer,
            status.HTTP_429_TOO_MANY_REQUESTS: FoutSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: FoutSerializer,
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

    @extend_schema(
        request=UnlockEnkelvoudigInformatieObjectSerializer,
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description=_("No content")),
            status.HTTP_400_BAD_REQUEST: FoutSerializer,
            status.HTTP_401_UNAUTHORIZED: FoutSerializer,
            status.HTTP_403_FORBIDDEN: FoutSerializer,
            status.HTTP_404_NOT_FOUND: FoutSerializer,
            status.HTTP_406_NOT_ACCEPTABLE: FoutSerializer,
            status.HTTP_410_GONE: FoutSerializer,
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: FoutSerializer,
            status.HTTP_429_TOO_MANY_REQUESTS: FoutSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: FoutSerializer,
        },
    )
    @action(detail=True, methods=["post"])
    def unlock(self, request, *args, **kwargs):
        eio = self.get_object()
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


@extend_schema(
    parameters=[
        OpenApiParameter(
            name=PATH_PARAMETER_NAME,
            type=str,
            location=OpenApiParameter.PATH,
            description=PATH_PARAMETER_DESCRIPTION,
        ),
    ]
)
@extend_schema_view(
    list=extend_schema(
        summary=_("Alle audit trail regels behorend bij het INFORMATIEOBJECT."),
        description=_("Alle audit trail regels behorend bij het INFORMATIEOBJECT."),
    ),
    retrieve=extend_schema(
        summary=_("Een specifieke audit trail regel opvragen."),
        description=_("Een specifieke audit trail regel opvragen."),
    ),
)
class EnkelvoudigInformatieObjectAuditTrailViewSet(AuditTrailViewSet):
    main_resource_lookup_field = "enkelvoudiginformatieobject_uuid"
    global_description = "Opvragen van de audit trail regels."

    def initialize_request(self, request, *args, **kwargs):
        # workaround for drf-nested-viewset injecting the URL kwarg into request.data
        return super(viewsets.ReadOnlyModelViewSet, self).initialize_request(
            request, *args, **kwargs
        )
