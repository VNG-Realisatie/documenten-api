from zds_schema.filtersets import FilterSet

from drc.datamodel.models import ObjectInformatieObject


class ObjectInformatieObjectFilter(FilterSet):
    class Meta:
        model = ObjectInformatieObject
        fields = (
            'object',
            'informatieobject',
        )
