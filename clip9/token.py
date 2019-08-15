"""Provides methods pertaining to Twitch tokens"""

import logging

import requests

from clip9.constants import BASE_OAUTH2_URL

def get_app_access_token(client_id, client_secret):
    """Gets a Twitch app access token given a client ID and secret.

    The response should look like the example given here:
    https://dev.twitch.tv/docs/authentication/getting-tokens-oauth/#oauth-client-credentials-flow
    """
    logging.info(f"Requesting an app access token for {client_id}")
    app_access_tok_params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials',
    }

    resp = requests.post(f'{BASE_OAUTH2_URL}/token',
                         data=app_access_tok_params)
    resp_json = resp.json()

    if (resp.status_code >= 400):
        logging.error(f"Error when getting an app access token: "
                      f"{resp_json['message']}")
        resp.raise_for_status()
    else:
        logging.info("Got an app access token")
        return resp_json['access_token']


def validate_token(token):
    """Validates a Twitch token"""
    logging.info(f"Validating token {token}")
    validation_headers = {'Authorization': f'OAuth {token}'}

    resp = requests.get(f'{BASE_OAUTH2_URL}/validate',
                        headers=validation_headers)

    is_valid = resp.status_code == 200
    logging.info(f"Token {token} is valid: {is_valid}")
    return is_valid


def revoke_token(token):
    """Revokes a Twitch token"""
    pass
