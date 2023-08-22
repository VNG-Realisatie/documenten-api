from django.utils.translation import ugettext_lazy as _

from django_filters import rest_framework as filters
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from vng_api_common.filters import URLModelChoiceFilter
from vng_api_common.filtersets import FilterSet
from vng_api_common.utils import get_help_text

from drc.datamodel.models import (
    EnkelvoudigInformatieObject,
    EnkelvoudigInformatieObjectCanonical,
    Gebruiksrechten,
    ObjectInformatieObject,
    Verzending,
)


def expand_filter(queryset, name, value):
    """expansion filter logic is placed at view level"""
    return queryset


class EnkelvoudigInformatieObjectListFilter(FilterSet):
    trefwoorden = filters.CharFilter(lookup_expr="icontains")

    expand = extend_schema_field(OpenApiTypes.STR)(
        filters.CharFilter(
            method=expand_filter,
            help_text=_(
                "Examples: \n"
                "`expand=zaaktype, status, status.statustype, hoofdzaak.status.statustype, hoofdzaak.deelzaken.status.statustype`\n"
                "Haal details van gelinkte resources direct op. Als je meerdere resources tegelijk wilt ophalen kun je deze scheiden met een komma. Voor het ophalen van resources die een laag dieper genest zijn wordt de punt-notatie gebruikt.",
            ),
        )
    )

    class Meta:
        model = EnkelvoudigInformatieObject
        fields = ("identificatie", "bronorganisatie", "trefwoorden")


class EnkelvoudigInformatieObjectDetailFilter(FilterSet):
    versie = filters.NumberFilter(field_name="versie")
    registratie_op = filters.IsoDateTimeFilter(
        field_name="begin_registratie", lookup_expr="lte", label="begin_registratie"
    )


class ObjectInformatieObjectFilter(FilterSet):
    informatieobject = URLModelChoiceFilter(
        queryset=EnkelvoudigInformatieObjectCanonical.objects.all(),
        instance_path="canonical",
        help_text=get_help_text("datamodel.ObjectInformatieObject", "informatieobject"),
    )
    expand = extend_schema_field(OpenApiTypes.STR)(
        filters.CharFilter(
            method=expand_filter,
            help_text=_(
                "Examples: \n"
                "`expand=zaaktype, status, status.statustype, hoofdzaak.status.statustype, hoofdzaak.deelzaken.status.statustype`\n"
                "Haal details van gelinkte resources direct op. Als je meerdere resources tegelijk wilt ophalen kun je deze scheiden met een komma. Voor het ophalen van resources die een laag dieper genest zijn wordt de punt-notatie gebruikt.",
            ),
        )
    )

    class Meta:
        model = ObjectInformatieObject
        fields = ("object", "informatieobject")


class GebruiksrechtenFilter(FilterSet):
    informatieobject = URLModelChoiceFilter(
        queryset=EnkelvoudigInformatieObjectCanonical.objects.all(),
        instance_path="canonical",
        help_text=get_help_text("datamodel.Gebruiksrechten", "informatieobject"),
    )
    expand = extend_schema_field(OpenApiTypes.STR)(
        filters.CharFilter(
            method=expand_filter,
            help_text=_(
                "Examples: \n"
                "`expand=zaaktype, status, status.statustype, hoofdzaak.status.statustype, hoofdzaak.deelzaken.status.statustype`\n"
                "Haal details van gelinkte resources direct op. Als je meerdere resources tegelijk wilt ophalen kun je deze scheiden met een komma. Voor het ophalen van resources die een laag dieper genest zijn wordt de punt-notatie gebruikt.",
            ),
        )
    )

    class Meta:
        model = Gebruiksrechten
        fields = {
            "informatieobject": ["exact"],
            "startdatum": ["lt", "lte", "gt", "gte"],
            "einddatum": ["lt", "lte", "gt", "gte"],
        }


class VerzendingFilter(FilterSet):
    informatieobject = URLModelChoiceFilter(
        queryset=EnkelvoudigInformatieObjectCanonical.objects.all(),
        instance_path="canonical",
        help_text=get_help_text("datamodel.Verzending", "informatieobject"),
    )
    expand = extend_schema_field(OpenApiTypes.STR)(
        filters.CharFilter(
            method=expand_filter,
            help_text=_(
                "Examples: \n"
                "`expand=zaaktype, status, status.statustype, hoofdzaak.status.statustype, hoofdzaak.deelzaken.status.statustype`\n"
                "Haal details van gelinkte resources direct op. Als je meerdere resources tegelijk wilt ophalen kun je deze scheiden met een komma. Voor het ophalen van resources die een laag dieper genest zijn wordt de punt-notatie gebruikt.",
            ),
        )
    )

    class Meta:
        model = Verzending
        fields = {
            "aard_relatie": ["exact"],
            "informatieobject": ["exact"],
            "betrokkene": ["exact"],
        }
