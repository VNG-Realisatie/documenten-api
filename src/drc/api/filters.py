from zds_schema.filtersets import FilterSet

from drc.datamodel.models import Gebruiksrechten, ObjectInformatieObject


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
