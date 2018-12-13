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


class ChecksumAlgoritmes(DjangoChoices):
    crc_16 = ChoiceItem('CRC-16')
    crc_32 = ChoiceItem('CRC-32')
    crc_64 = ChoiceItem('CRC-64')
    fletcher_4 = ChoiceItem('fletcher-4')
    fletcher_8 = ChoiceItem('fletcher-8')
    fletcher_16 = ChoiceItem('fletcher-16')
    fletcher_32 = ChoiceItem('fletcher-32')
    hmac = ChoiceItem('HMAC')
    md5 = ChoiceItem('MD5')
    sha_1 = ChoiceItem('SHA-1')
    sha_256 = ChoiceItem('SHA-256')
    sha_512 = ChoiceItem('SHA-512')
    sha_3 = ChoiceItem('SHA-3')
