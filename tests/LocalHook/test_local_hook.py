# -*- coding: utf-8 -*-
"""Test hooks feature of falcon_provider_memcache module."""
# standard library
import binascii
import json
import os
from typing import Tuple
from uuid import uuid4

# third-party
from falcon.testing import Result


def read_file() -> object:
    """Return file object for file upload."""
    return open('storage/test', 'r')


def create_multipart_formdata(fields: list) -> Tuple[str, dict]:
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
            filename: str = value.get('filename')
            value: str = value.get('content')

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


def test_local_delete(client_hook_local_storage_1, storage_directory) -> None:
    """Testing DELETE resource

    Args:
        client_hook_local_storage_1 (fixture): The test client.
        storage_directory (fixture): The storage directory.
    """
    key = f'{uuid4()}'

    # create file in storage to read
    filename: str = os.path.join(storage_directory, f'{key}.txt')
    with open(filename, 'w') as fh:
        fh.write('delete me')

    params = {'filename': filename}
    response: Result = client_hook_local_storage_1.simulate_delete('/middleware', params=params)
    assert response.status_code == 204
    if not os.path.isfile(response.text):
        assert True
    else:
        assert False, 'File was not deleted'


def test_local_delete_404(client_hook_local_storage_1, storage_directory) -> None:
    """Testing DELETE resource

    Args:
        client_hook_local_storage_1 (fixture): The test client.
        storage_directory (fixture): The storage directory.
    """
    key = f'{uuid4()}'
    filename = os.path.join(storage_directory, f'{key}.txt')
    params = {'filename': filename}
    response: Result = client_hook_local_storage_1.simulate_delete('/middleware', params=params)
    assert response.status_code == 404


def test_local_file_exists(client_hook_local_storage_1, storage_directory) -> None:
    """Testing GET resource

    Args:
        client_hook_local_storage_1 (fixture): The test client.
        storage_directory (fixture): The storage directory.
    """
    key = f'{uuid4()}'

    # create file in storage to read
    filename = os.path.join(storage_directory, f'{key}.txt')
    with open(filename, 'w') as fh:
        fh.write(key)

    params = {'filename': f'{key}.txt'}
    response: Result = client_hook_local_storage_1.simulate_get('/middleware', params=params)
    assert response.status_code == 200
    assert response.text == key


def test_local_does_not_exists(client_hook_local_storage_1) -> None:
    """Testing GET resource

    Args:
        client_hook_local_storage_1 (fixture): The test client.
    """
    params = {'filename': 'non-existent-file.txt'}
    response: Result = client_hook_local_storage_1.simulate_get('/middleware', params=params)
    assert response.status_code == 500
    response_data = json.loads(response.text)
    assert response_data.get('title') == 'Internal Server Error'


def test_local_file_upload(client_hook_local_storage_1, storage_directory) -> None:
    """Testing POST resource

    Args:
        client_hook_local_storage_1 (fixture): The test client.
        storage_directory (fixture): The storage directory.
    """
    file_key = f'{uuid4()}'

    # fields
    fields = {'file': {'filename': f'{file_key}.txt', 'content': file_key}}
    fields.update({'key': file_key})

    # multi-part data
    data, headers = create_multipart_formdata(fields)

    response = client_hook_local_storage_1.simulate_post('/middleware', body=data, headers=headers)
    assert response.status_code == 200
    assert response.text == f'{storage_directory}/{file_key}.txt'
    if not os.path.isfile(response.text):
        assert False, 'Uploaded file does not exist in storage'


# directories are now automatically created
# def test_local_file_upload_fail(client_hook_local_storage_1) -> None:
#     """Testing POST resource
#
#     Args:
#         client_hook_local_storage_1 (fixture): The test client.
#         storage_directory (fixture): The storage directory.
#     """
#     file_key = f'{uuid4()}'
#
#     # fields
#     fields = {'file': {'filename': f'sub1/{file_key}.txt', 'content': file_key}}
#     fields.update({'key': file_key})
#
#     # multi-part data
#     data, headers = create_multipart_formdata(fields)
#
#     response: Result = client_hook_local_storage_1.simulate_post(
#         '/middleware', body=data, headers=headers
#     )
#     assert response.status_code == 500
#     response_data = json.loads(response.text)
#     assert response_data.get('title') == 'Internal Server Error'
