"""
Test that the caching mechanisms are in place.
"""
from rest_framework import status
from rest_framework.test import APITestCase, APITransactionTestCase
from vng_api_common.tests import CacheMixin, JWTAuthMixin, generate_jwt_auth, reverse
from vng_api_common.tests.schema import get_spec

from drc.datamodel.tests.factories import (
    EnkelvoudigInformatieObjectFactory,
    GebruiksrechtenFactory,
    ObjectInformatieObjectFactory,
)


class EnkelvoudigInformatieObjectCacheTests(CacheMixin, JWTAuthMixin, APITestCase):
    heeft_alle_autorisaties = True

    def test_eio_get_cache_header(self):
        eio = EnkelvoudigInformatieObjectFactory.create()

        response = self.client.get(reverse(eio))

        self.assertHasETag(response)

    def test_eio_head_cache_header(self):
        eio = EnkelvoudigInformatieObjectFactory.create()

        self.assertHeadHasETag(reverse(eio))

    def test_head_in_apischema(self):
        spec = get_spec()

        endpoint = spec["paths"]["/api/v1/enkelvoudiginformatieobjecten/{uuid}"]

        self.assertIn("head", endpoint)

    def test_conditional_get_304(self):
        eio = EnkelvoudigInformatieObjectFactory.create(with_etag=True)
        response = self.client.get(reverse(eio), HTTP_IF_NONE_MATCH=f'"{eio._etag}"')

        self.assertEqual(response.status_code, status.HTTP_304_NOT_MODIFIED)

    def test_conditional_get_stale(self):
        eio = EnkelvoudigInformatieObjectFactory.create(with_etag=True)

        response = self.client.get(reverse(eio), HTTP_IF_NONE_MATCH=f'"not-an-md5"')

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ObjectInformatieObjectCacheTests(CacheMixin, JWTAuthMixin, APITestCase):
    heeft_alle_autorisaties = True

    def test_oio_get_cache_header(self):
        oio = ObjectInformatieObjectFactory.create()

        response = self.client.get(reverse(oio))

        self.assertHasETag(response)

    def test_oio_head_cache_header(self):
        oio = ObjectInformatieObjectFactory.create()

        self.assertHeadHasETag(reverse(oio))

    def test_head_in_apischema(self):
        spec = get_spec()

        endpoint = spec["paths"]["/api/v1/objectinformatieobjecten/{uuid}"]

        self.assertIn("head", endpoint)

    def test_conditional_get_304(self):
        oio = ObjectInformatieObjectFactory.create(with_etag=True)
        response = self.client.get(reverse(oio), HTTP_IF_NONE_MATCH=f'"{oio._etag}"')

        self.assertEqual(response.status_code, status.HTTP_304_NOT_MODIFIED)

    def test_conditional_get_stale(self):
        oio = ObjectInformatieObjectFactory.create(with_etag=True)

        response = self.client.get(reverse(oio), HTTP_IF_NONE_MATCH=f'"not-an-md5"')

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GebruiksrechtenCacheTests(CacheMixin, JWTAuthMixin, APITestCase):
    heeft_alle_autorisaties = True

    def test_gebruiksrecht_get_cache_header(self):
        gebruiksrecht = GebruiksrechtenFactory.create()

        response = self.client.get(reverse(gebruiksrecht))

        self.assertHasETag(response)

    def test_gebruiksrechthead_cache_header(self):
        gebruiksrecht = GebruiksrechtenFactory.create()

        self.assertHeadHasETag(reverse(gebruiksrecht))

    def test_head_in_apischema(self):
        spec = get_spec()

        endpoint = spec["paths"]["/api/v1/gebruiksrechten/{uuid}"]

        self.assertIn("head", endpoint)

    def test_conditional_get_304(self):
        gebruiksrecht = GebruiksrechtenFactory.create(with_etag=True)
        response = self.client.get(
            reverse(gebruiksrecht), HTTP_IF_NONE_MATCH=f'"{gebruiksrecht._etag}"'
        )

        self.assertEqual(response.status_code, status.HTTP_304_NOT_MODIFIED)

    def test_conditional_get_stale(self):
        gebruiksrecht = GebruiksrechtenFactory.create(with_etag=True)

        response = self.client.get(
            reverse(gebruiksrecht), HTTP_IF_NONE_MATCH=f'"not-an-md5"'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class EnkelvoudigInformatieObjectCacheTransactionTests(
    JWTAuthMixin, APITransactionTestCase
):
    heeft_alle_autorisaties = True

    def setUp(self):
        super().setUp()
        self._create_credentials(
            self.client_id,
            self.secret,
            self.heeft_alle_autorisaties,
            self.max_vertrouwelijkheidaanduiding,
        )

    def test_invalidate_etag_after_change(self):
        """
        Because changes are made to the informatieobject, a code 200 should be
        returned
        """
        eio = EnkelvoudigInformatieObjectFactory.create(titel="bla", with_etag=True)
        etag = eio._etag

        eio.titel = "aangepast"
        eio.save()

        response = self.client.get(reverse(eio), HTTP_IF_NONE_MATCH=f"{etag}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
