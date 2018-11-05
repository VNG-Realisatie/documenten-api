from django.utils.translation import ugettext_lazy as _

from djchoices import ChoiceItem, DjangoChoices
from zds_schema.constants import ObjectTypes


class RelatieAarden(DjangoChoices):
    hoort_bij = ChoiceItem('hoort_bij', _("Hoort bij, omgekeerd: kent"))
    legt_vast = ChoiceItem('legt_vast', _("Legt vast, omgekeerd: kan vastgelegd zijn als"))

    @classmethod
    def from_object_type(cls, object_type: str) -> str:
        if object_type == ObjectTypes.zaak:
            return cls.hoort_bij

        if object_type == ObjectTypes.besluit:
            return cls.legt_vast

        raise ValueError(f"Unknown object_type '{object_type}'")
