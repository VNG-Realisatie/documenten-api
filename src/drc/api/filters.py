from django_filters import rest_framework as filters
from vng_api_common.filters import URLModelChoiceFilter
from vng_api_common.filtersets import FilterSet

from drc.datamodel.models import (
    EnkelvoudigInformatieObject, EnkelvoudigInformatieObjectCanonical,
    Gebruiksrechten, ObjectInformatieObject
)


class EnkelvoudigInformatieObjectListFilter(FilterSet):
    class Meta:
        model = EnkelvoudigInformatieObject
        fields = (
            'identificatie',
            'bronorganisatie',
        )


class EnkelvoudigInformatieObjectDetailFilter(FilterSet):
    versie = filters.NumberFilter(field_name='versie')
    registratie_op = filters.IsoDateTimeFilter(
        field_name='begin_registratie',
        lookup_expr='lte',
        label='begin_registratie',
    )


class ObjectInformatieObjectFilter(FilterSet):
    informatieobject = URLModelChoiceFilter(
        queryset=EnkelvoudigInformatieObjectCanonical.objects.all(),
        instance_path='canonical'
    )

    class Meta:
        model = ObjectInformatieObject
        fields = (
            'object',
            'informatieobject',
        )


class GebruiksrechtenFilter(FilterSet):
    informatieobject = URLModelChoiceFilter(
        queryset=EnkelvoudigInformatieObjectCanonical.objects.all(),
        instance_path='canonical'
    )

    class Meta:
        model = Gebruiksrechten
        fields = {
            'informatieobject': ['exact'],
            'startdatum': ['lt', 'lte', 'gt', 'gte'],
            'einddatum': ['lt', 'lte', 'gt', 'gte'],
        }
