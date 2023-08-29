from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from drc.datamodel.models import BestandsDeel


class BestandsDeelSerializer(serializers.HyperlinkedModelSerializer):
    lock = serializers.CharField(
        help_text="Hash string, which represents id of the lock of related informatieobject",
    )

    class Meta:
        model = BestandsDeel
        fields = ("url", "volgnummer", "omvang", "inhoud", "voltooid", "lock")
        extra_kwargs = {
            "url": {"lookup_field": "uuid"},
            "volgnummer": {"read_only": True},
            "omvang": {"read_only": True},
            "voltooid": {
                "read_only": True,
                "help_text": _(
                    "Indicatie of dit bestandsdeel volledig is geupload. Dat wil zeggen: "
                    "het aantal bytes dat staat genoemd bij grootte is daadwerkelijk ontvangen."
                ),
            },
            "inhoud": {"write_only": True},
        }

    def validate(self, attrs):
        valid_attrs = super().validate(attrs)

        inhoud = valid_attrs.get("inhoud")
        lock = valid_attrs.get("lock")
        if inhoud:
            if inhoud.size != self.instance.omvang:
                raise serializers.ValidationError(
                    _(
                        "Het aangeleverde bestand heeft een afwijkende bestandsgrootte (volgens het `grootte`-veld)."
                        "Verwachting: {expected}b, ontvangen: {received}b"
                    ).format(expected=self.instance.omvang, received=inhoud.size),
                    code="file-size",
                )

        if lock != self.instance.informatieobject.lock:
            raise serializers.ValidationError(
                _("Lock id is not correct"), code="incorrect-lock-id"
            )

        return valid_attrs
