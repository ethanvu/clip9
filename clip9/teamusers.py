"""Module for TeamUsers class."""

from clip9.users import Users
from twitch import TwitchClient

class TeamUsers(Users):
    """Represents a list of Twitch users in a team."""

    def get(self, client_id, oauth_token=None, *args):
        """Gets a list of users given a team name.

        :param client_id: Twitch developer client ID.
        :param oauth_token: Twitch developer OAuth2 token.
        :param *args: First arg is the name of the team, rest are ignored.
        :returns: A list of dictionaries, each representing a Twitch user.
        """
        client = TwitchClient(client_id=client_id, oauth_token=oauth_token)
        team = client.teams.get(args[0])
        self.users_list = team.users
