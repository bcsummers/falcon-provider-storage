# -*- coding: utf-8 -*-
"""Test hooks feature of falcon_provider_memcache module."""
# standard library
import binascii
import io
import json
import os
from uuid import uuid4

# third-party
import botocore
from falcon.testing import Result


def create_multipart_formdata(fields: list) -> None:
    """Create form data.

    Args:
        fields: The list of fields to create.

    Returns:
        tuple: The request body and headers
    """
    random: str = binascii.hexlify(os.urandom(16)).decode('ascii')
    boundary = f'----WebKitFormBoundary{random}'

    body = []
    for field, value in fields.items():
        body.append(f'--{boundary}\r\n')
        if isinstance(value, dict):
            filename = value.get('filename')
            value = value.get('content')

            body.append(
                f'Content-Disposition: form-data; name="{field}"; filename="{filename}"\r\n\r\n'
            )
            # body.append(f'Content-Type: text/plain\r\n\r\n')
        else:
            body.append(f'Content-Disposition: form-data; name="{field}"\r\n\r\n')

        # add value
        body.append(f'{value}\r\n')
    body.append(f'--{boundary}--\r\n')

    body = ''.join(body)
    headers = {
        'content-type': f'multipart/form-data; boundary={boundary}',
        # 'content-length': str(len(body)),
    }
    return body, headers


def test_s3_hook_file_delete(
    client_hook_s3_storage_1: object, s3_client: object, s3_resource: object, s3_bucket: str
) -> None:
    """Testing DELETE resource

    Args:
        client_hook_s3_storage_1 (fixture): The test client.
        s3_client (fixture): A S3 client object.
        s3_resource (fixture): A S3 resource object.
        s3_bucket (fixture): The s3 bucket name.
    """
    key = f'{uuid4()}'
    contents = io.BytesIO(key.encode())

    # create file in storage to read
    contents.seek(0)
    s3_client.upload_fileobj(
        contents, s3_bucket, f'{key}.txt', ExtraArgs={'ContentType': 'text/plain'}
    )

    params = {'filename': f'{key}.txt'}
    response: Result = client_hook_s3_storage_1.simulate_delete('/middleware', params=params)
    assert response.status_code == 204
    try:
        s3_resource.Object(s3_bucket, f'{key}.txt').load()
        assert False, 'File was not deleted'
    except botocore.exceptions.ClientError:
        assert True


# pylint: disable=unused-argument
def test_s3_hook_file_delete_404(
    client_hook_s3_storage_1: object, s3_client: object, s3_resource: object, s3_bucket: str
) -> None:
    """Testing DELETE resource

    Args:
        client_hook_s3_storage_1 (fixture): The test client.
        s3_client (fixture): A S3 client object.
        s3_resource (fixture): A S3 resource object.
        s3_bucket (fixture): The s3 bucket name.
    """
    key = f'{uuid4()}'

    params = {'filename': f'{key}.txt'}
    response: Result = client_hook_s3_storage_1.simulate_delete('/middleware', params=params)
    assert response.status_code == 404


def test_s3_hook_file_exists(
    client_hook_s3_storage_1: object, s3_client: object, s3_resource: object, s3_bucket: str
) -> None:
    """Testing GET resource

    Args:
        client_hook_s3_storage_1 (fixture): The test client.
        s3_client (fixture): A S3 client object.
        s3_resource (fixture): A S3 resource object.
        s3_bucket (fixture): The s3 bucket name.
    """
    key = f'{uuid4()}'
    contents = io.BytesIO(key.encode())

    # create file in storage to read
    contents.seek(0)
    s3_client.upload_fileobj(
        contents, s3_bucket, f'{key}.txt', ExtraArgs={'ContentType': 'text/plain'}
    )

    params = {'filename': f'{key}.txt'}
    response: Result = client_hook_s3_storage_1.simulate_get('/middleware', params=params)
    assert response.status_code == 200
    assert response.text == key
    s3_resource.Object(s3_bucket, f'{key}.txt').delete()


def test_s3_hook_does_not_exists(client_hook_s3_storage_1: object) -> None:
    """Testing GET resource

    Args:
        client_hook_s3_storage_1 (fixture): The test client.
    """
    params = {'filename': 'non-existent-file.txt'}
    response: Result = client_hook_s3_storage_1.simulate_get('/middleware', params=params)
    assert response.status_code == 500
    response_data = json.loads(response.text)
    assert response_data.get('title') == 'Internal Server Error'


def test_s3_hook_file_upload(
    client_hook_s3_storage_1: object, s3_client: object, s3_resource: object, s3_bucket: str
) -> None:
    """Testing POST resource

    Args:
        client_hook_s3_storage_1 (fixture): The test client.
        s3_client (fixture): A S3 client object.
        s3_resource (fixture): A S3 resource object.
        s3_bucket (fixture): The s3 bucket name.
    """
    file_key = f'{uuid4()}'

    # fields
    fields = {'file': {'filename': f'{file_key}.txt', 'content': file_key}}
    fields.update({'key': file_key})

    # multi-part data
    data, headers = create_multipart_formdata(fields)

    response: Result = client_hook_s3_storage_1.simulate_post(
        '/middleware', body=data, headers=headers
    )
    assert response.status_code == 200
    assert response.text == f'{file_key}.txt'

    assert (
        s3_client.get_object(Bucket=s3_bucket, Key=f'{file_key}.txt').get('Body').read().decode()
        == file_key
    )
    s3_resource.Object(s3_bucket, f'{file_key}.txt').delete()


def test_s3_hook_file_upload_fail(client_s3_storage_2) -> None:
    """Testing POST resource

    Args:
        client_s3_storage_2 (fixture): The test client.
    """
    file_key = f'{uuid4()}'

    # fields
    fields = {'file': {'filename': f'sub1/{file_key}.txt', 'content': file_key}}
    fields.update({'key': file_key})

    # multi-part data
    data, headers = create_multipart_formdata(fields)

    response: Result = client_s3_storage_2.simulate_post('/middleware', body=data, headers=headers)
    assert response.status_code == 500
    response_data = json.loads(response.text)
    assert response_data.get('title') == 'Internal Server Error'
