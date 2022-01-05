from datetime import date

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .constants import POSTAL_CODE_LENGTH, Statussen


def validate_status(status: str = None, ontvangstdatum: date = None, instance=None):
    """
    Validate that certain status values are not used when an ontvangstdatum is
    provided.
    """
    if ontvangstdatum is None and instance is not None:
        ontvangstdatum = instance.ontvangstdatum

    if status is None and instance is not None:
        status = instance.status

    # if it's still empty, all statusses are allowed
    if ontvangstdatum is None:
        return

    # it is an optional field...
    if not status:
        return

    invalid_statuses = Statussen.invalid_for_received()
    if status in invalid_statuses:
        values = ", ".join(invalid_statuses)
        raise ValidationError(
            {
                "status": ValidationError(
                    _(
                        "De statuswaarden `{values}` zijn niet van toepassing "
                        "op ontvangen documenten."
                    ).format(values=values),
                    code="invalid_for_received",
                )
            }
        )


def validate_postal_code(value):
    """
    Validates a string is an correct dutch postal code.
    """
    if len(value) != POSTAL_CODE_LENGTH:
        raise ValidationError(
            _("Postcode moet %s tekens lang zijn.") % POSTAL_CODE_LENGTH,
            code="invalid-length",
        )

    postal_digits = value[:-4]

    if not all(digit.isdigit() for digit in postal_digits):
        raise ValidationError(_("De eerste vier karakters dienen een cijfer te zijn."))
    elif not int(postal_digits) >= 1000 or not int(postal_digits) <= 9999:
        raise ValidationError(
            _("Alleen cijfers tussen de 1000 en 9999 zijn toegestaan")
        )

    postal_letters = value[4:]

    if not all(letter.isalpha() for letter in postal_letters):
        raise ValidationError(_("De laatste twee karakters dienen een letter te zijn."))
