"""Falcon app used for testing."""
# standard library
import os

# third-party
import falcon

# first-party
from falcon_provider_storage.middleware import StorageMiddleware
from falcon_provider_storage.utils import S3StorageProvider


class S3StorageResource1:
    """Local Storage middleware testing resource."""

    # pylint: disable=no-member
    def on_delete(self, req: falcon.Request, resp: falcon.Response) -> None:
        """Support GET method."""
        filename: str = req.get_param('filename')
        resp.status = falcon.HTTP_404
        if self.delete_file(filename):
            resp.status = falcon.HTTP_204

    # pylint: disable=no-member
    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:
        """Support GET method."""
        filename: str = req.get_param('filename')
        if self.is_file(filename):  # code coverage testing of is_file
            pass
        resp.text = self.get_file(filename)

    def on_post(self, req: falcon.Request, resp: falcon.Response) -> None:
        """Support GET method."""
        try:
            form = req.get_media()
            # expect a single
            for part in form:
                if part.name == 'file':
                    data = part.stream
                    filename = part.filename
                    break
        except TypeError:
            raise falcon.HTTPBadRequest(  # pylint: disable=raise-missing-from
                # code=self.code(),
                description='File upload must be form-data',
                title='Bad Request',
            )

        storage_path = self.save_file(data, filename, content_type=req.content_type)
        resp.text = storage_path


aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
s3_bucket = os.getenv('S3_BUCKET')
s3_provider = S3StorageProvider(
    bucket=s3_bucket,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)
app_s3_storage_1 = falcon.App(middleware=[StorageMiddleware(provider=s3_provider)])
app_s3_storage_1.add_route('/middleware', S3StorageResource1())


# Bad Config

aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
s3_provider = S3StorageProvider(
    bucket='bad_bucket',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)
app_s3_storage_2 = falcon.App(middleware=[StorageMiddleware(provider=s3_provider)])
app_s3_storage_2.add_route('/middleware', S3StorageResource1())
