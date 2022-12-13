"""Falcon app used for testing."""

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

        resp.text = self.save_file(data, filename)


local_provider = LocalStorageProvider(bucket='storage')
app_local_storage_1 = falcon.App(middleware=[StorageMiddleware(provider=local_provider)])
app_local_storage_1.add_route('/middleware', LocalStorageResource1())
