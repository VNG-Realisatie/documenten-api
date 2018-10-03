import datetime
import uuid

from django.utils import timezone

import factory
from zds_schema.constants import ObjectTypes


class EnkelvoudigInformatieObjectFactory(factory.django.DjangoModelFactory):
    identificatie = uuid.uuid4().hex
    bronorganisatie = '1'
    creatiedatum = datetime.date(2018, 6, 27)
    titel = 'some titel'
    auteur = 'some auteur'
    formaat = 'some formaat'
    taal = 'dut'
    inhoud = factory.django.FileField(data=b'some data', filename='file.bin')
    informatieobjecttype = 'https://example.com/ztc/api/v1/catalogus/1/informatieobjecttype/1'

    class Meta:
        model = 'datamodel.EnkelvoudigInformatieObject'


class ObjectInformatieObjectFactory(factory.django.DjangoModelFactory):

    informatieobject = factory.SubFactory(EnkelvoudigInformatieObjectFactory)
    object = factory.Faker('url')
    registratiedatum = factory.Faker('past_datetime', tzinfo=timezone.utc)

    class Meta:
        model = 'datamodel.ObjectInformatieObject'

    class Params:
        is_zaak = factory.Trait(
            object_type=ObjectTypes.zaak,
            object=factory.Sequence(lambda n: f'https://zrc.nl/api/v1/zaken/{n}')
        )
        is_besluit = factory.Trait(
            object_type=ObjectTypes.besluit,
            object=factory.Sequence(lambda n: f'https://brc.nl/api/v1/besluiten/{n}')
        )
