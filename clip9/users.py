"""Module for Users interface."""

class Users:
    """Represents a list of Twitch users."""

    def __init__(self):
        self.users_list = []


    def get(self, source, client_id, oauth2_token=None):
        """Gets a list of users.

        :param source: Object that will be used to identify which users to return.
        :param client_id: Twitch developer client ID.
        :param oauth_token: Twitch developer OAuth2 token.
        :returns: A list of dictionaries, each representing a Twitch user.
        """
        raise NotImplementedError
