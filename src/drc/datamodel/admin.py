from django.contrib import admin

from .models import (
    EnkelvoudigInformatieObject, Gebruiksrechten, ObjectInformatieObject
)


class GebruiksrechtenInline(admin.TabularInline):
    model = Gebruiksrechten
    extra = 1


@admin.register(EnkelvoudigInformatieObject)
class EnkelvoudigInformatieObjectAdmin(admin.ModelAdmin):
    list_display = ['__str__']
    inlines = [GebruiksrechtenInline]


@admin.register(ObjectInformatieObject)
class ObjectInformatieObjectAdmin(admin.ModelAdmin):
    list_display = ['informatieobject', 'object', '__str__']
    list_select_related = ('informatieobject',)
    search_fields = ('informatieobject__titel', 'object')
