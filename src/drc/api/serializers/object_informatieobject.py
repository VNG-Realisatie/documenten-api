from rest_framework import serializers
from vng_api_common.constants import ObjectTypes
from vng_api_common.serializers import add_choice_values_help_text
from vng_api_common.utils import get_help_text
from vng_api_common.validators import IsImmutableValidator, URLValidator

from drc.api.auth import get_zrc_auth
from drc.api.fields import EnkelvoudigInformatieObjectHyperlinkedRelatedField
from drc.api.validators import (
    InformatieObjectUniqueValidator,
    ObjectInformatieObjectValidator,
)
from drc.datamodel.models.enkelvoudig_informatieobject import (
    EnkelvoudigInformatieObject,
)
from drc.datamodel.models.object_informatieobject import ObjectInformatieObject


class ObjectInformatieObjectSerializer(serializers.HyperlinkedModelSerializer):
    informatieobject = EnkelvoudigInformatieObjectHyperlinkedRelatedField(
        view_name="enkelvoudiginformatieobject-detail",
        lookup_field="uuid",
        queryset=EnkelvoudigInformatieObject.objects,
        help_text=get_help_text("datamodel.ObjectInformatieObject", "informatieobject"),
    )

    class Meta:
        model = ObjectInformatieObject
        fields = (
            "url",
            "informatieobject",
            "object",
            "object_type",
            "naam_relatie",
            "naam_inverse_relatie",
        )
        extra_kwargs = {
            "url": {"lookup_field": "uuid"},
            "informatieobject": {"validators": [IsImmutableValidator()]},
            "object": {
                "validators": [
                    URLValidator(
                        get_auth=get_zrc_auth, headers={"Accept-Crs": "EPSG:4326"}
                    ),
                    IsImmutableValidator(),
                ]
            },
            "object_type": {"validators": [IsImmutableValidator()]},
        }
        validators = [
            ObjectInformatieObjectValidator(),
            InformatieObjectUniqueValidator("object", "informatieobject"),
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        value_display_mapping = add_choice_values_help_text(ObjectTypes)
        self.fields["object_type"].help_text += f"\n\n{value_display_mapping}"

        if not hasattr(self, "initial_data"):
            return
