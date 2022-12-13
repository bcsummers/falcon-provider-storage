"""Testing conf module."""
# standard library
import os

# third-party
import boto3
import pytest
from falcon import testing

from .LocalHook.app import app_hook_local_storage_1
from .LocalMiddleware.app import app_local_storage_1
from .S3Hook.app import app_hook_s3_storage_1
from .S3Middleware.app import app_s3_storage_1, app_s3_storage_2

# the log directory for all test cases
_storage_directory = 'storage'
os.makedirs(_storage_directory, exist_ok=True)


@pytest.fixture
def client_hook_local_storage_1() -> testing.TestClient:
    """Create testing client"""
    return testing.TestClient(app_hook_local_storage_1)


@pytest.fixture
def client_local_storage_1() -> testing.TestClient:
    """Create testing client"""
    return testing.TestClient(app_local_storage_1)


@pytest.fixture
def client_hook_s3_storage_1() -> testing.TestClient:
    """Create testing client"""
    return testing.TestClient(app_hook_s3_storage_1)


@pytest.fixture
def client_s3_storage_1() -> testing.TestClient:
    """Create testing client"""
    return testing.TestClient(app_s3_storage_1)


@pytest.fixture
def client_s3_storage_2() -> testing.TestClient:
    """Create testing client"""
    return testing.TestClient(app_s3_storage_2)


@pytest.fixture
def s3_client() -> object:
    """Return the log directory"""
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

    return boto3.client(
        's3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key
    )


@pytest.fixture
def s3_resource() -> object:
    """Return the log directory"""
    return boto3.resource('s3')


@pytest.fixture
def s3_bucket() -> str:
    """Return the log directory"""
    return os.getenv('S3_BUCKET')


@pytest.fixture
def storage_directory() -> str:
    """Return the log directory"""
    return _storage_directory


def pytest_unconfigure(config: object) -> None:  # pylint: disable=unused-argument
    """Add pytest test case indicator"""
    if os.path.isdir(_storage_directory):
        for log_file in os.listdir(_storage_directory):
            file_path = os.path.join(_storage_directory, log_file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
