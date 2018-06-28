import os

from drf_extra_fields.fields import Base64FileField
from rest_framework import serializers

from drc.datamodel.models import EnkelvoudigInformatieObject


class AnyFileType:
    def __contains__(self, item):
        return True


class AnyBase64File(Base64FileField):
    ALLOWED_TYPES = AnyFileType()

    def get_file_extension(self, filename, decoded_file):
        filename, file_extension = os.path.splitext(filename)
        return file_extension


class EnkelvoudigInformatieObjectSerializer(serializers.HyperlinkedModelSerializer):

    inhoud = AnyBase64File()

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
