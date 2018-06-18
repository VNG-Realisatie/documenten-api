from rest_framework import serializers

from drc.datamodel.models import EnkelvoudigInformatieObject


class EnkelvoudigInformatieObjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EnkelvoudigInformatieObject
        fields = (
            'informatieobjectidentificatie',
            'bronorganisatie',
            'creatiedatum',
            'titel',
            'auteur',
            'formaat',
            'taal',
            'inhoud'
        )
