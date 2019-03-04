import datetime
import uuid

from django.utils import timezone

import factory
import factory.fuzzy
from zds_schema.constants import ObjectTypes, VertrouwelijkheidsAanduiding

from ..constants import RelatieAarden


class EnkelvoudigInformatieObjectFactory(factory.django.DjangoModelFactory):
    identificatie = uuid.uuid4().hex
    bronorganisatie = factory.Faker('ssn', locale='nl_NL')
    creatiedatum = datetime.date(2018, 6, 27)
    titel = 'some titel'
    auteur = 'some auteur'
    formaat = 'some formaat'
    taal = 'dut'
    inhoud = factory.django.FileField(data=b'some data', filename='file.bin')
    informatieobjecttype = 'https://example.com/ztc/api/v1/catalogus/1/informatieobjecttype/1'
    vertrouwelijkheidaanduiding = VertrouwelijkheidsAanduiding.openbaar

    class Meta:
        model = 'datamodel.EnkelvoudigInformatieObject'


class ObjectInformatieObjectFactory(factory.django.DjangoModelFactory):

    informatieobject = factory.SubFactory(EnkelvoudigInformatieObjectFactory)
    object = factory.Faker('url')
    aard_relatie = factory.fuzzy.FuzzyChoice(RelatieAarden.values)

    class Meta:
        model = 'datamodel.ObjectInformatieObject'

    class Params:
        is_zaak = factory.Trait(
            object_type=ObjectTypes.zaak,
            object=factory.Sequence(lambda n: f'https://zrc.nl/api/v1/zaken/{n}'),
            registratiedatum=factory.Faker('past_datetime', tzinfo=timezone.utc),
            aard_relatie=RelatieAarden.hoort_bij
        )
        is_besluit = factory.Trait(
            object_type=ObjectTypes.besluit,
            object=factory.Sequence(lambda n: f'https://brc.nl/api/v1/besluiten/{n}'),
            aard_relatie=RelatieAarden.legt_vast
        )


class GebruiksrechtenFactory(factory.django.DjangoModelFactory):
    informatieobject = factory.SubFactory(EnkelvoudigInformatieObjectFactory)
    omschrijving_voorwaarden = factory.Faker('paragraph')

    class Meta:
        model = 'datamodel.Gebruiksrechten'

    @factory.lazy_attribute
    def startdatum(self):
        return datetime.datetime.combine(
            self.informatieobject.creatiedatum,
            datetime.time(0, 0)
        ).replace(tzinfo=timezone.utc)
