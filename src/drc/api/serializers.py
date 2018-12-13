"""
Serializers of the Document Registratie Component REST API
"""
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from drf_extra_fields.fields import Base64FileField
from rest_framework import serializers
from rest_framework.settings import api_settings
from zds_schema.constants import ObjectTypes
from zds_schema.validators import IsImmutableValidator, URLValidator

from drc.datamodel.constants import ChecksumAlgoritmes, RelatieAarden
from drc.datamodel.models import (
    EnkelvoudigInformatieObject, ObjectInformatieObject
)
from drc.sync.signals import SyncError

from .auth import get_zrc_auth, get_ztc_auth


class AnyFileType:
    def __contains__(self, item):
        return True


class AnyBase64File(Base64FileField):
    ALLOWED_TYPES = AnyFileType()

    def get_file_extension(self, filename, decoded_file):
        return "bin"


class IntegriteitSerializer(serializers.Serializer):
    algoritme = serializers.ChoiceField(
        label=_("algoritme"), choices=ChecksumAlgoritmes.choices,
        help_text=EnkelvoudigInformatieObject._meta.get_field('integriteit_algoritme').help_text
    )
    waarde = serializers.CharField(
        label=_("waarde"),
        max_length=EnkelvoudigInformatieObject._meta.get_field('integriteit_waarde').max_length,
        help_text=EnkelvoudigInformatieObject._meta.get_field('integriteit_waarde').help_text
    )
    datum = serializers.DateField(
        label=_("datum"),
        help_text=EnkelvoudigInformatieObject._meta.get_field('integriteit_datum').help_text,
    )


class EnkelvoudigInformatieObjectSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the EnkelvoudigInformatieObject model
    """
    inhoud = AnyBase64File()
    bestandsomvang = serializers.IntegerField(
        source='inhoud.size', read_only=True,
        min_value=0
    )
    integriteit = IntegriteitSerializer(
        label=_("integriteit"), allow_null=True, required=False,
        help_text=_("Uitdrukking van mate van volledigheid en onbeschadigd zijn van digitaal bestand")
    )

    class Meta:
        model = EnkelvoudigInformatieObject
        fields = (
            'url',
            'identificatie',
            'bronorganisatie',
            'creatiedatum',
            'titel',
            'vertrouwelijkaanduiding',
            'auteur',
            'formaat',
            'taal',
            'bestandsnaam',
            'inhoud',
            'bestandsomvang',
            'link',
            'beschrijving',
            'integriteit',

            'informatieobjecttype'  # van-relatie
        )
        extra_kwargs = {
            'url': {
                'lookup_field': 'uuid',
            },
            'informatieobjecttype': {
                'validators': [URLValidator(get_auth=get_ztc_auth)],
            }
        }

    def create(self, validated_data):
        """
        Handle nested writes.
        """
        integriteit = validated_data.pop('integriteit', None)
        eio = super().create(validated_data)
        eio.integriteit = integriteit
        eio.save()
        return eio

    def update(self, instance, validated_data):
        """
        Handle nested writes.
        """
        instance.integriteit = validated_data.pop('integriteit', None)
        return super().update(instance, validated_data)


class ObjectInformatieObjectSerializer(serializers.HyperlinkedModelSerializer):
    aard_relatie_weergave = serializers.ChoiceField(
        source='get_aard_relatie_display', read_only=True,
        choices=[(force_text(value), key) for key, value in RelatieAarden.choices]
    )

    # TODO: valideer dat ObjectInformatieObject.informatieobjecttype hoort
    # bij zaak.zaaktype
    class Meta:
        model = ObjectInformatieObject
        fields = (
            'url',
            'informatieobject',
            'object',
            'object_type',
            'aard_relatie_weergave',
            'titel',
            'beschrijving',
            'registratiedatum',
        )
        extra_kwargs = {
            'url': {
                'lookup_field': 'uuid',
            },
            'informatieobject': {
                'lookup_field': 'uuid',
                'validators': [IsImmutableValidator()],
            },
            'object': {
                'validators': [
                    URLValidator(get_auth=get_zrc_auth, headers={'Accept-Crs': 'EPSG:4326'}),
                    IsImmutableValidator(),
                ],
            },
            'object_type': {
                'validators': [IsImmutableValidator()]
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not hasattr(self, 'initial_data'):
            return

        object_type = self.initial_data.get('object_type')

        if object_type == ObjectTypes.besluit:
            del self.fields['titel']
            del self.fields['beschrijving']
            del self.fields['registratiedatum']

    def save(self, **kwargs):
        # can't slap a transaction atomic on this, since ZRC/BRC query for the
        # relation!
        try:
            return super().save(**kwargs)
        except SyncError as sync_error:
            # delete the object again
            ObjectInformatieObject.objects.filter(
                informatieobject=self.validated_data['informatieobject'],
                object=self.validated_data['object']
            )._raw_delete('default')
            raise serializers.ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: sync_error.args[0]
            }) from sync_error
