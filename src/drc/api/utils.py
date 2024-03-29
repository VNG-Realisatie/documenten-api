import os
import shutil

from django.conf import settings
from django.contrib.sites.models import Site

from rest_framework.reverse import reverse


def get_absolute_url(url_name: str, uuid: str) -> str:
    path = reverse(
        url_name,
        kwargs={"version": settings.REST_FRAMEWORK["DEFAULT_VERSION"], "uuid": uuid},
    )
    domain = settings.DRC_BASE_URL
    return f"{domain}{path}"


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
