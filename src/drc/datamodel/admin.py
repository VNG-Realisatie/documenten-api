from django.contrib import admin

from .models import EnkelvoudigInformatieObject, ObjectInformatieObject


@admin.register(EnkelvoudigInformatieObject)
class EnkelvoudigInformatieObjectAdmin(admin.ModelAdmin):
    list_display = ['__str__']


@admin.register(ObjectInformatieObject)
class ObjectInformatieObjectAdmin(admin.ModelAdmin):
    list_display = ['informatieobject', 'object', '__str__', 'registratiedatum']
    list_select_related = ('informatieobject',)
    list_filter = ('registratiedatum',)
    date_hierarchy = 'registratiedatum'
    search_fields = ('titel', 'beschrijving', 'informatieobject__titel', 'object')
