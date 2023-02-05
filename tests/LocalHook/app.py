"""Falcon app used for testing."""
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
        resp.text = self.get_file(filename)

    @falcon.before(local_storage, STORAGE_DIRECTORY)
    def on_post(self, req: falcon.Request, resp: falcon.Response) -> None:
        """Support POST method."""
        try:
            form = req.get_media()
            # expect a single
            for part in form:
                if part.name == 'file':
                    data = part.stream
                    filename = part.filename
                    break
        except TypeError as ex:
            raise falcon.HTTPBadRequest(
                # code=self.code(),
                description='File upload must be form-data',
                title='Bad Request',
            ) from ex

        resp.text = self.save_file(data, filename)


app_hook_local_storage_1 = falcon.App()
app_hook_local_storage_1.add_route('/middleware', LocalStorageResource1())
