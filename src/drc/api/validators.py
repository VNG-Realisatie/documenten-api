from django.core.exceptions import ValidationError

from rest_framework import serializers

from drc.datamodel.validators import validate_status


class StatusValidator:
    """
    Wrap around drc.datamodel.validate_status to output the errors to the
    correct field.
    """

    def set_context(self, serializer):
        self.instance = getattr(serializer, 'instance', None)

    def __call__(self, attrs: dict):
        try:
            validate_status(
                status=attrs.get('status'),
                ontvangstdatum=attrs.get('ontvangstdatum'),
                instance=self.instance
            )
        except ValidationError as exc:
            raise serializers.ValidationError(exc.error_dict)
