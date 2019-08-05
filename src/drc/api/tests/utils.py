from math import ceil

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse as _reverse, reverse_lazy as _reverse_lazy


def reverse(*args, **kwargs):
    kwargs.setdefault('kwargs', {})
    kwargs['kwargs']['version'] = settings.REST_FRAMEWORK['DEFAULT_VERSION']
    return _reverse(*args, **kwargs)


def reverse_lazy(*args, **kwargs):
    kwargs.setdefault('kwargs', {})
    kwargs['kwargs']['version'] = settings.REST_FRAMEWORK['DEFAULT_VERSION']
    return _reverse_lazy(*args, **kwargs)


def split_file(file_obj, chunk_size) -> list:
    result = []
    count = ceil(file_obj.size/chunk_size)
    for i in range(count):
        result.append(SimpleUploadedFile(f"file_{i}.txt", file_obj.read(chunk_size)))

    return result
