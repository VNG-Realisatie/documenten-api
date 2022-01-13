from datetime import timedelta

from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.tests import JWTAuthMixin, reverse
from vng_api_common.tests.schema import get_validation_errors

from drc.datamodel.constants import AfzenderTypes, PostAdresTypes
from drc.datamodel.tests.factories import (
    EnkelvoudigInformatieObjectCanonicalFactory,
    VerzendingFactory,
)

INFORMATIEOBJECTTYPE = "https://example.com/informatieobjecttype/foo"


class VerzendingAPITests(JWTAuthMixin, APITestCase):
    heeft_alle_autorisaties = True

    def test_list(self):
        VerzendingFactory.create_batch(size=3)

        response = self.client.get(reverse("verzending-list"))

        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["count"], 3)

    def test_detail(self):
        verzending = VerzendingFactory()

        detail_url = reverse("verzending-detail", kwargs={"uuid": verzending.uuid})
        informatieobject_url = reverse(
            "enkelvoudiginformatieobject-detail",
            kwargs={
                "version": "1",
                "uuid": verzending.informatieobject.latest_version.uuid,
            },
        )

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = {
            "url": f"http://testserver{detail_url}",
            "betrokkene": verzending.betrokkene,
            "informatieobject": f"http://testserver{informatieobject_url}",
            "aardRelatie": verzending.aard_relatie,
            "toelichting": verzending.toelichting,
            "ontvangstdatum": verzending.ontvangstdatum,
            "verzenddatum": verzending.verzenddatum,
            "contactPersoon": verzending.contact_persoon,
            "contactpersoonnaam": verzending.contactpersoonnaam,
            "afwijkendBinnenlandsCorrespondentieadresVerzending": {
                "huisletter": verzending.binnenlands_correspondentieadres_huisletter,
                "huisnummer": verzending.binnenlands_correspondentieadres_huisnummer,
                "huisnummerToevoeging": verzending.binnenlands_correspondentieadres_huisnummer_toevoeging,
                "naamOpenbareRuimte": verzending.binnenlands_correspondentieadres_naam_openbare_ruimte,
                "postcode": verzending.binnenlands_correspondentieadres_postcode,
                "woonplaatsnaam": verzending.binnenlands_correspondentieadres_woonplaats,
            },
            "afwijkendCorrespondentiePosteadresVerzending": {
                "postBusOfAntwoordnummer": verzending.buitenlands_correspondentiepostadres_postbus_of_antwoord_nummer,
                "postadresPostcode": verzending.buitenlands_correspondentiepostadres_postadres_postcode,
                "postadresType": verzending.buitenlands_correspondentiepostadres_postadrestype,
                "woonplaatsnaam": verzending.buitenlands_correspondentiepostadres_woonplaats,
            },
            "afwijkendbuitenlandsCorrespondentieadresVerzending": {
                "adresBuitenland1": verzending.buitenlands_correspondentieadres_adres_buitenland_1,
                "adresBuitenland2": verzending.buitenlands_correspondentieadres_adres_buitenland_2,
                "adresBuitenland3": verzending.buitenlands_correspondentieadres_adres_buitenland_3,
                "landPostadres": verzending.buitenlands_correspondentieadres_land_postadres,
            },
        }

        self.assertEqual(response.json(), expected_data)

    def test_create(self):
        eio = EnkelvoudigInformatieObjectCanonicalFactory.create(
            latest_version__creatiedatum="2018-12-24",
            latest_version__informatieobjecttype=INFORMATIEOBJECTTYPE,
        )

        eio_url = reverse(
            "enkelvoudiginformatieobject-detail",
            kwargs={"uuid": eio.latest_version.uuid},
        )

        response = self.client.post(
            reverse("verzending-list"),
            {
                "betrokkene": "https://foo.com/persoonX",
                "informatieobject": eio_url,
                "aardRelatie": AfzenderTypes.geadresseerde,
                "toelichting": "Verzending van XYZ",
                "ontvangstdatum": (timezone.now() - timedelta(days=3)).strftime(
                    "%Y-%m-%d"
                ),
                "verzenddatum": timezone.now().strftime("%Y-%m-%d"),
                "contactPersoon": "https://foo.com/persoonY",
                "contactpersoonnaam": "persoonY",
                "afwijkendBinnenlandsCorrespondentieadresVerzending": {
                    "huisletter": "Q",
                    "huisnummer": 1,
                    "huisnummerToevoeging": "XYZ",
                    "naamOpenbareRuimte": "ParkY",
                    "postcode": "1800XY",
                    "woonplaatsnaam": "Alkmaar",
                },
                "afwijkendCorrespondentiePosteadresVerzending": {
                    "postBusOfAntwoordnummer": 20,
                    "postadresPostcode": "1800YX",
                    "postadresType": PostAdresTypes.postbusnummer,
                    "woonplaatsnaam": "Den Haag",
                },
                "afwijkendbuitenlandsCorrespondentieadresVerzending": {
                    "adresBuitenland1": "Adres 1",
                    "adresBuitenland2": "Adres 2",
                    "adresBuitenland3": "Adres 3",
                    "landPostadres": "https://foo.com/landY",
                },
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update(self):
        verzending = VerzendingFactory(
            binnenlands_correspondentieadres_huisletter="Y",
            buitenlands_correspondentiepostadres_postbus_of_antwoord_nummer=20,
        )

        new_eio = EnkelvoudigInformatieObjectCanonicalFactory.create(
            latest_version__creatiedatum="2018-12-24",
            latest_version__informatieobjecttype=INFORMATIEOBJECTTYPE,
        )

        informatieobject_url = reverse(
            "enkelvoudiginformatieobject-detail",
            kwargs={"version": "1", "uuid": new_eio.latest_version.uuid},
        )

        response = self.client.put(
            reverse("verzending-detail", kwargs={"uuid": verzending.uuid}),
            {
                "betrokkene": verzending.betrokkene,
                "informatieobject": f"http://testserver{informatieobject_url}",
                "aardRelatie": verzending.aard_relatie,
                "toelichting": verzending.toelichting,
                "ontvangstdatum": verzending.ontvangstdatum,
                "verzenddatum": verzending.verzenddatum,
                "contactPersoon": verzending.contact_persoon,
                "contactpersoonnaam": verzending.contactpersoonnaam,
                "afwijkendCorrespondentiePosteadresVerzending": {
                    "postBusOfAntwoordnummer": 13,
                    "postadresPostcode": verzending.buitenlands_correspondentiepostadres_postadres_postcode,
                    "postadresType": verzending.buitenlands_correspondentiepostadres_postadrestype,
                    "woonplaatsnaam": verzending.buitenlands_correspondentiepostadres_woonplaats,
                },
                "afwijkendbuitenlandsCorrespondentieadresVerzending": {
                    "adresBuitenland1": verzending.buitenlands_correspondentieadres_adres_buitenland_1,
                    "adresBuitenland2": verzending.buitenlands_correspondentieadres_adres_buitenland_2,
                    "adresBuitenland3": verzending.buitenlands_correspondentieadres_adres_buitenland_3,
                    "landPostadres": verzending.buitenlands_correspondentieadres_land_postadres,
                },
            },
        )

        verzending.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            verzending.buitenlands_correspondentiepostadres_postbus_of_antwoord_nummer,
            13,
        )
        self.assertEqual(verzending.informatieobject, new_eio)

    def test_partial_update(self):
        verzending = VerzendingFactory(betrokkene="https://foo.com/PersoonY")

        response = self.client.patch(
            reverse("verzending-detail", kwargs={"uuid": verzending.uuid}),
            {"betrokkene": "https://foo.com/PersoonX"},
        )

        verzending.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(verzending.betrokkene, "https://foo.com/PersoonX")

    def test_delete(self):
        verzending = VerzendingFactory()

        response = self.client.delete(
            reverse("verzending-detail", kwargs={"uuid": verzending.uuid}),
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_postal_code_validation(self):
        verzending = VerzendingFactory(
            buitenlands_correspondentiepostadres_postadres_postcode="1800XY"
        )

        response = self.client.patch(
            reverse("verzending-detail", kwargs={"uuid": verzending.uuid}),
            {
                "afwijkendCorrespondentiePosteadresVerzending": {
                    "postBusOfAntwoordnummer": verzending.buitenlands_correspondentiepostadres_postbus_of_antwoord_nummer,
                    "postadresPostcode": "18800RR",
                    "postadresType": verzending.buitenlands_correspondentiepostadres_postadrestype,
                    "woonplaatsnaam": verzending.buitenlands_correspondentiepostadres_woonplaats,
                }
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(
            response, "afwijkendCorrespondentiePosteadresVerzending.postadresPostcode"
        )
        self.assertEqual(error["reason"], "Postcode moet 6 tekens lang zijn.")
