import uuid as _uuid

from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _

from vng_api_common.caching import ETagMixin

from ..query import InformatieobjectRelatedQuerySet


class Gebruiksrechten(ETagMixin, models.Model):
    uuid = models.UUIDField(
        unique=True, default=_uuid.uuid4, help_text="Unieke resource identifier (UUID4)"
    )
    informatieobject = models.ForeignKey(
        "EnkelvoudigInformatieObjectCanonical",
        on_delete=models.CASCADE,
        help_text="URL-referentie naar het INFORMATIEOBJECT.",
    )
    omschrijving_voorwaarden = models.TextField(
        _("omschrijving voorwaarden"),
        help_text=_(
            "Omschrijving van de van toepassing zijnde voorwaarden aan "
            "het gebruik anders dan raadpleging"
        ),
    )
    startdatum = models.DateTimeField(
        _("startdatum"),
        help_text=_(
            "Begindatum van de periode waarin de gebruiksrechtvoorwaarden van toepassing zijn. "
            "Doorgaans is de datum van creatie van het informatieobject de startdatum."
        ),
    )
    einddatum = models.DateTimeField(
        _("startdatum"),
        blank=True,
        null=True,
        help_text=_(
            "Einddatum van de periode waarin de gebruiksrechtvoorwaarden van toepassing zijn."
        ),
    )

    objects = InformatieobjectRelatedQuerySet.as_manager()

    class Meta:
        verbose_name = _("gebruiksrecht informatieobject")
        verbose_name_plural = _("gebruiksrechten informatieobject")

    def __str__(self):
        return str(self.informatieobject.latest_version)

    @transaction.atomic
    def save(self, *args, **kwargs):
        informatieobject_versie = self.informatieobject.latest_version
        # ensure the indication is set properly on the IO
        if not informatieobject_versie.indicatie_gebruiksrecht:
            informatieobject_versie.indicatie_gebruiksrecht = True
            informatieobject_versie.save()
        super().save(*args, **kwargs)

    @transaction.atomic
    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        informatieobject = self.informatieobject
        other_gebruiksrechten = informatieobject.gebruiksrechten_set.exclude(pk=self.pk)
        if not other_gebruiksrechten.exists():
            informatieobject_versie = self.informatieobject.latest_version
            informatieobject_versie.indicatie_gebruiksrecht = None
            informatieobject_versie.save()

    def unique_representation(self):
        informatieobject = self.informatieobject.latest_version
        return f"({informatieobject.unique_representation()}) - {self.omschrijving_voorwaarden[:50]}"
