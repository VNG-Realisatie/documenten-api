from django.utils.translation import ugettext_lazy as _

from djchoices import ChoiceItem, DjangoChoices
from vng_api_common import constants

POSTAL_CODE_LENGTH = 6


class Statussen(DjangoChoices):
    in_bewerking = ChoiceItem(
        "in_bewerking",
        _("In bewerking"),
        description=_("Aan het informatieobject wordt nog gewerkt."),
    )
    concept = ChoiceItem(
        "concept",
        _("Concept"),
        description=_(
            "Het document is inhoudelijk klaar om voorgelegd te"
            "worden aan anderen en zo nodig aangepast te worden op"
            "basis van commentaar.."
        ),
    )
    definitief = ChoiceItem(
        "definitief",
        _("Definitief"),
        description=_(
            "Informatieobject door bevoegd iets of iemand "
            "vastgesteld dan wel ontvangen."
        ),
    )
    ter_vaststelling = ChoiceItem(
        "ter_vaststelling",
        _("Ter vaststelling"),
        description=_("Informatieobject gereed maar moet nog vastgesteld " "worden."),
    )
    Vastgesteld = ChoiceItem(
        "vastgesteld",
        _("Vastgesteld"),
        description=_("Het besluitvormingstraject is afgerond."),
    )
    gearchiveerd = ChoiceItem(
        "gearchiveerd",
        _("Gearchiveerd"),
        description=_(
            "Informatieobject duurzaam bewaarbaar gemaakt; een "
            "gearchiveerd informatie-element."
        ),
    )

    @classmethod
    def invalid_for_received(cls) -> tuple:
        return (cls.in_bewerking, cls.ter_vaststelling)


class ChecksumAlgoritmes(DjangoChoices):
    crc_16 = ChoiceItem("crc_16", "CRC-16")
    crc_32 = ChoiceItem("crc_32", "CRC-32")
    crc_64 = ChoiceItem("crc_64", "CRC-64")
    fletcher_4 = ChoiceItem("fletcher_4", "Fletcher-4")
    fletcher_8 = ChoiceItem("fletcher_8", "Fletcher-8")
    fletcher_16 = ChoiceItem("fletcher_16", "Fletcher-16")
    fletcher_32 = ChoiceItem("fletcher_32", "Fletcher-32")
    hmac = ChoiceItem("hmac", "HMAC")
    md5 = ChoiceItem("md5", "MD5")
    sha_1 = ChoiceItem("sha_1", "SHA-1")
    sha_256 = ChoiceItem("sha_256", "SHA-256")
    sha_512 = ChoiceItem("sha_512", "SHA-512")
    sha_3 = ChoiceItem("sha_3", "SHA-3")


class OndertekeningSoorten(DjangoChoices):
    analoog = ChoiceItem("analoog", _("Analoog"))
    digitaal = ChoiceItem("digitaal", _("Digitaal"))
    pki = ChoiceItem("pki", _("PKI"))
    # TODO: more...


class ObjectInformatieObjectTypes(DjangoChoices):
    besluit = constants.BESLUIT_CHOICE
    zaak = constants.ZAAK_CHOICE
    verzoek = constants.VERZOEK_CHOICE


class AfzenderTypes(DjangoChoices):
    afzender = ChoiceItem("afzender", _("Afzender"))
    geadresseerde = ChoiceItem("geadresseerde", _("Geadresseerde"))


class PostAdresTypes(DjangoChoices):
    antwoordnummer = ChoiceItem("antwoordnummer", _("Antwoordnummer"))
    postbusnummer = ChoiceItem("postbusnummer", _("Postbusnummer"))
