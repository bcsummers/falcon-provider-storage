"""Falcon storage module."""
# flake8: noqa
from .__metadata__ import (
    __author__,
    __author_email__,
    __description__,
    __license__,
    __package_name__,
    __url__,
    __version__,
)
from .utils import LocalStorageProvider, S3StorageProvider, StorageProvider
