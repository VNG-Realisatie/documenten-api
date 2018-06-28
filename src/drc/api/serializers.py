import os

from drf_extra_fields.fields import Base64FileField
from rest_framework import serializers

from drc.datamodel.models import EnkelvoudigInformatieObject


class CustomBase64File(Base64FileField):
    ALLOWED_TYPES = ['txt', 'png', 'jpg', '']

    def get_file_extension(self, filename, decoded_file):
        filename, file_extension = os.path.splitext(filename)
        return file_extension


class EnkelvoudigInformatieObjectSerializer(serializers.HyperlinkedModelSerializer):

    inhoud = CustomBase64File()

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
