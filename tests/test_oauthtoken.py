"""Tests the oauthtoken module."""

import json

import pytest
import requests
import responses

from constants import BASE_OAUTH2_URL
from oauthtoken import OauthToken


example_client_id = 'uo6dggojyb8d6soh92zknwmi5ej1q2'
example_client_secret = 'nyo51xcdrerl8z9m56w9w6wg'
example_app_access_token = 'prau3ol6mg5glgek8m89ec2s9q5i3i'

example_app_access_token_pass_resp = {
    'access_token': example_app_access_token,
    'expires_in': 5184000,
    'token_type': 'bearer'
}

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

example_token_validation_pass_resp = {
    'client_id': example_client_id,
    'scopes': []
}

example_token_validation_fail_resp = {
    'status': 401,
    'message': 'invalid access token'
}

example_token_revoke_fail_resp_missing_token = {
    'status': 400,
    'message': 'missing oauth token'
}

example_token_revoke_fail_resp_invalid_token = {
    'status': 400,
    'message': 'Invalid token'
}


@pytest.fixture
@responses.activate
def token():
    responses.add(responses.POST,
                  f'{BASE_OAUTH2_URL}/token',
                  body=json.dumps(example_app_access_token_pass_resp),
                  status=200,
                  content_type='application/json')
    token = OauthToken(example_client_id, example_client_secret)
    return token


@responses.activate
def test_token_constructor_valid_client_id_and_secret_pass(token):
    responses.add(responses.POST,
                  f'{BASE_OAUTH2_URL}/token',
                  body=json.dumps(example_app_access_token_pass_resp),
                  status=200,
                  content_type='application/json')

    assert example_app_access_token == token.token


@responses.activate
def test_token_constructor_invalid_client_id_exception_thrown():
    responses.add(responses.POST,
                  f'{BASE_OAUTH2_URL}/token',
                  body=json.dumps(
                      example_app_access_token_fail_resp_invalid_client_id
                  ),
                  status=400,
                  content_type='application/json')

    with pytest.raises(requests.HTTPError):
        OauthToken('a', example_client_secret)


@responses.activate
def test_token_constructor_invalid_client_secret_exception_thrown():
    responses.add(responses.POST,
                  f'{BASE_OAUTH2_URL}/token',
                  body=json.dumps(
                      example_app_access_token_fail_resp_invalid_client_secret
                  ),
                  status=403,
                  content_type='application/json')

    with pytest.raises(requests.HTTPError):
        OauthToken(example_client_id, 'a')


@responses.activate
def test_token_constructor_missing_client_id_exception_thrown():
    responses.add(responses.POST,
                  f'{BASE_OAUTH2_URL}/token',
                  body=json.dumps(
                      example_app_access_token_fail_resp_missing_client_id
                  ),
                  status=400,
                  content_type='application/json')

    with pytest.raises(requests.HTTPError):
        OauthToken(None, example_client_secret)


@responses.activate
def test_token_constructor_missing_client_secret_exception_thrown():
    responses.add(responses.POST,
                  f'{BASE_OAUTH2_URL}/token',
                  body=json.dumps(
                      example_app_access_token_fail_resp_missing_client_secret
                  ),
                  status=400,
                  content_type='application/json')

    with pytest.raises(requests.HTTPError):
        OauthToken(example_client_id, None)


@responses.activate
def test_validate_valid_ret_true(token):
    responses.add(responses.GET,
                  f'{BASE_OAUTH2_URL}/validate',
                  body=json.dumps(example_token_validation_pass_resp),
                  status=200,
                  content_type='application/json')

    is_valid = token.validate()
    assert is_valid is True


@responses.activate
def test_validate_invalid_ret_false(token):
    responses.add(responses.GET,
                  f'{BASE_OAUTH2_URL}/validate',
                  body=json.dumps(example_token_validation_fail_resp),
                  status=401,
                  content_type='application/json')

    is_valid = token.validate()
    assert is_valid is False


@responses.activate
def test_revoke_valid_token_pass(token):
    responses.add(responses.POST,
                  f'{BASE_OAUTH2_URL}/revoke',
                  status=200)

    token.revoke()
    assert token.token is None


@responses.activate
def test_revoke_missing_token_throw_exception(token):
    token.token = None
    responses.add(responses.POST,
                  f'{BASE_OAUTH2_URL}/revoke',
                  body=json.dumps(
                      example_token_revoke_fail_resp_missing_token
                  ),
                  status=400,
                  content_type='application/json')

    with pytest.raises(requests.HTTPError):
        token.revoke()


@responses.activate
def test_revoke_invalid_token_fail(token):
    responses.add(responses.POST,
                  f'{BASE_OAUTH2_URL}/revoke',
                  body=json.dumps(
                      example_token_revoke_fail_resp_invalid_token
                  ),
                  status=400,
                  content_type='application/json')

    with pytest.raises(requests.HTTPError):
        token.revoke()
