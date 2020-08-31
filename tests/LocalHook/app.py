# -*- coding: utf-8 -*-
"""Falcon app used for testing."""
# standard library
import cgi

# third-party
import falcon

# first-party
from falcon_provider_storage.hook import local_storage

# define the local storage directory for testing
STORAGE_DIRECTORY = 'storage'


class LocalStorageResource1:
    """Local Storage middleware testing resource."""

    # pylint: disable=no-member
    @falcon.before(local_storage, STORAGE_DIRECTORY)
    def on_delete(self, req: falcon.Request, resp: falcon.Response) -> None:
        """Support DELETE method."""
        filename: str = req.get_param('filename')
        resp.status = falcon.HTTP_404
        if self.delete_file(filename):
            resp.status = falcon.HTTP_204

    # pylint: disable=no-member
    @falcon.before(local_storage, STORAGE_DIRECTORY)
    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:
        """Support GET method."""
        filename: str = req.get_param('filename')
        if self.is_file(filename):  # code coverage testing of is_file
            pass
        resp.body = self.get_file(filename)

    @falcon.before(local_storage, STORAGE_DIRECTORY)
    def on_post(self, req: falcon.Request, resp: falcon.Response) -> None:
        """Support POST method."""
        try:
            env: dict = req.env
            env.setdefault('QUERY_STRING', '')
            app_data: dict = cgi.FieldStorage(fp=req.stream, environ=env)
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

        resp.body = self.save_file(app_file.file, app_file.filename)


app_hook_local_storage_1 = falcon.API()
app_hook_local_storage_1.add_route('/middleware', LocalStorageResource1())
