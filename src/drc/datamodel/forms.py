from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from vng_api_common.descriptors import GegevensGroepType

from drc.datamodel.models import Verzending


class GegevensGroepTypeMixin:
    def get_gegevens_groep_type_fields(self):
        return [
            attribute
            for name, attribute in self._meta.model.__dict__.items()
            if type(attribute) == GegevensGroepType
        ]

    def clean(self):
        """ "
        Validate that all fields are filled in for required GegevensGroepType fields.
        Also validates that all required fields are filled in if the GegevensGroepType
        itself is not required but one of the required fields of the GegevensGroepType
        is filled in (to prevent the GegevensGroepType from having incomplete data).
        """
        super().clean()

        gegevens_groep_type_fields = self.get_gegevens_groep_type_fields()
        missing_field_errors = {}

        for attribute in gegevens_groep_type_fields:
            required_groep_fields = set(
                field
                for field in list(attribute.mapping.values())
                if field.name not in attribute.optional
            )

            filled_in_required_fields = set(
                field
                for field in required_groep_fields
                if field.name in self.cleaned_data and self.cleaned_data[field.name]
            )

            if attribute.required:
                missing_fields = required_groep_fields - filled_in_required_fields
            else:
                missing_fields = (
                    required_groep_fields - filled_in_required_fields
                    if filled_in_required_fields
                    else []
                )

            if missing_fields:
                missing_field_errors.update(
                    {
                        field.name: ValidationError(
                            _(
                                "%(field)s is een verplicht veld wanneer gerelateerde velden zijn ingevuld."
                            ),
                            code="required",
                            params={"field": field.verbose_name},
                        )
                        for field in missing_fields
                    }
                )

        if missing_field_errors:
            raise ValidationError(missing_field_errors)


class VerzendingForm(GegevensGroepTypeMixin, forms.ModelForm):
    class Meta:
        model = Verzending
        fields = "__all__"
