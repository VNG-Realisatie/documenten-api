from django.contrib import admin

from privates.admin import PrivateMediaMixin

from .models import (
    EnkelvoudigInformatieObject, Gebruiksrechten, ObjectInformatieObject
)


class GebruiksrechtenInline(admin.TabularInline):
    model = Gebruiksrechten
    extra = 1


def unlock(modeladmin, request, queryset):
    queryset.update(lock='')


@admin.register(EnkelvoudigInformatieObject)
class EnkelvoudigInformatieObjectAdmin(PrivateMediaMixin, admin.ModelAdmin):
    list_display = ['__str__', 'get_not_lock_display']
    inlines = [GebruiksrechtenInline]
    private_media_fields = ('inhoud',)
    actions = [unlock]

    def get_not_lock_display(self, obj) -> bool:
        return not bool(obj.lock)
    get_not_lock_display.short_description = 'free to change'
    get_not_lock_display.boolean = True


@admin.register(ObjectInformatieObject)
class ObjectInformatieObjectAdmin(admin.ModelAdmin):
    list_display = ['informatieobject', 'object', '__str__', 'registratiedatum']
    list_select_related = ('informatieobject',)
    list_filter = ('registratiedatum',)
    date_hierarchy = 'registratiedatum'
    search_fields = ('titel', 'beschrijving', 'informatieobject__titel', 'object')
