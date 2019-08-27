"""Module for the ClipGetter class."""

import logging
import math

import requests
from twitch import TwitchHelix

from clip9.constants import BASE_TWITCHMETRICS_URL

class ClipGetter:
    """Gets 'good' clips for streamers in a Twitch team since a certain
    time until now.
    """

    def __init__(self, users_list, start_time=None, end_time=None, lang=None):
        """Initializes a new ClipGetter

        :param users_list: List of dictionaries of information of users.
        :param start_time: Beginning of time window of clips to get.  RFC 3339
            format.
        :param end_time: End of time window of clips to get.  RFC 3339 format.
        :param lang: Language of clips to get.  Default is all languages.
        """
        self.users_list = users_list
        self.start_time = start_time
        self.end_time = end_time
        self.lang = 'en'
        self.clips_list = None


    @staticmethod
    def _get_avg_viewers_in_past_week(user_id, user_name):
        """Return the average viewers of a user in the past week."""
        logging.info(f"Getting average view count for {user_name}")
        resp = requests.get(f'{BASE_TWITCHMETRICS_URL}c/{user_id}-{user_name}'
                            f'/recent_viewership_values')

        if (resp.status_code == 404):
            logging.info(f"Couldn't find weekly viewer stats for {user_name}."
                         f"Skipping getting clips for this user.")
            return 0
        elif (resp.status_code != 200):
            logging.error(f"Error when getting weekly viewer stats of "
                          f"{user_name}: Got status code {resp.status_code}")
            resp.raise_for_status()

        resp_json = resp.json()

        view_snap_count = 0
        total_views = 0
        for view_snapshot in resp_json:
            view_snap_count = view_snap_count + 1
            total_views = total_views + view_snapshot[1]
        logging.debug(f"view_snap_count = {view_snap_count}, "
                      f"total_views = {total_views}")

        if (view_snap_count == 0):
            logging.info(f"Avg views in the past week for {user_name} is "
                         f"0")
            return 0
        avg_views = total_views / view_snap_count
        logging.info(f"Average views in the past week for {user_name} is "
                     f"{avg_views}")
        return avg_views


    @staticmethod
    def _get_clip_rating(clip_views, avg_viewers):
        """Return a rating for the given clip."""
        return clip_views / (avg_viewers/9 + 100)


    @staticmethod
    def _get_good_clips(user_id, user_name, client_id=None, oauth_token=None):
        """Return a list of information of 'good' clips for a user since a
        start time until now.
        """
        avg_views = self._get_avg_viewers_in_past_week(user_id, user_name)
        if (avg_views == 0):
            logging.info(f"{user_name} didn't stream since {self.start_time}."
                         f"Skipping getting clips for {user_name}.")
            return None

        logging.info(f"Getting clips for {user_name} since {self.start_time}")
        client = TwitchHelix(client_id, oauth_token)
        clips = client.get_clips(broadcaster_id=userid)
        clip_headers = {'Authorization': f'Bearer {self.access_token}'}
        clip_params = {
            'broadcaster_id': streamer_id,
            'started_at': self.start_time,
        }
        resp = requests.get(f'https://api.twitch.tv/helix/clips', 
                            headers=clip_headers, params=clip_params)
        resp_json = resp.json()

        if (resp.status_code >= 400):
            logging.error(f"Error when getting clips of streamer "
                          f"{streamer_name}: {resp_json['message']}")
            resp.raise_for_status()

        logging.info(f"Got a list of clips of streamer {streamer_name}")
        all_clips = resp_json['data']
        good_clips = []
        for clip in all_clips:
            logging.debug(f"Clip {clip['id']} has {clip['view_count']} views")
            clip['rating'] = self._get_clip_rating(clip['view_count'],
                                                   avg_views)
            logging.info(f"Clip {clip['id']} rating {clip['rating']}")
            if (clip['rating'] >= 1):
                logging.info(f"Clip {clip['id']} is 'good'")
                good_clips.append(clip)
            else:
                break
        logging.info(f"Found {len(good_clips)} good clip(s) for "
                     f"{streamer_name}")
        return good_clips


    def get_clips(self, client_id=None, oauth_token=None):
        """Return a list of information of 'good' clips for streamers in a
        Twitch Team.
        
        The format of the information of each clip can be seen here
        https://dev.twitch.tv/docs/api/reference/#get-clips
        """
        self.access_token = self._get_access_token()
        team_members = self._get_team_members()
        team_clips = []
        for team_member in team_members:
            if (team_member['broadcaster_language'] == 'en'):
                clips = self._get_good_clips(team_member['_id'],
                                             team_member['name'])
                logging.info(clips)
                if clips:
                    team_clips.extend(clips)
        return team_clips
