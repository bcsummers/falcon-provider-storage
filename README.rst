=======================
falcon-provider-storage
=======================

|build| |coverage| |code-style| |pre-commit|

A falcon hook and middleware storage provider.

------------
Installation
------------

Install the extension via pip.

.. code:: bash

    > pip install falcon-provider-storage
    > pip install falcon-provider-storage[s3]

--------
Overview
--------

This package provides a hook and middleware storage component for the Falcon framework. The module currently supports local and AWS S3 storage. It provides 4 basic method for managing files: ``delete_file()``, ``get_file()``, ``is_file()``, ``save_file()``.

--------
Requires
--------
* Falcon - https://pypi.org/project/falcon/

Extra Requires
--------------
* boto3 - https://pypi.org/project/boto3/

-----
Hooks
-----

The local_storage or s3_storage hooks can be applied at the class level or the method level. Once applied all four methods are available in the class or method.

For more information on falcon hooks see https://falcon.readthedocs.io/en/stable/api/hooks.html.

.. code:: python

    import falcon

    from falcon_provider_storage.hook import local_storage

    # define the local storage directory for testing
    storage_directory = 'storage'


    @falcon.before(local_storage, storage_directory)
    class LocalStorageResource1(object):
        """Local Storage middleware testing resource."""

        def on_delete(self, req, resp):
            """Support DELETE method."""
            filename = req.get_param('filename')
            resp.status = falcon.HTTP_404
            if self.delete_file(filename):
                resp.status = falcon.HTTP_204

        def on_get(self, req, resp):
            """Support GET method."""
            filename = req.get_param('filename')
            if self.is_file(filename):  # code coverage testing of is_file
                pass
            resp.text = self.get_file(filename)  # optionally pass read mode (e.g., mode='rb')

        def on_post(self, req, resp):
            """Support POST method."""
            try:
                # expects a single file with name "file"
                form = req.get_media()
                for part in form:
                    if part.name == 'file':
                        data = part.stream
                        filename = part.filename
                        break
            except TypeError:
                raise falcon.HTTPBadRequest(
                    description='File upload must be form-data',
                    title='Bad Request',
                )

            # if directory doesn't exist it will be created automatically
            # optionally pass write mode (e.g., mode='wb')
            resp.text = self.save_file(data, filename)


    app = falcon.App()
    app.add_route('/middleware', LocalStorageResource1())


----------
Middleware
----------

When using StorageMiddleware all responder methods will have access to the four storage methods. For more information on falcon middleware see https://falcon.readthedocs.io/en/stable/api/middleware.html.

.. code:: python

    import falcon

    from falcon_provider_storage.middleware import StorageMiddleware
    from falcon_provider_storage.utils import LocalStorageProvider


    class LocalStorageResource1(object):
        """Local Storage middleware testing resource."""

        def on_delete(self, req, resp):
            """Support GET method."""
            filename = req.get_param('filename')
            resp.status = falcon.HTTP_404
            if self.delete_file(filename):
                resp.status = falcon.HTTP_204

        def on_get(self, req, resp):
            """Support GET method."""
            filename = req.get_param('filename')
            resp.text = self.get_file(filename)

        def on_post(self, req, resp):
            """Support GET method."""
            try:
                # expects a single file with name "file"
                form = req.get_media()
                for part in form:
                    if part.name == 'file':
                        data = part.stream
                        filename = part.filename
                        break
            except TypeError:
                raise falcon.HTTPBadRequest(
                    description='File upload must be form-data',
                    title='Bad Request',
                )

            storage_path = self.save_file(data, filename)
            resp.text = storage_path


    local_provider = LocalStorageProvider(bucket='storage')
    app = falcon.App(middleware=[StorageMiddleware(provider=local_provider)])
    app.add_route('/middleware', LocalStorageResource1())

-----------
Development
-----------

Installation
------------

After cloning the repository, all development requirements can be installed via poetry. For linting and code consistency the pre-commit hooks should be installed.

.. code:: bash

    > poetry install --with dev --all-extras
    > pre-commit install

Testing
-------

.. code:: bash

    > poetry install --with dev,test --all-extras
    > pytest --cov=falcon_provider_storage --cov-report=term-missing tests/

.. |build| image:: https://github.com/bcsummers/falcon-provider-storage/workflows/build/badge.svg
    :target: https://github.com/bcsummers/falcon-provider-storage/actions

.. |coverage| image:: https://codecov.io/gh/bcsummers/falcon-provider-storage/branch/master/graph/badge.svg?token=PCPZPOMRC2
    :target: https://codecov.io/gh/bcsummers/falcon-provider-storage

.. |code-style| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/python/black

.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit
