import math
import os
import uuid

from django.conf import settings
from django.core.files.base import ContentFile, File
from django.db import transaction
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from vng_api_common.constants import VertrouwelijkheidsAanduiding
from vng_api_common.models import APICredential
from vng_api_common.serializers import (
    GegevensGroepSerializer,
    add_choice_values_help_text,
)
from vng_api_common.validators import IsImmutableValidator, PublishValidator

from drc.api.auth import get_ztc_auth
from drc.api.fields import AnyBase64File
from drc.api.serializers.bestandsdeel import BestandsDeelSerializer
from drc.api.utils import create_filename, merge_files
from drc.api.validators import StatusValidator
from drc.datamodel.constants import ChecksumAlgoritmes, OndertekeningSoorten, Statussen
from drc.datamodel.models import (
    EnkelvoudigInformatieObject,
    EnkelvoudigInformatieObjectCanonical,
)
from drc.datamodel.models.bestandsdeel import BestandsDeel


class IntegriteitSerializer(GegevensGroepSerializer):
    class Meta:
        model = EnkelvoudigInformatieObject
        gegevensgroep = "integriteit"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        value_display_mapping = add_choice_values_help_text(ChecksumAlgoritmes)
        self.fields["algoritme"].help_text += f"\n\n{value_display_mapping}"


class OndertekeningSerializer(GegevensGroepSerializer):
    class Meta:
        model = EnkelvoudigInformatieObject
        gegevensgroep = "ondertekening"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        value_display_mapping = add_choice_values_help_text(OndertekeningSoorten)
        self.fields["soort"].help_text += f"\n\n{value_display_mapping}"


class EnkelvoudigInformatieObjectSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the EnkelvoudigInformatieObject model
    """

    url = serializers.HyperlinkedIdentityField(
        view_name="enkelvoudiginformatieobject-detail", lookup_field="uuid"
    )
    inhoud = AnyBase64File(
        view_name="enkelvoudiginformatieobject-download",
        required=False,
        allow_null=True,
    )
    integriteit = IntegriteitSerializer(
        label=_("integriteit"),
        allow_null=True,
        required=False,
        help_text=_(
            "Uitdrukking van mate van volledigheid en onbeschadigd zijn van digitaal bestand."
        ),
    )
    # TODO: validator!
    ondertekening = OndertekeningSerializer(
        label=_("ondertekening"),
        allow_null=True,
        required=False,
        help_text=_(
            "Aanduiding van de rechtskracht van een informatieobject. Mag niet van een waarde "
            "zijn voorzien als de `status` de waarde 'in bewerking' of 'ter vaststelling' heeft."
        ),
    )
    locked = serializers.BooleanField(
        label=_("locked"),
        read_only=True,
        source="canonical.lock",
        help_text=_(
            "Geeft aan of het document gelocked is. Alleen als een document gelocked is, "
            "mogen er aanpassingen gemaakt worden."
        ),
    )
    bestandsdelen = BestandsDeelSerializer(
        source="canonical.bestandsdelen", many=True, read_only=True
    )

    class Meta:
        model = EnkelvoudigInformatieObject
        fields = (
            "url",
            "identificatie",
            "bronorganisatie",
            "creatiedatum",
            "titel",
            "vertrouwelijkheidaanduiding",
            "auteur",
            "status",
            "formaat",
            "taal",
            "versie",
            "begin_registratie",
            "bestandsnaam",
            "inhoud",
            "bestandsomvang",
            "link",
            "beschrijving",
            "ontvangstdatum",
            "verzenddatum",
            "indicatie_gebruiksrecht",
            "verschijningsvorm",
            "ondertekening",
            "integriteit",
            "informatieobjecttype",  # van-relatie,
            "locked",
            "bestandsdelen",
        )
        extra_kwargs = {
            "informatieobjecttype": {
                "validators": [
                    PublishValidator(
                        "InformatieObjectType",
                        settings.ZTC_API_SPEC,
                        get_auth=get_ztc_auth,
                    ),
                ]
            },
            "taal": {"min_length": 3},
        }
        read_only_fields = ["versie", "begin_registratie"]
        validators = [StatusValidator()]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        value_display_mapping = add_choice_values_help_text(
            VertrouwelijkheidsAanduiding
        )
        self.fields[
            "vertrouwelijkheidaanduiding"
        ].help_text += f"\n\n{value_display_mapping}"

        value_display_mapping = add_choice_values_help_text(Statussen)
        self.fields["status"].help_text += f"\n\n{value_display_mapping}"

    def _get_informatieobjecttype(self, informatieobjecttype_url: str) -> dict:
        if not hasattr(self, "informatieobjecttype"):
            # dynamic so that it can be mocked in tests easily
            Client = import_string(settings.ZDS_CLIENT_CLASS)
            client = Client.from_url(informatieobjecttype_url)
            client.auth = APICredential.get_auth(
                informatieobjecttype_url, scopes=["zds.scopes.zaaktypes.lezen"]
            )
            self._informatieobjecttype = client.request(
                informatieobjecttype_url, "informatieobjecttype"
            )
        return self._informatieobjecttype

    def validate_indicatie_gebruiksrecht(self, indicatie):
        if (
            self.instance
            and not indicatie
            and self.instance.canonical.gebruiksrechten_set.exists()
        ):
            raise serializers.ValidationError(
                _(
                    "De indicatie kan niet weggehaald worden of ongespecifieerd "
                    "zijn als er Gebruiksrechten gedefinieerd zijn."
                ),
                code="existing-gebruiksrechten",
            )
        # create: not self.instance or update: usage_rights exists
        elif indicatie and (
            not self.instance
            or not self.instance.canonical.gebruiksrechten_set.exists()
        ):
            raise serializers.ValidationError(
                _(
                    "De indicatie moet op 'ja' gezet worden door `gebruiksrechten` "
                    "aan te maken, dit kan niet direct op deze resource."
                ),
                code="missing-gebruiksrechten",
            )
        return indicatie

    def validate(self, attrs):
        valid_attrs = super().validate(attrs)
        # check if file.size equal bestandsomvang
        if self.instance is None:  # create
            inhoud = valid_attrs.get("inhoud")
            if inhoud is not None and inhoud.size != valid_attrs.get("bestandsomvang"):
                raise serializers.ValidationError(
                    _(
                        "The size of upload file should match the 'bestandsomvang' field"
                    ),
                    code="file-size",
                )
        else:  # update
            inhoud = valid_attrs.get("inhoud", self.instance.inhoud)
            bestandsomvang = valid_attrs.get(
                "bestandsomvang", self.instance.bestandsomvang
            )
            if inhoud and inhoud.size != bestandsomvang:
                raise serializers.ValidationError(
                    _("The size of upload file should match bestandsomvang field"),
                    code="file-size",
                )

        return valid_attrs

    def _create_bestandsdeel(self, full_size, canonical):
        """add chunk urls"""
        parts = math.ceil(full_size / settings.CHUNK_SIZE)
        for i in range(parts):
            chunk_size = min(settings.CHUNK_SIZE, full_size)
            BestandsDeel.objects.create(
                informatieobject=canonical, omvang=chunk_size, volgnummer=i + 1
            )
            full_size -= chunk_size

    @transaction.atomic
    def create(self, validated_data):
        """
        Handle nested writes.
        """
        integriteit = validated_data.pop("integriteit", None)
        ondertekening = validated_data.pop("ondertekening", None)
        # add vertrouwelijkheidaanduiding
        if "vertrouwelijkheidaanduiding" not in validated_data:
            informatieobjecttype = self._get_informatieobjecttype(
                validated_data["informatieobjecttype"]
            )
            validated_data["vertrouwelijkheidaanduiding"] = informatieobjecttype[
                "vertrouwelijkheidaanduiding"
            ]

        canonical = EnkelvoudigInformatieObjectCanonical.objects.create()
        validated_data["canonical"] = canonical

        eio = super().create(validated_data)
        eio.integriteit = integriteit
        eio.ondertekening = ondertekening
        eio.save()

        # large file process
        if not eio.inhoud and eio.bestandsomvang and eio.bestandsomvang > 0:
            self._create_bestandsdeel(validated_data["bestandsomvang"], canonical)

        # create empty file if size == 0
        if eio.bestandsomvang == 0:
            eio.inhoud.save("empty_file", ContentFile(""))

        return eio

    def update(self, instance, validated_data):
        """
        Instead of updating an existing EnkelvoudigInformatieObject,
        create a new EnkelvoudigInformatieObject with the same
        EnkelvoudigInformatieObjectCanonical
        """
        integriteit = validated_data.pop("integriteit", None)
        ondertekening = validated_data.pop("ondertekening", None)

        eio = super().update(instance, validated_data)
        eio.integriteit = integriteit
        eio.ondertekening = ondertekening
        eio.save()

        # each update - delete previous part files
        if eio.canonical.bestandsdelen.exists():
            for part in eio.canonical.bestandsdelen.all():
                part.inhoud.delete()
                part.delete()

        # large file process
        if not eio.inhoud and eio.bestandsomvang and eio.bestandsomvang > 0:
            self._create_bestandsdeel(eio.bestandsomvang, eio.canonical)

        # create empty file if size == 0
        if eio.bestandsomvang == 0 and not eio.inhoud:
            eio.inhoud.save("empty_file", ContentFile(""))

        return eio


class EnkelvoudigInformatieObjectWithLockSerializer(
    EnkelvoudigInformatieObjectSerializer
):
    """
    This serializer class is used by EnkelvoudigInformatieObjectViewSet for
    update and partial_update operations
    """

    lock = serializers.CharField(
        write_only=True,
        help_text=_(
            "Lock must be provided during updating the document (PATCH, PUT), "
            "not while creating it"
        ),
    )

    class Meta(EnkelvoudigInformatieObjectSerializer.Meta):
        # Use the same fields as the parent class and add the lock to it
        fields = EnkelvoudigInformatieObjectSerializer.Meta.fields + ("lock",)

    def validate(self, attrs):
        valid_attrs = super().validate(attrs)

        if not self.instance.canonical.lock:
            raise serializers.ValidationError(
                _("Unlocked document can't be modified"), code="unlocked"
            )

        try:
            lock = valid_attrs["lock"]
        except KeyError:
            raise serializers.ValidationError(
                _("Lock id must be provided"), code="missing-lock-id"
            )

        # update
        if lock != self.instance.canonical.lock:
            raise serializers.ValidationError(
                _("Lock id is not correct"), code="incorrect-lock-id"
            )

        return valid_attrs


class EnkelvoudigInformatieObjectCreateLockSerializer(
    EnkelvoudigInformatieObjectSerializer
):
    """
    This serializer class is used by EnkelvoudigInformatieObjectViewSet for
    create operation for large files
    """

    lock = serializers.CharField(
        read_only=True,
        source="canonical.lock",
        help_text=_(
            "Lock id generated if the large file is created and should be used "
            "while updating the document. Documents with base64 encoded files "
            "are created without lock"
        ),
    )

    class Meta(EnkelvoudigInformatieObjectSerializer.Meta):
        # Use the same fields as the parent class and add the lock to it
        fields = EnkelvoudigInformatieObjectSerializer.Meta.fields + ("lock",)
        extra_kwargs = EnkelvoudigInformatieObjectSerializer.Meta.extra_kwargs.copy()
        extra_kwargs.update({"lock": {"source": "canonical.lock", "read_only": True}})

    def create(self, validated_data):
        eio = super().create(validated_data)

        # lock document if it is a large file upload
        if not eio.inhoud and eio.bestandsomvang and eio.bestandsomvang > 0:
            eio.canonical.lock = uuid.uuid4().hex
            eio.canonical.save()
        return eio


class LockEnkelvoudigInformatieObjectSerializer(serializers.ModelSerializer):
    """
    Serializer for the lock action of EnkelvoudigInformatieObjectCanonical
    model
    """

    class Meta:
        model = EnkelvoudigInformatieObjectCanonical
        fields = ("lock",)
        extra_kwargs = {"lock": {"read_only": True}}

    def validate(self, attrs):
        valid_attrs = super().validate(attrs)
        if self.instance.lock:
            raise serializers.ValidationError(
                _("The document is already locked"), code="existing-lock"
            )
        return valid_attrs

    @transaction.atomic
    def save(self, **kwargs):
        self.instance.lock = uuid.uuid4().hex
        self.instance.save()

        # create new version of document
        eio = self.instance.latest_version
        eio.pk = None
        eio.versie = eio.versie + 1
        eio.save()

        return self.instance


class UnlockEnkelvoudigInformatieObjectSerializer(serializers.ModelSerializer):
    """
    Serializer for the unlock action of EnkelvoudigInformatieObjectCanonical
    model
    """

    class Meta:
        model = EnkelvoudigInformatieObjectCanonical
        fields = ("lock",)
        extra_kwargs = {"lock": {"required": False}}

    def validate(self, attrs):
        valid_attrs = super().validate(attrs)
        force_unlock = self.context.get("force_unlock", False)

        if force_unlock:
            return valid_attrs

        lock = valid_attrs.get("lock", "")
        if lock != self.instance.canonical.lock:
            raise serializers.ValidationError(
                _("Lock id is not correct"), code="incorrect-lock-id"
            )

        if (
            not self.instance.canonical.complete_upload
            and not self.instance.canonical.empty_bestandsdelen
        ):
            raise serializers.ValidationError(
                _("Upload of part files is not complete"), code="incomplete-upload"
            )
        is_empty = (
            self.instance.canonical.empty_bestandsdelen and not self.instance.inhoud
        )
        if is_empty and self.instance.bestandsomvang > 0:
            raise serializers.ValidationError(
                _("Either file should be upload or the file size = 0"), code="file-size"
            )

        return valid_attrs

    @transaction.atomic
    def save(self, **kwargs):
        # unlock
        self.instance.canonical.lock = ""
        self.instance.canonical.save()

        # merge files and clean bestandsdelen
        if self.instance.canonical.empty_bestandsdelen:
            return self.instance

        bestandsdelen = self.instance.canonical.bestandsdelen.order_by("volgnummer")
        if self.instance.canonical.complete_upload:
            part_files = [p.inhoud.file for p in bestandsdelen]
            # create the name of target file using the storage backend to the serializer
            name = create_filename(self.instance.bestandsnaam)
            file_field = self.instance._meta.get_field("inhoud")
            rel_name = file_field.generate_filename(self.instance, name)
            rel_path, file_name = os.path.split(rel_name)
            # merge files
            file_dir = os.path.join(settings.PRIVATE_MEDIA_ROOT, rel_path)
            target_file = merge_files(part_files, file_dir, file_name)
            # save full file to the instance FileField
            with open(target_file, "rb") as file_obj:
                self.instance.inhoud.save(file_name, File(file_obj))
        else:
            self.instance.bestandsomvang = None
            self.instance.save()

        # delete part files
        for part in bestandsdelen:
            part.inhoud.delete()
            part.delete()

        return self.instance


class EIOZoekSerializer(serializers.Serializer):
    uuid__in = serializers.ListField(
        child=serializers.UUIDField(),
        help_text=_("Array of unieke resource identifiers (UUID4)"),
    )
