"""Module for Users interface."""

class Users:
    """Represents a list of Twitch users."""

    def __init__(self):
        self.users_list = []


    def get(self, *args, client_id=None, oauth2_token=None):
        """Gets a list of users.

        :param *args: Used to identify which users to return.
        :param client_id: Twitch developer client ID.
        :param oauth_token: Twitch developer OAuth2 token.
        :returns: A list of dictionaries, each representing a Twitch
                  user.
        """
        raise NotImplementedError
