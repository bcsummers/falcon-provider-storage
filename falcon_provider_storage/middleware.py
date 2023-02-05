"""Falcon storage provider middleware module."""
# third-party
import falcon

# first-party
from falcon_provider_storage.utils import StorageProviderABC


class StorageMiddleware:
    """Storage middleware module.

    Args:
        provider (StorageProvider): An instance of storage provider (e.g., LocalStorageProvider,
            S3StorageProvider).
    """

    def __init__(self, provider: StorageProviderABC):
        """Initialize class properties."""
        self.provider = provider
        if not isinstance(provider, StorageProviderABC):  # pragma: no cover
            raise ValueError('Invalid provider provided.')

    def process_resource(
        self, _req: falcon.Request, _resp: falcon.Response, resource, _params: dict
    ):  # pylint: disable=unused-argument
        """Process resource method."""
        resource.delete_file = self.provider.delete_file
        resource.get_file = self.provider.get_file
        resource.is_file = self.provider.is_file
        resource.save_file = self.provider.save_file
