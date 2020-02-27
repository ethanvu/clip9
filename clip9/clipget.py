"""Module for the ClipGetter class."""

import logging

import requests
from twitch import TwitchHelix
from twitch.resources import Clip


class ClipGetter:
    """Gets 'good' clips for streamers in a Twitch team since a certain
    time until now.
    """

    def __init__(self, users_list, started_at=None, ended_at=None, lang=None):
        """Initializes a new ClipGetter

        :param users_list: List of dictionaries of information of users.
        :param started_at: Beginning of time window of clips to get in
                           RFC 3339 format.
        :param ended_at: End of time window of clips to get in RFC 3339
                         format.
        :param lang: Language of clips to get.  Default is all languages.
        """
        self.users_list = users_list
        self.started_at = started_at
        self.ended_at = ended_at
        self.lang = lang
        self.client = None


    def _get_clips(self, user_id, user_name, client_id=None, oauth_token=None):
        """Returns a list of clips for a user."""
        logging.info("Getting clips for %s", user_name)
        clip_headers = {}
        if client_id is not None:
            clip_headers['Client-ID'] = client_id
        if oauth_token is not None:
            clip_headers['Authorization'] = f'Bearer {oauth_token}'
        clip_params = {
            'broadcaster_id': user_id,
            'started_at': self.started_at,
            'ended_at': self.ended_at,
            'first': 100,
        }
        resp = requests.get(f'https://api.twitch.tv/helix/clips',
                            headers=clip_headers, params=clip_params)
        resp_json = resp.json()

        if resp.status_code >= 400:
            logging.error("Error when getting clips of streamer %s: %s",
                          user_name, resp_json['message'])
            resp.raise_for_status()

        logging.info("Got a list of clips of streamer %s", user_name)
        clips_json = resp_json['data']
        clips = []
        for clip_json in clips_json:
            clips.append(Clip.construct_from(clip_json))
        return clips


    def _get_clip_video_views(self, clip):
        """Returns the view count of the video that a clip was created from."""
        logging.info("Getting video views for clip %s", clip['id'])
        if clip['video_id'] == '':
            return 900  # Default video views
        video = self.client.get_videos(video_ids=[clip['video_id']])[0]
        return video.view_count


    def _get_clip_rating(self, clip_views, video_views):
        """Return a rating given the view count of a clip and a video."""
        return clip_views / (video_views/9 + 100)


    def _get_good_clips(self, clips):
        """Return a subset of 'good' clips from a list of clips."""
        logging.info("Getting good clips from %s clip(s)", len(clips))
        good_clips = []
        for clip in clips:
            logging.debug("Clip %s by %s has %s views", clip['id'],
                          clip['broadcaster_name'], clip['view_count'])
            video_views = self._get_clip_video_views(clip)
            logging.debug("Clip %s's video %s has %s views", clip['id'],
                          clip['video_id'], video_views)
            clip['rating'] = self._get_clip_rating(clip['view_count'],
                                                   video_views)
            logging.info("Clip %s rating %s", clip['id'], clip['rating'])
            if clip['rating'] >= 1:
                logging.info("Clip %s is 'good'", clip['id'])
                good_clips.append(clip)
        return good_clips


    def get_clips(self, client_id=None, oauth_token=None):
        """Return a list of information of 'good' clips from a list of
        users.

        The format of the information of each clip can be found here:
        https://dev.twitch.tv/docs/api/reference/#get-clips
        """
        logging.info("Getting clips")
        self.client = TwitchHelix(client_id=client_id, oauth_token=oauth_token)
        total_clips = []
        for user in self.users_list:
            if (self.lang is None
                    or user['broadcaster_language'] == self.lang):
                clips = self._get_clips(user['_id'], user['name'],
                                        client_id, oauth_token)
                good_clips = self._get_good_clips(clips)
                logging.info("Found %s good clip(s) for %s", len(good_clips),
                             user['name'])
                if good_clips:
                    total_clips.extend(good_clips)
        logging.info("Got %s clips", len(total_clips))
        return total_clips
