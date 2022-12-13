"""Falcon Storage hook module."""
# third-party
import falcon

from .utils import LocalStorageProvider, S3StorageProvider


def local_storage(
    req: falcon.Request, resp: falcon.Response, resource: object, params: dict, bucket: str
):  # pylint: disable=unused-argument
    """Provide an instance of REDIS client to method via resource.

    .. code-block:: python
        :linenos:
        :lineno-start: 1

        @falcon.before(local_storage, bucket)
        def on_get(self, req, resp):
            filename = req.get_param('filename')

    Args:
        req: The falcon req object.
        resp: The falcon resp object.
        resource: The falcon resp object.
        params: List of query params.
        bucket: The base directory/bucket where files should be written.
    """
    provider = LocalStorageProvider(bucket)

    # insert storage methods into resource
    resource.delete_file = provider.delete_file
    resource.get_file = provider.get_file
    resource.is_file = provider.is_file
    resource.save_file = provider.save_file


def s3_storage(
    req: falcon.Request,
    resp: falcon.Response,
    resource: object,
    params: dict,
    bucket: str,
    aws_access_key_id: str,
    aws_secret_access_key: str,
):  # pylint: disable=unused-argument
    """Provide an instance of REDIS client to method via resource.

    .. code-block:: python
        :linenos:
        :lineno-start: 1

        @falcon.before(s3_storage, BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
        def on_get(self, req, resp):
            filename = req.get_param('filename')

    Args:
        req: The falcon req object.
        resp: The falcon resp object.
        resource: The falcon resp object.
        params: List of query params.
        bucket: The base directory/bucket where files should be written.
        aws_access_key_id: The AWS access key Id.
        aws_secret_access_key: The AWS secret key.
    """
    provider = S3StorageProvider(bucket, aws_access_key_id, aws_secret_access_key)

    # insert storage methods into resource
    resource.delete_file = provider.delete_file
    resource.get_file = provider.get_file
    resource.is_file = provider.is_file
    resource.save_file = provider.save_file
