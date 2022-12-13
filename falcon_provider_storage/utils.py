"""Storage Provider Module"""
# standard library
import os

# third-party
import falcon

try:
    # third-party
    from botocore.exceptions import ClientError
except ImportError:  # pragma: no cover
    # caught and handled when importing boto3 in S3 class
    pass


class StorageProvider:
    """Base Storage Provider Module

    Args:
        bucket (str): The base directory/bucket where files should be written.
    """

    def __init__(self, bucket: str):  # pragma: no cover
        """Initialize class properties."""
        self.bucket = bucket

    def delete_file(self, path: str):  # pragma: no cover
        """Delete file from storage."""
        raise NotImplementedError('This method must be implemented in child class.')

    def get_file(self, path: str, **kwargs):  # pragma: no cover
        """Return file from storage."""
        raise NotImplementedError('This method must be implemented in child class.')

    def is_file(self, path: str):  # pragma: no cover
        """Return True if file exist, else False."""
        raise NotImplementedError('This method must be implemented in child class.')

    def save_file(self, contents: bytes, path: str, **kwargs):  # pragma: no cover
        """Write file to storage."""
        raise NotImplementedError('This method must be implemented in child class.')


class LocalStorageProvider(StorageProvider):
    """Local Storage Provider Module

    Args:
        bucket (str): The base directory/bucket where files should be written.
    """

    def __init__(self, bucket: str):
        """Initialize class properties."""
        super().__init__(bucket)

        if not os.access(self.bucket, os.W_OK):  # pragma: no cover
            raise falcon.HTTPInternalServerError(  # pylint: disable=raise-missing-from
                # code=code(),
                description='App does not have write access to storage bucket.',
                title='Internal Server Error',
            )

    def delete_file(self, path: str) -> bool:
        """Delete a file.

        Args:
            path: The path of the file to delete.

        Return:
            str: True if the file was delete.
        """
        try:
            os.remove(path)
            return True
        except FileNotFoundError:
            return False
        except PermissionError:  # pragma: no cover
            return False

    # pylint: disable=unspecified-encoding
    def get_file(self, path: str, **kwargs) -> bytes:
        """Return file from storage.

        Args:
            path: The path of the file to return.
            mode (str | kwargs): The read mode for the file.

        Raises:
            falcon.HTTPInternalServerError: Raised for any exception during the file download.

        Returns:
            bytes: The file contents.
        """
        fully_qualified_path = os.path.join(self.bucket, path)
        try:
            with open(fully_qualified_path, kwargs.get('mode', 'rb')) as fh:
                return fh.read()
        except OSError:
            raise falcon.HTTPInternalServerError(  # pylint: disable=raise-missing-from
                # code=code(),
                description=f'File ({path}) could not be accessed.',
                title='Internal Server Error',
            )

    def is_file(self, path: str) -> bool:
        """Return True if file exists, else False.

        Args:
            path: The path of the file to return.

        Returns:
            bool: True if file exists, else False.
        """
        fully_qualified_path = os.path.join(self.bucket, path)
        return os.path.isfile(fully_qualified_path)

    # pylint: disable=unspecified-encoding
    def save_file(self, contents, path, **kwargs):
        """Write file to storage.

        Args:
            contents: The contents of the file.
            path: The path to write the file.
            mode (str | kwargs): The write mode, defaults to 'wb'.

        Raises:
            falcon.HTTPInternalServerError: Raised for any exception during the file check.

        Returns:
            str: The final path to where the file was written.
        """
        fully_qualified_path = os.path.join(self.bucket, path)
        # ensure the directory exists
        try:
            os.makedirs(os.path.dirname(fully_qualified_path), exist_ok=True)
            with open(fully_qualified_path, kwargs.get('mode', 'wb')) as fh:
                fh.write(contents.read())
        except OSError:  # pragma: no cover
            raise falcon.HTTPInternalServerError(  # pylint: disable=raise-missing-from
                # code=code(),
                description='File could not be written.',
                title='Internal Server Error',
            )
        return fully_qualified_path


class S3StorageProvider(StorageProvider):
    """S3 Storage Provider Module

    Args:
        bucket: The base directory/bucket where files should be written.
        aws_access_key_id: The AWS access key Id.
        aws_secret_access_key: The AWS secret key.
    """

    def __init__(self, bucket: str, aws_access_key_id: str, aws_secret_access_key: str):
        """Initialize class properties."""
        super().__init__(bucket)

        try:
            # third-party
            import boto3  # pylint: disable=import-outside-toplevel
        except ImportError:  # pragma: no cover
            print(
                'S3StorageProvider requires boto3 and botocore to be installed '
                'try "pip install falcon-provider-storage[s3]".'
            )
            raise

        # initialize the boto3 client
        self.client = boto3.client(
            's3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key
        )
        self.resource = boto3.resource('s3')

    def delete_file(self, path: str) -> bool:
        """Delete a file.

        .. code:: javascript

            {
                'ResponseMetadata': {
                    'RequestId': 'B..............5',
                    'HostId': '0..........................................=',
                    'HTTPStatusCode': 204,
                    'HTTPHeaders': {
                        'x-amz-id-2': '0.............................................=',
                        'x-amz-request-id': 'B..............5',
                        'date': 'Mon, 26 Aug 2019 21:39:22 GMT',
                        'x-amz-version-id': 'M..............................W',
                        'x-amz-delete-marker': 'true',
                        'server': 'AmazonS3'
                    },
                    'RetryAttempts': 0
                },
                'DeleteMarker': True,
                'VersionId': 'M..............................W'
            }

        Args:
            path: The path of the file to delete.

        Return:
            str: True if the file was delete.
        """
        if self.is_file(path):
            try:
                self.resource.Object(self.bucket, path).delete()
                return True
            except ClientError:  # pragma: no cover
                return False
        else:
            return False

    def get_file(self, path: str, **kwargs) -> object:
        """Return file from storage.

        Args:
            path: The path of the file to return.

        Raises:
            falcon.HTTPInternalServerError: Raised for any exception during the file download.

        Returns:
            object: A boto file object.
        """
        try:
            file_obj: object = self.client.get_object(Bucket=self.bucket, Key=path)
        except Exception:
            raise falcon.HTTPInternalServerError(  # pylint: disable=raise-missing-from
                # code=code(),
                description='File download failed.',
                title='Internal Server Error',
            )
        return file_obj['Body'].read()

    def is_file(self, path: str) -> bool:
        """Return True if file exists, else False.

        Args:
            path: The path of the file to return.

        Raises:
            falcon.HTTPInternalServerError: Raised for any exception during the file check.

        Returns:
            bool: True if file exists, else False.
        """
        try:
            self.resource.Object(self.bucket, path).load()
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False

            # pylint: disable=raise-missing-from
            raise falcon.HTTPInternalServerError(  # pragma: no cover
                # code=code(),
                description='File download failed.',
                title='Internal Server Error',
            )
        except TypeError:  # pragma: no cover
            raise falcon.HTTPInternalServerError(  # pylint: disable=raise-missing-from
                # code=code(),
                description='File download failed.',
                title='Internal Server Error',
            )

    def save_file(self, contents: bytes, path: str, **kwargs):
        """Write file to storage.

        Args:
            contents: The contents of the file.
            path: The path to write the file.
            content_type (str | kwargs): The file content-type.

        Raises:
            falcon.HTTPInternalServerError: Raised for any exception during the file check.

        Returns:
            str: The final path to where the file was written.
        """
        try:
            self.client.upload_fileobj(
                contents, self.bucket, path, ExtraArgs={'ContentType': kwargs.get('content_type')}
            )
        except (ClientError, TypeError) as err:
            raise falcon.HTTPInternalServerError(  # pylint: disable=raise-missing-from
                # code=code(),
                description=f'File upload failed ({err}).',
                title='Internal Server Error',
            )
        return path
