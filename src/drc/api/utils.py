import os
import shutil
from typing import Optional
from urllib.parse import urlparse, parse_qs

from django.conf import settings
from django.contrib.sites.models import Site

from rest_framework.reverse import reverse


def get_absolute_url(url_name: str, uuid: str) -> str:
    path = reverse(
        url_name,
        kwargs={"version": settings.REST_FRAMEWORK["DEFAULT_VERSION"], "uuid": uuid},
    )
    domain = Site.objects.get_current().domain
    protocol = "https" if settings.IS_HTTPS else "http"
    return f"{protocol}://{domain}{path}"


def merge_files(part_files, file_dir, file_name) -> str:
    os.makedirs(file_dir, exist_ok=True)

    file_path = os.path.join(file_dir, file_name)
    with open(file_path, "wb") as output:
        for file in part_files:
            with file.open("rb") as fileobj:
                shutil.copyfileobj(fileobj, output, settings.READ_CHUNK)
    return file_path


def create_filename(name):
    main_part, ext = os.path.splitext(name)
    ext = ext or f".{settings.DEFAULT_EXTENSION}"
    return f"{main_part}{ext}"


class GetVersionFromUrl:
    """
    Get document version from URL parameter

    When updating DRF to a version > 3.12, this will have to be modified as explained here:
    https://stackoverflow.com/questions/59243383/proper-usage-of-callable-default-function-in-django-rest-framework-drf
    """
    requires_context = True
    serializer_instance = None

    def set_context(self, serializer_field):
        self.serializer_instance = getattr(serializer_field, "parent", None)

    def __call__(self) -> Optional[int]:
        if not self.serializer_instance:
            return None

        initial_data = self.serializer_instance.initial_data
        informatieobject_url = urlparse(initial_data["informatieobject"])
        query_params = parse_qs(informatieobject_url.query)
        if "versie" in query_params:
            return query_params["versie"][0]

        return None
