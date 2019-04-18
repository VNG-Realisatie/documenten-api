from vng_api_common.filtersets import FilterSet

from drc.datamodel.models import (
    EnkelvoudigInformatieObject, Gebruiksrechten, ObjectInformatieObject
)


class EnkelvoudigInformatieObjectFilter(FilterSet):
    class Meta:
        model = EnkelvoudigInformatieObject
        fields = (
            'identificatie',
            'bronorganisatie'
        )


class ObjectInformatieObjectFilter(FilterSet):
    class Meta:
        model = ObjectInformatieObject
        fields = (
            'object',
            'informatieobject',
        )


class GebruiksrechtenFilter(FilterSet):
    class Meta:
        model = Gebruiksrechten
        fields = {
            'informatieobject': ['exact'],
            'startdatum': ['lt', 'lte', 'gt', 'gte'],
            'einddatum': ['lt', 'lte', 'gt', 'gte'],
        }
