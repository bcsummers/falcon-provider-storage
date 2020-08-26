# -*- coding: utf-8 -*-
"""Falcon app used for testing."""
# standard library
import cgi
import os

# third-party
import falcon

# first-party
from falcon_provider_storage.hook import s3_storage

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
S3_BUCKET = os.getenv('S3_BUCKET')


class S3StorageResource1:
    """Local Storage middleware testing resource."""

    # pylint: disable=no-member
    @falcon.before(s3_storage, S3_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    def on_delete(self, req: falcon.Request, resp: falcon.Response) -> None:
        """Support GET method."""
        filename: str = req.get_param('filename')
        resp.status = falcon.HTTP_404
        if self.delete_file(filename):
            resp.status = falcon.HTTP_204

    # pylint: disable=no-member
    @falcon.before(s3_storage, S3_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:
        """Support GET method."""
        filename: str = req.get_param('filename')
        # if self.is_file(filename):  # code coverage testing of is_file
        #     pass
        resp.body = self.get_file(filename)

    @falcon.before(s3_storage, S3_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    def on_post(self, req: falcon.Request, resp: falcon.Response) -> None:
        """Support GET method."""
        try:
            env: dict = req.env
            env.setdefault('QUERY_STRING', '')
            app_data = cgi.FieldStorage(fp=req.stream, environ=env)
        except TypeError:
            raise falcon.HTTPBadRequest(  # pylint: disable=raise-missing-from
                # code=self.code(),
                description='File upload must be form-data',
                title='Bad Request',
            )

        try:
            app_file = app_data['file']
        except KeyError:
            raise falcon.HTTPBadRequest(  # pylint: disable=raise-missing-from
                # code=self.code(),
                description='No App uploaded',
                title='Bad Request',
            )

        resp.body = self.save_file(app_file.file, app_file.filename, req.content_type)


app_hook_s3_storage_1 = falcon.API()
app_hook_s3_storage_1.add_route('/middleware', S3StorageResource1())
