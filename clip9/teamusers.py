"""Module for TeamUsers class."""

from clip9.users import Users
from twitch import TwitchClient

class TeamUsers(Users):
    """Represents a list of Twitch users in a team."""

    def get(self, source, client_id, oauth_token=None):
        """Gets a list of users given a team name.

        :param source: Name of the team.
        :param client_id: Twitch developer client ID.
        :param oauth_token: Twitch developer OAuth2 token.
        :returns: A list of dictionaries, each representing a Twitch user.
        """
        example_users_list = [{ 
            '_id': 5582097,
            'broadcaster_language': 'en',
            'created_at': '2009-04-13T21:22:28Z',
            'display_name': 'Sarbandia',
            'followers': 1182,
            'game': 'Hearthstone: Heroes of Warcraft',
            'language': 'en',
            'logo': 'https://static-cdn.jtvnw.net/jtv_user_pictures/sarbandia-profile_image-6693b5952f31c847-300x300.jpeg',
            'mature': False,
            'name': 'sarbandia',
            'partner': False,
            'profile_banner': 'https://static-cdn.jtvnw.net/jtv_user_pictures/sarbandia-profile_banner-247cdbe62dbcf4d9-480.jpeg',
            'profile_banner_background_color': None,
            'status': 'Midrange shaman laddering',
            'updated_at': '2016-12-15T19:02:40Z',
            'url': 'https://www.twitch.tv/sarbandia',
            'video_banner': None,
            'views': 8168
        }]
        client = TwitchClient(client_id=client_id, oauth_token=oauth_token)
        team = client.teams.get(source)
        self.users_list = example_users_list
