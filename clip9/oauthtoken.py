"""Module for the OauthToken class.

A Twitch development client ID and secret are required to use this
class. More info can be found below: 
https://dev.twitch.tv/docs/authentication/getting-tokens-oauth/#oauth-client-credentials-flow
"""

import logging

import requests

from clip9.constants import BASE_OAUTH2_URL


class OauthToken:
    """A Twitch app access token.  Once the token instance has called
    revoke(), the instance is useless and shouldn't be used anymore.
    """

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.token = self._get_app_access_token(client_id, client_secret)


    def _get_app_access_token(self, client_id, client_secret):
        """Gets a Twitch app access token."""
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


    def validate(self):
        """Returns true if the token is valid, false otherwise."""
        logging.info(f"Validating token {self.token}")
        validation_headers = {'Authorization': f'OAuth {self.token}'}

        resp = requests.get(f'{BASE_OAUTH2_URL}/validate',
                            headers=validation_headers)

        is_valid = resp.status_code == 200
        logging.info(f"Token {self.token} is valid: {is_valid}")
        return is_valid


    def revoke(self):
        """Revokes the token."""
        logging.info(f"Revoking token {self.token}")
        revoke_params = {
            'client_id': self.client_id,
            'token': self.token,
        }

        resp = requests.post(f'{BASE_OAUTH2_URL}/revoke',
                             data=revoke_params)

        if (resp.status_code >= 400):
            resp_json = resp.json()
            logging.error(f"Error when revoking app access token: "
                          f"{resp_json['message']}")
            resp.raise_for_status()
        else:
            logging.info(f"Token {self.token} was sucessfully revoked")
            self.token = None
