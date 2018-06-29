import factory

from drc.datamodel.models import EnkelvoudigInformatieObject


class EnkelvoudigInformatieObjectFactory(factory.django.DjangoModelFactory):

    inhoud = factory.django.FileField(filename='file.bin')

    class Meta:
        model = EnkelvoudigInformatieObject
