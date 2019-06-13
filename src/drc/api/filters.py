from copy import deepcopy
from urllib.parse import urlparse

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_filters import filters
from vng_api_common.filters import URLModelChoiceField, URLModelChoiceFilter
from vng_api_common.filtersets import FILTER_FOR_DBFIELD_DEFAULTS, FilterSet
from vng_api_common.utils import get_resource_for_path

from drc.datamodel.models import (
    EnkelvoudigInformatieObject, EnkelvoudigInformatieObjectCanonical,
    Gebruiksrechten, ObjectInformatieObject
)


class InformatieObjectURLChoiceField(URLModelChoiceField):
    def url_to_pk(self, url: str):
        parsed = urlparse(url)
        path = parsed.path
        instance = get_resource_for_path(path).canonical
        model = self.queryset.model
        if not isinstance(instance, model):
            raise ValidationError(_("Invalid resource type supplied, expected %r") % model, code='invalid-type')
        return instance.pk


class InformatieObjectChoiceFilter(URLModelChoiceFilter):
    field_class = InformatieObjectURLChoiceField


FILTER_FOR_DBFIELD_INFORMATIEOBJECT = deepcopy(FILTER_FOR_DBFIELD_DEFAULTS)
FILTER_FOR_DBFIELD_INFORMATIEOBJECT[models.ForeignKey]['filter_class'] = InformatieObjectChoiceFilter
FILTER_FOR_DBFIELD_INFORMATIEOBJECT[models.OneToOneField]['filter_class'] = InformatieObjectChoiceFilter


class InformatieObjectFilterSet(FilterSet):
    FILTER_DEFAULTS = FILTER_FOR_DBFIELD_INFORMATIEOBJECT


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
