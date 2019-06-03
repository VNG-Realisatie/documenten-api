from django.contrib import admin

from privates.admin import PrivateMediaMixin

from .models import (
    EnkelvoudigInformatieObject, Gebruiksrechten, ObjectInformatieObject
)


class GebruiksrechtenInline(admin.TabularInline):
    model = Gebruiksrechten
    extra = 1


@admin.register(EnkelvoudigInformatieObject)
class EnkelvoudigInformatieObjectAdmin(PrivateMediaMixin, admin.ModelAdmin):
    list_display = ['__str__']
    inlines = [GebruiksrechtenInline]
    private_media_fields = ('inhoud', )


@admin.register(ObjectInformatieObject)
class ObjectInformatieObjectAdmin(admin.ModelAdmin):
    list_display = ['informatieobject', 'object', '__str__', 'registratiedatum']
    list_select_related = ('informatieobject',)
    list_filter = ('registratiedatum',)
    date_hierarchy = 'registratiedatum'
    search_fields = ('titel', 'beschrijving', 'informatieobject__titel', 'object')
