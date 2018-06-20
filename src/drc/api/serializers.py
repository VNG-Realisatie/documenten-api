from rest_framework import serializers

from drc.datamodel.models import EnkelvoudigInformatieObject


class EnkelvoudigInformatieObjectSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = EnkelvoudigInformatieObject
        fields = (
            'url',
            'identificatie',
            'bronorganisatie',
            'creatiedatum',
            'titel',
            'auteur',
            'formaat',
            'taal',
            'inhoud'
        )
