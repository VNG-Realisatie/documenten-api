from django.contrib import admin

from .models import EnkelvoudigInformatieObject


@admin.register(EnkelvoudigInformatieObject)
class EnkelvoudigInformatieObjectAdmin(admin.ModelAdmin):
    list_display = ['__str__']
