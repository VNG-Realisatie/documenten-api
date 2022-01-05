from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from privates.admin import PrivateMediaMixin

from drc.datamodel.forms import VerzendingForm

from .models import (
    BestandsDeel,
    EnkelvoudigInformatieObject,
    EnkelvoudigInformatieObjectCanonical,
    Gebruiksrechten,
    ObjectInformatieObject,
    Verzending,
)


class GebruiksrechtenInline(admin.TabularInline):
    model = Gebruiksrechten
    extra = 1


class EnkelvoudigInformatieObjectInline(admin.StackedInline):
    model = EnkelvoudigInformatieObject
    extra = 1


def unlock(modeladmin, request, queryset):
    queryset.update(lock="")


@admin.register(EnkelvoudigInformatieObjectCanonical)
class EnkelvoudigInformatieObjectCanonicalAdmin(PrivateMediaMixin, admin.ModelAdmin):
    list_display = ["__str__", "get_not_lock_display"]
    inlines = [EnkelvoudigInformatieObjectInline, GebruiksrechtenInline]
    private_media_fields = ("inhoud",)
    actions = [unlock]

    def get_not_lock_display(self, obj) -> bool:
        return not bool(obj.lock)

    get_not_lock_display.short_description = "free to change"
    get_not_lock_display.boolean = True


@admin.register(EnkelvoudigInformatieObject)
class EnkelvoudigInformatieObjectAdmin(admin.ModelAdmin):
    list_display = ("identificatie", "uuid", "bronorganisatie", "titel", "versie")
    list_filter = ("bronorganisatie",)
    search_fields = ("identificatie", "uuid")
    ordering = ("-begin_registratie",)
    raw_id_fields = ("canonical",)


@admin.register(ObjectInformatieObject)
class ObjectInformatieObjectAdmin(admin.ModelAdmin):
    list_display = ["informatieobject", "object", "__str__"]
    list_select_related = ("informatieobject",)
    search_fields = ("informatieobject__titel", "object")


@admin.register(Gebruiksrechten)
class GebruiksrechtenAdmin(admin.ModelAdmin):
    list_display = ("uuid", "informatieobject")
    list_filter = ("informatieobject",)
    raw_id_fields = ("informatieobject",)


@admin.register(BestandsDeel)
class BestandsDeelAdmin(PrivateMediaMixin, admin.ModelAdmin):
    list_display = ("__str__", "informatieobject", "volgnummer", "voltooid")
    list_filter = ("informatieobject",)
    private_media_fields = ("inhoud",)


@admin.register(Verzending)
class VerzendingAdmin(admin.ModelAdmin):
    form = VerzendingForm

    list_display = (
        "uuid",
        "aard_relatie",
        "contactpersoonnaam",
        "verzenddatum",
        "ontvangstdatum",
    )
    list_filter = ("aard_relatie",)
    ordering = (
        "-verzenddatum",
        "-ontvangstdatum",
    )
    search_fields = (
        "contactpersoonnaam",
        "uuid",
    )

    readonly_fields = ("uuid",)

    fieldsets = (
        (
            _("Algemeen"),
            {
                "fields": (
                    "uuid",
                    "aard_relatie",
                    "toelichting",
                    "verzenddatum",
                    "ontvangstdatum",
                ),
            },
        ),
        (
            _("Contactpersoon"),
            {
                "fields": (
                    "contact_persoon",
                    "contactpersoonnaam",
                ),
            },
        ),
        (
            _("Afwijkend binnenlands correspondentieadres verzending"),
            {
                "fields": (
                    "binnenlands_correspondentieadres_huisletter",
                    "binnenlands_correspondentieadres_huisnummer",
                    "binnenlands_correspondentieadres_huisnummer_toevoeging",
                    "binnenlands_correspondentieadres_naam_openbare_ruimte",
                    "binnenlands_correspondentieadres_postcode",
                    "binnenlands_correspondentieadres_woonplaats",
                ),
            },
        ),
        (
            _("Afwijkend buitenlands correspondentieadres verzending"),
            {
                # TODO: add buitenlands_correspondentieadres_land_postadres
                "fields": (
                    "buitenlands_correspondentieadres_adres_buitenland_1",
                    "buitenlands_correspondentieadres_adres_buitenland_2",
                    "buitenlands_correspondentieadres_adres_buitenland_3",
                ),
            },
        ),
        (
            _("Afwijkend correspondentie postadres verzending"),
            {
                "fields": (
                    "buitenlands_correspondentiepostadres_postbus_of_antwoord_nummer",
                    "buitenlands_correspondentiepostadres_postadres_postcode",
                    "buitenlands_correspondentiepostadres_postadrestype",
                    "buitenlands_correspondentiepostadres_woonplaats",
                ),
            },
        ),
    )
