from django.utils.translation import ugettext_lazy as _

from djchoices import ChoiceItem, DjangoChoices


class RelatieAarden(DjangoChoices):
    hoort_bij = ChoiceItem('hoort_bij', _("Hoort bij, omgekeerd: kent"))
    legt_vast = ChoiceItem('legt_vast', _("Legt vast, omgekeerd: kan vastgelegd zijn als"))
