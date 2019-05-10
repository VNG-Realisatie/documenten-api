from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.tests import JWTAuthMixin, get_validation_errors

from drc.datamodel.tests.factories import (
    EnkelvoudigInformatieObjectFactory, GebruiksrechtenFactory
)

from .utils import reverse
from ..scopes import (
    SCOPE_DOCUMENTEN_ALLES_LEZEN, SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN,
    SCOPE_DOCUMENTEN_BIJWERKEN
)

INFORMATIEOBJECTTYPE = 'https://example.com/informatieobjecttype/foo'


class GebruiksrechtenTests(JWTAuthMixin, APITestCase):
    scopes = [SCOPE_DOCUMENTEN_BIJWERKEN, SCOPE_DOCUMENTEN_ALLES_LEZEN]
    informatieobjecttype = INFORMATIEOBJECTTYPE

    def test_create(self):
        url = reverse('gebruiksrechten-list')
        eio = EnkelvoudigInformatieObjectFactory.create(
            creatiedatum='2018-12-24',
            informatieobjecttype=INFORMATIEOBJECTTYPE
        )
        eio_url = reverse('enkelvoudiginformatieobject-detail', kwargs={'uuid': eio.uuid})

        eio_detail = self.client.get(eio_url)

        self.assertIsNone(eio_detail.json()['indicatieGebruiksrecht'])

        response = self.client.post(url, {
            'informatieobject': eio_url,
            'startdatum': '2018-12-24T00:00:00Z',
            'omschrijvingVoorwaarden': 'Een hele set onredelijke voorwaarden',
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # ensure that the indication is updated now
        eio_detail = self.client.get(eio_url)
        self.assertTrue(eio_detail.json()['indicatieGebruiksrecht'])

    def test_block_clearing_indication(self):
        """
        If gebruiksrechten exist, you cannot change the indicatieGebruiksrechten
        anymore.
        """
        gebruiksrechten = GebruiksrechtenFactory.create(
            informatieobject__informatieobjecttype=INFORMATIEOBJECTTYPE
        )
        url = reverse(
            'enkelvoudiginformatieobject-detail',
            kwargs={'uuid': gebruiksrechten.informatieobject.uuid}
        )

        for invalid_value in (None, False):
            data = {'indicatieGebruiksrecht': invalid_value}
            response = self.client.patch(url, data)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            error = get_validation_errors(response, 'indicatieGebruiksrecht')
            self.assertEqual(error['code'], 'existing-gebruiksrechten')

    def test_block_setting_indication_true(self):
        """
        Assert that it's not possible to set the indication to true if there are
        no gebruiksrechten.
        """
        eio = EnkelvoudigInformatieObjectFactory.create(
            informatieobjecttype=INFORMATIEOBJECTTYPE
        )
        url = reverse('enkelvoudiginformatieobject-detail', kwargs={'uuid': eio.uuid})

        response = self.client.patch(url, {'indicatieGebruiksrecht': True})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, 'indicatieGebruiksrecht')
        self.assertEqual(error['code'], 'missing-gebruiksrechten')

    def test_delete_gebruiksrechten(self):
        self.autorisatie.scopes += [SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN]
        self.autorisatie.save()

        gebruiksrechten = GebruiksrechtenFactory.create(
            informatieobject__informatieobjecttype=INFORMATIEOBJECTTYPE
        )
        url = reverse(
            'gebruiksrechten-detail',
            kwargs={'uuid': gebruiksrechten.uuid}
        )
        eio_url = reverse(
            'enkelvoudiginformatieobject-detail',
            kwargs={'uuid': gebruiksrechten.informatieobject.uuid}
        )

        eio_data = self.client.get(eio_url).json()
        self.assertTrue(eio_data['indicatieGebruiksrecht'])

        # delete the gebruiksrechten
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        eio_data = self.client.get(eio_url).json()
        self.assertIsNone(eio_data['indicatieGebruiksrecht'])
