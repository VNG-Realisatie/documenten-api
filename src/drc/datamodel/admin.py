from django.contrib import admin

from .models import EnkelvoudigInformatieObject, ZaakInformatieObject


@admin.register(EnkelvoudigInformatieObject)
class EnkelvoudigInformatieObjectAdmin(admin.ModelAdmin):
    list_display = ['__str__']


@admin.register(ZaakInformatieObject)
class ZaakInformatieObjectAdmin(admin.ModelAdmin):
    list_display = ['zaak', 'informatieobject']
