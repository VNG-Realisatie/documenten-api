from unittest.mock import patch


class MockValidationsMixin:
    def setUp(self):
        super().setUp()

        fetcher_patcher = patch("vng_api_common.validators.fetcher")
        fetcher_patcher.start()
        self.addCleanup(fetcher_patcher.stop)

        shape_patcher = patch(
            "vng_api_common.validators.obj_has_shape", return_value=True
        )
        shape_patcher.start()
        self.addCleanup(shape_patcher.stop)
