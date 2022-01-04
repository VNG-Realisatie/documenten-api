import uuid as _uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinValueValidator

from privates.fields import PrivateMediaFileField


class BestandsDeel(models.Model):
    uuid = models.UUIDField(
        unique=True, default=_uuid.uuid4, help_text="Unieke resource identifier (UUID4)"
    )
    informatieobject = models.ForeignKey(
        "EnkelvoudigInformatieObjectCanonical",
        on_delete=models.CASCADE,
        related_name="bestandsdelen",
    )
    volgnummer = models.PositiveIntegerField(
        help_text=_("Een volgnummer dat de volgorde van de bestandsdelen aangeeft.")
    )
    omvang = models.BigIntegerField(
        validators=[MinValueValidator(0)],
        help_text=_("De grootte van dit specifieke bestandsdeel."),
    )
    inhoud = PrivateMediaFileField(
        upload_to="part-uploads/%Y/%m/",
        blank=True,
        help_text=_("De (binaire) bestandsinhoud van dit specifieke bestandsdeel."),
    )

    class Meta:
        verbose_name = "bestands deel"
        verbose_name_plural = "bestands delen"
        unique_together = ("informatieobject", "volgnummer")

    def unique_representation(self):
        return f"({self.informatieobject.latest_version.unique_representation()}) - {self.volgnummer}"

    @property
    def voltooid(self) -> bool:
        return bool(self.inhoud.name)
