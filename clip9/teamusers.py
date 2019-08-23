"""Module for TeamUsers class."""

import logging

from clip9.users import Users
from twitch import TwitchClient

class TeamUsers(Users):
    """Represents a list of Twitch users in a team."""

    def get(self, *args, client_id=None, oauth_token=None):
        """Gets a list of users given a team name.

        :param *args: First arg is the name of the team, rest are ignored.
        :param client_id: Twitch developer client ID.
        :param oauth_token: Twitch developer OAuth2 token.
        :returns: A list of dictionaries, each representing a Twitch user.
        """
        logging.info(f"Getting users from team {args[0]}")
        client = TwitchClient(client_id=client_id, oauth_token=oauth_token)
        team = client.teams.get(args[0])
        logging.info(f"Got {len(team.users)} users")
        self.users_list = team.users
