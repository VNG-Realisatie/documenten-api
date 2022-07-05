import datetime
import uuid

from django.utils import timezone

import factory
import factory.fuzzy
from vng_api_common.constants import ObjectTypes, VertrouwelijkheidsAanduiding

from drc.datamodel.constants import AfzenderTypes, PostAdresTypes


class EnkelvoudigInformatieObjectCanonicalFactory(factory.django.DjangoModelFactory):
    latest_version = factory.RelatedFactory(
        "drc.datamodel.tests.factories.EnkelvoudigInformatieObjectFactory", "canonical"
    )

    class Meta:
        model = "datamodel.EnkelvoudigInformatieObjectCanonical"


class EnkelvoudigInformatieObjectFactory(factory.django.DjangoModelFactory):
    canonical = factory.SubFactory(
        EnkelvoudigInformatieObjectCanonicalFactory, latest_version=None
    )
    identificatie = uuid.uuid4().hex
    bronorganisatie = factory.Faker("ssn", locale="nl_NL")
    creatiedatum = datetime.date(2018, 6, 27)
    titel = "some titel"
    auteur = "some auteur"
    formaat = "some formaat"
    taal = "nld"
    inhoud = factory.django.FileField(data=b"some data", filename="file.bin")
    informatieobjecttype = (
        "https://example.com/ztc/api/v1/catalogus/1/informatieobjecttype/1"
    )
    vertrouwelijkheidaanduiding = VertrouwelijkheidsAanduiding.openbaar
    bestandsomvang = factory.LazyAttribute(lambda o: o.inhoud.size)

    class Meta:
        model = "datamodel.EnkelvoudigInformatieObject"

    class Params:
        with_etag = factory.Trait(
            _etag=factory.PostGenerationMethodCall("calculate_etag_value")
        )


class ObjectInformatieObjectFactory(factory.django.DjangoModelFactory):
    informatieobject = factory.SubFactory(EnkelvoudigInformatieObjectCanonicalFactory)
    object = factory.Faker("url")

    class Meta:
        model = "datamodel.ObjectInformatieObject"

    class Params:
        is_zaak = factory.Trait(
            object_type=ObjectTypes.zaak,
            object=factory.Sequence(lambda n: f"https://zrc.nl/api/v1/zaken/{n}"),
        )
        is_besluit = factory.Trait(
            object_type=ObjectTypes.besluit,
            object=factory.Sequence(lambda n: f"https://brc.nl/api/v1/besluiten/{n}"),
        )
        with_etag = factory.Trait(
            _etag=factory.PostGenerationMethodCall("calculate_etag_value")
        )


class GebruiksrechtenFactory(factory.django.DjangoModelFactory):
    informatieobject = factory.SubFactory(EnkelvoudigInformatieObjectCanonicalFactory)
    omschrijving_voorwaarden = factory.Faker("paragraph")

    class Meta:
        model = "datamodel.Gebruiksrechten"

    class Params:
        with_etag = factory.Trait(
            _etag=factory.PostGenerationMethodCall("calculate_etag_value")
        )

    @factory.lazy_attribute
    def startdatum(self):
        return datetime.datetime.combine(
            self.informatieobject.latest_version.creatiedatum, datetime.time(0, 0)
        ).replace(tzinfo=timezone.utc)


class BestandsDeelFactory(factory.django.DjangoModelFactory):
    informatieobject = factory.SubFactory(EnkelvoudigInformatieObjectCanonicalFactory)
    inhoud = factory.django.FileField(data=b"some data", filename="file_part.bin")
    omvang = factory.LazyAttribute(lambda o: o.inhoud.size)
    volgnummer = factory.fuzzy.FuzzyInteger(1, 100, 1)

    class Meta:
        model = "datamodel.BestandsDeel"


class VerzendingFactory(factory.django.DjangoModelFactory):
    informatieobject = factory.SubFactory(EnkelvoudigInformatieObjectCanonicalFactory)
    aard_relatie = factory.fuzzy.FuzzyChoice(
        [value for value, label in AfzenderTypes.choices]
    )

    betrokkene = factory.Faker("url")
    contact_persoon = factory.Faker("url")

    buitenlands_correspondentieadres_adres_buitenland_2 = "Breedstraat"
    buitenlands_correspondentieadres_land_postadres = factory.Faker("url")

    buitenlands_correspondentiepostadres_postbus_of_antwoord_nummer = (
        factory.fuzzy.FuzzyInteger(1, 9999)
    )

    buitenlands_correspondentiepostadres_postadres_postcode = "1800XY"
    buitenlands_correspondentiepostadres_postadrestype = factory.fuzzy.FuzzyChoice(
        [value for value, label in PostAdresTypes.choices]
    )
    buitenlands_correspondentiepostadres_woonplaats = factory.Faker(
        "city", locale="nl_NL"
    )

    class Meta:
        model = "datamodel.Verzending"
