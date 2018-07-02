import datetime
import uuid

import factory

from drc.datamodel.models import (
    EnkelvoudigInformatieObject, ZaakInformatieObject
)


class EnkelvoudigInformatieObjectFactory(factory.django.DjangoModelFactory):

    identificatie = uuid.uuid4().hex
    bronorganisatie = '1'
    creatiedatum = datetime.date(2018, 6, 27)
    titel = 'some titel'
    auteur = 'some auteur'
    formaat = 'some formaat'
    taal = 'some taal'
    inhoud = factory.django.FileField(data=b'some data', filename='file.bin')

    class Meta:
        model = EnkelvoudigInformatieObject


class ZaakInformatieObjectFactory(factory.django.DjangoModelFactory):

    informatieobject = factory.SubFactory(EnkelvoudigInformatieObjectFactory)

    class Meta:
        model = ZaakInformatieObject
