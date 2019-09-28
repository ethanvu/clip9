"""Module for TeamUsers class."""

import logging

from twitch import TwitchClient

from users import Users


class TeamUsers(Users):
    """Represents a list of Twitch users in a team."""

    def get(self, *args, client_id=None, oauth_token=None):
        """Gets a list of users given a team name.

        :param *args: First arg is the name of the team, rest are
                      ignored.
        :param client_id: Twitch developer client ID.
        :param oauth_token: Twitch developer OAuth2 token.
        :returns: A list of dictionaries, each representing a Twitch
                  user.
        :raises TypeError: When the first arg is None.
        :raises requests.HTTPError: When there is an error
                                    communicating with the Twitch
                                    Kraken API.
        """
        logging.info("Getting users from team %s", args[0])
        if args[0] is None:
            raise TypeError
        client = TwitchClient(client_id=client_id, oauth_token=oauth_token)
        team = client.teams.get(args[0])
        logging.info("Got %s users", len(team.users))
        self.users_list = team.users
