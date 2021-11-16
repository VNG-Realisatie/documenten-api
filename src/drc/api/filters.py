from django.db.models import Q

from django_filters import rest_framework as filters
from django_filters.constants import EMPTY_VALUES
from vng_api_common.filters import URLModelChoiceFilter
from vng_api_common.filtersets import FilterSet
from vng_api_common.utils import get_help_text

from drc.datamodel.models import (
    EnkelvoudigInformatieObject,
    EnkelvoudigInformatieObjectCanonical,
    Gebruiksrechten,
    ObjectInformatieObject,
)


class ObjectFilter(filters.BaseCSVFilter):
    """
    Allow filtering of ENKELVOUDIGINFORMATIEOBJECTen by objects they are related
    to (through the OBJECTINFORMATIEOBJECT resource)
    """

    def filter(self, qs, values):
        if values in EMPTY_VALUES:
            return qs

        if self.distinct:
            qs = qs.distinct()

        lookups = Q()
        for value in values:
            lookups |= Q(object=value)

        oios = ObjectInformatieObject.objects.filter(lookups)
        qs = self.get_method(qs)(
            canonical__id__in=list(oios.values_list("informatieobject__id", flat=True))
        )
        return qs


class EnkelvoudigInformatieObjectListFilter(FilterSet):
    object = ObjectFilter(
        help_text=(
            "De URL van het gerelateerde object "
            "(zoals vastgelegd in de OBJECTINFORMATIEOBJECT resource). "
            "Meerdere waardes kunnen met komma's gescheiden worden."
        )
    )

    class Meta:
        model = EnkelvoudigInformatieObject
        fields = ("identificatie", "bronorganisatie", "object")


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

    class Meta:
        model = ObjectInformatieObject
        fields = ("object", "informatieobject")


class GebruiksrechtenFilter(FilterSet):
    informatieobject = URLModelChoiceFilter(
        queryset=EnkelvoudigInformatieObjectCanonical.objects.all(),
        instance_path="canonical",
        help_text=get_help_text("datamodel.Gebruiksrechten", "informatieobject"),
    )

    class Meta:
        model = Gebruiksrechten
        fields = {
            "informatieobject": ["exact"],
            "startdatum": ["lt", "lte", "gt", "gte"],
            "einddatum": ["lt", "lte", "gt", "gte"],
        }
