"""Tests the token module."""

import json

import pytest
import requests
import responses

from clip9.constants import BASE_OAUTH2_URL
from clip9 import token


example_client_id = 'uo6dggojyb8d6soh92zknwmi5ej1q2'
example_client_secret = 'nyo51xcdrerl8z9m56w9w6wg'
example_app_access_token = 'prau3ol6mg5glgek8m89ec2s9q5i3i'

example_app_access_token_fail_resp_invalid_client_id = {
    'status': 400,
    'message': 'invalid client'
}

example_app_access_token_fail_resp_invalid_client_secret = {
    'status': 403,
    'message': 'invalid client secret'
}

example_app_access_token_fail_resp_missing_client_id = {
    'status': 400,
    'message': 'missing client id'
}

example_app_access_token_fail_resp_missing_client_secret = {
    'status': 400,
    'message': 'missing client secret'
}

example_app_access_token_pass_resp = {
    'access_token': example_app_access_token,
    'expires_in': 5184000,
    'token_type': 'bearer'
}

example_token_validation_fail_resp = {
    'status': 401,
    'message': 'invalid access token'
}

example_token_validation_pass_resp = {
    'client_id': example_client_id,
    'scopes': []
}

example_token_revoke_fail_resp_invalid_client_id = {
    'status': 404,
    'message': 'client does not exist'
}

example_token_revoke_fail_resp_invalid_token = {
    'status': 400,
    'message': 'Invalid token'
}

example_token_revoke_fail_resp_missing_client_id = {
    'status': 400,
    'message': 'missing client id'
}

example_token_revoke_fail_resp_missing_token = {
    'status': 400,
    'message': 'missing oauth token'
}



@responses.activate
def test_get_app_access_token_invalid_client_id_exception_thrown():
    responses.add(responses.POST,
                  f'{BASE_OAUTH2_URL}/token',
                  body=json.dumps(
                      example_app_access_token_fail_resp_invalid_client_id
                  ),
                  status=400,
                  content_type='application/json')
    with pytest.raises(requests.HTTPError):
        token.get_app_access_token('a', example_client_secret)


@responses.activate
def test_get_app_access_token_invalid_client_secret_exception_thrown():
    responses.add(responses.POST,
                  f'{BASE_OAUTH2_URL}/token',
                  body=json.dumps(
                      example_app_access_token_fail_resp_invalid_client_secret
                  ),
                  status=403,
                  content_type='application/json')
    with pytest.raises(requests.HTTPError):
        token.get_app_access_token(example_client_id, 'a')


@responses.activate
def test_get_app_access_token_missing_client_id_exception_thrown():
    responses.add(responses.POST,
                  f'{BASE_OAUTH2_URL}/token',
                  body=json.dumps(
                      example_app_access_token_fail_resp_missing_client_id
                  ),
                  status=400,
                  content_type='application/json')
    with pytest.raises(requests.HTTPError):
        token.get_app_access_token(None, example_client_secret)


@responses.activate
def test_get_app_access_token_missing_client_secret_exception_thrown():
    responses.add(responses.POST,
                  f'{BASE_OAUTH2_URL}/token',
                  body=json.dumps(
                      example_app_access_token_fail_resp_missing_client_secret
                  ),
                  status=400,
                  content_type='application/json')
    with pytest.raises(requests.HTTPError):
        token.get_app_access_token(example_client_id, None)


@responses.activate
def test_get_app_access_token_valid_client_id_and_secret_pass():
    responses.add(responses.POST,
                  f'{BASE_OAUTH2_URL}/token',
                  body=json.dumps(example_app_access_token_pass_resp),
                  status=200,
                  content_type='application/json')
    app_access_token = token.get_app_access_token(example_client_id,
                                                  example_client_secret)
    assert app_access_token == example_app_access_token


@responses.activate
def test_validate_token_invalid_ret_false():
    responses.add(responses.GET,
                  f'{BASE_OAUTH2_URL}/validate',
                  body=json.dumps(example_token_validation_fail_resp),
                  status=401,
                  content_type='application/json')
    is_valid = token.validate_token('a')
    assert is_valid is False


@responses.activate
def test_validate_token_valid_ret_true():
    responses.add(responses.GET,
                  f'{BASE_OAUTH2_URL}/validate',
                  body=json.dumps(example_token_validation_pass_resp),
                  status=200,
                  content_type='application/json')
    is_valid = token.validate_token(example_app_access_token)
    assert is_valid is True


@responses.activate
def test_revoke_token_invalid_client_id_throw_exception():
    responses.add(responses.POST,
                  f'{BASE_OAUTH2_URL}/revoke',
                  body=json.dumps(
                      example_token_revoke_fail_resp_invalid_client_id
                  ),
                  status=404,
                  content_type='application/json')
    with pytest.raises(requests.HTTPError):
        token.revoke_token('a', example_app_access_token)


@responses.activate
def test_revoke_token_invalid_token_throw_exception():
    responses.add(responses.POST,
                  f'{BASE_OAUTH2_URL}/revoke',
                  body=json.dumps(
                      example_token_revoke_fail_resp_invalid_token
                  ),
                  status=400,
                  content_type='application/json')
    with pytest.raises(requests.HTTPError):
        token.revoke_token(example_client_id, 'a')


@responses.activate
def test_revoke_token_missing_client_id_throw_exception():
    responses.add(responses.POST,
                  f'{BASE_OAUTH2_URL}/revoke',
                  body=json.dumps(
                      example_token_revoke_fail_resp_missing_client_id
                  ),
                  status=400,
                  content_type='application/json')
    with pytest.raises(requests.HTTPError):
        token.revoke_token(None, example_app_access_token)


@responses.activate
def test_revoke_token_missing_token_throw_exception():
    responses.add(responses.POST,
                  f'{BASE_OAUTH2_URL}/revoke',
                  body=json.dumps(
                      example_token_revoke_fail_resp_missing_token
                  ),
                  status=400,
                  content_type='application/json')
    with pytest.raises(requests.HTTPError):
        token.revoke_token(example_client_id, None)


@responses.activate
def test_revoke_token_valid_client_id_and_token_pass():
    responses.add(responses.POST,
                  f'{BASE_OAUTH2_URL}/revoke',
                  status=200)
    was_revoked = token.revoke_token(example_client_id,
                                     example_app_access_token)
    assert was_revoked is True
