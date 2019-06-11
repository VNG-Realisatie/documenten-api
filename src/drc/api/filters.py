from urllib.parse import urlparse

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_filters import filters
from django_filters.rest_framework import filterset
from vng_api_common.filters import URLModelChoiceField
from vng_api_common.filtersets import FilterSet, InformatieObjectFilterSet
from vng_api_common.utils import get_resource_for_path

from drc.datamodel.models import (
    EnkelvoudigInformatieObject, EnkelvoudigInformatieObjectCanonical,
    Gebruiksrechten, ObjectInformatieObject
)


class EnkelvoudigInformatieObjectFilter(FilterSet):
    class Meta:
        model = EnkelvoudigInformatieObject
        fields = (
            'identificatie',
            'bronorganisatie'
        )


class ObjectInformatieObjectFilter(InformatieObjectFilterSet):
    class Meta:
        model = ObjectInformatieObject
        fields = (
            'object',
            'informatieobject',
        )


class GebruiksrechtenFilter(InformatieObjectFilterSet):
    class Meta:
        model = Gebruiksrechten
        fields = {
            'informatieobject': ['exact'],
            'startdatum': ['lt', 'lte', 'gt', 'gte'],
            'einddatum': ['lt', 'lte', 'gt', 'gte'],
        }
