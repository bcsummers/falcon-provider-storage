# -*- coding: utf-8 -*-
"""Falcon app used for testing."""
# standard library
import cgi

# third-party
import falcon

# first-party
from falcon_provider_storage.middleware import StorageMiddleware
from falcon_provider_storage.utils import LocalStorageProvider


class LocalStorageResource1:
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
        filename = req.get_param('filename')
        if self.is_file(filename):  # code coverage testing of is_file
            pass
        resp.body = self.get_file(filename)

    def on_post(self, req: falcon.Request, resp: falcon.Response) -> None:
        """Support GET method."""
        try:
            env: dict = req.env
            env.setdefault('QUERY_STRING', '')
            app_data = cgi.FieldStorage(fp=req.stream, environ=env)
        except TypeError:
            raise falcon.HTTPBadRequest(
                # code=self.code(),
                description='File upload must be form-data',
                title='Bad Request',
            )

        try:
            app_file = app_data['file']
        except KeyError:
            raise falcon.HTTPBadRequest(
                # code=self.code(),
                description='No App uploaded',
                title='Bad Request',
            )

        resp.body = self.save_file(app_file.file, app_file.filename, req.content_type)


local_provider = LocalStorageProvider(bucket='storage')
app_local_storage_1 = falcon.API(middleware=[StorageMiddleware(provider=local_provider)])
app_local_storage_1.add_route('/middleware', LocalStorageResource1())
