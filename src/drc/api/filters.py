from zds_schema.filtersets import FilterSet

from drc.datamodel.models import ZaakInformatieObject


class ZaakInformatieObjectFilter(FilterSet):
    class Meta:
        model = ZaakInformatieObject
        fields = (
            'zaak',
            'informatieobject',
        )
