"""
Serializers of the Document Registratie Component REST API
"""
from django.conf import settings
from django.utils.encoding import force_text
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _

from drf_extra_fields.fields import Base64FileField
from rest_framework import serializers
from rest_framework.settings import api_settings
from vng_api_common.constants import ObjectTypes
from vng_api_common.models import APICredential
from vng_api_common.serializers import GegevensGroepSerializer
from vng_api_common.validators import IsImmutableValidator, URLValidator

from drc.datamodel.constants import RelatieAarden
from drc.datamodel.models import (
    EnkelvoudigInformatieObject, Gebruiksrechten, ObjectInformatieObject
)
from drc.sync.signals import SyncError

from .auth import get_zrc_auth, get_ztc_auth
from .validators import StatusValidator


class AnyFileType:
    def __contains__(self, item):
        return True


class AnyBase64File(Base64FileField):
    ALLOWED_TYPES = AnyFileType()

    def get_file_extension(self, filename, decoded_file):
        return "bin"


class IntegriteitSerializer(GegevensGroepSerializer):
    class Meta:
        model = EnkelvoudigInformatieObject
        gegevensgroep = 'integriteit'


class OndertekeningSerializer(GegevensGroepSerializer):
    class Meta:
        model = EnkelvoudigInformatieObject
        gegevensgroep = 'ondertekening'


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
        help_text=_("Uitdrukking van mate van volledigheid en onbeschadigd zijn van digitaal bestand.")
    )
    # TODO: validator!
    ondertekening = OndertekeningSerializer(
        label=_("ondertekening"), allow_null=True, required=False,
        help_text=_("Aanduiding van de rechtskracht van een informatieobject. Mag niet van een waarde "
                    "zijn voorzien als de `status` de waarde 'in bewerking' of 'ter vaststelling' heeft.")
    )

    class Meta:
        model = EnkelvoudigInformatieObject
        fields = (
            'url',
            'identificatie',
            'bronorganisatie',
            'creatiedatum',
            'titel',
            'vertrouwelijkheidaanduiding',
            'auteur',
            'status',
            'formaat',
            'taal',
            'bestandsnaam',
            'inhoud',
            'bestandsomvang',
            'link',
            'beschrijving',
            'ontvangstdatum',
            'verzenddatum',
            'indicatie_gebruiksrecht',
            'ondertekening',
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
        validators = [StatusValidator()]

    def _get_informatieobjecttype(self, informatieobjecttype_url: str) -> dict:
        if not hasattr(self, 'informatieobjecttype'):
            # dynamic so that it can be mocked in tests easily
            Client = import_string(settings.ZDS_CLIENT_CLASS)
            client = Client.from_url(informatieobjecttype_url)
            client.auth = APICredential.get_auth(
                informatieobjecttype_url,
                scopes=['zds.scopes.zaaktypes.lezen']
            )
            self._informatieobjecttype = client.request(informatieobjecttype_url, 'informatieobjecttype')
        return self._informatieobjecttype

    def validate_indicatie_gebruiksrecht(self, indicatie):
        if self.instance and not indicatie and self.instance.gebruiksrechten_set.exists():
            raise serializers.ValidationError(
                _("De indicatie kan niet weggehaald worden of ongespecifieerd "
                  "zijn als er Gebruiksrechten gedefinieerd zijn."),
                code='existing-gebruiksrechten'
            )
        # create: not self.instance or update: usage_rights exists
        elif indicatie and (not self.instance or not self.instance.gebruiksrechten_set.exists()):
            raise serializers.ValidationError(
                _("De indicatie moet op 'ja' gezet worden door `gebruiksrechten` "
                  "aan te maken, dit kan niet direct op deze resource."),
                code='missing-gebruiksrechten'
            )
        return indicatie

    def create(self, validated_data):
        """
        Handle nested writes.
        """
        integriteit = validated_data.pop('integriteit', None)
        ondertekening = validated_data.pop('ondertekening', None)
        # add vertrouwelijkheidaanduiding
        if 'vertrouwelijkheidaanduiding' not in validated_data:
            informatieobjecttype = self._get_informatieobjecttype(validated_data['informatieobjecttype'])
            validated_data['vertrouwelijkheidaanduiding'] = informatieobjecttype['vertrouwelijkheidaanduiding']

        eio = super().create(validated_data)
        eio.integriteit = integriteit
        eio.ondertekening = ondertekening
        eio.save()
        return eio

    def update(self, instance, validated_data):
        """
        Handle nested writes.
        """
        instance.integriteit = validated_data.pop('integriteit', None)
        instance.ondertekening = validated_data.pop('ondertekening', None)
        return super().update(instance, validated_data)

    def _replace_file_url(self, output: dict) -> None:
        if 'inhoud' in output:
            output['inhoud'] = f"{output['url']}/download"

    def to_representation(self, instance):
        # replace inhound url
        results = super().to_representation(instance)
        if isinstance(results, list):
            for result in results:
                self._replace_file_url(result)
        else:
            self._replace_file_url(results)
        return results


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


class GebruiksrechtenSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Gebruiksrechten
        fields = (
            'url',
            'informatieobject',
            'startdatum',
            'einddatum',
            'omschrijving_voorwaarden'
        )
        extra_kwargs = {
            'url': {
                'lookup_field': 'uuid',
            },
            'informatieobject': {
                'lookup_field': 'uuid',
                'validators': [IsImmutableValidator()],
            },
        }
