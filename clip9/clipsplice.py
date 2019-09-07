"""Module for ClipSplicer class."""

import logging
import re

import requests

class ClipSplicer():
    """Downloads and splices Twitch clips into a video."""

    def __init__(self, clips_list):
        self.clips_list = clips_list


    def _get_clip_src_url(self, thumbnail_url):
        """Gets the source url of a clip given its thumbnail url."""
        logging.info(f"Getting clip source URL from {thumbnail_url}")
        if (re.match('https://clips-media-assets.twitch.tv/'
                     '[0-9][0-9][0-9][0-9]+-preview-480x272.jpg',
                     thumbnail_url) is None):
            raise ValueError(f"{thumbnail_url} is an invalid clip thumbnail "
                             f"URL to parse")
        nums = re.findall('[0-9][0-9][0-9][0-9]+', thumbnail_url)
        logging.info(f"Found nums {nums[0]}")
        return (f'https://clips-media-assets2.twitch.tv/AT-{nums[0]}'
                 '-640x360.mp4')


    def _download_clip(self, clip, path):
        """Downloads a clip as an MP4 file.

        :param clip: Info of a clip recieved from the Twitch Helix API.
        :param path: Path to save the clip in.
        """
        logging.info(f"Downloading clip {clip['id']}")
        clip_src_url = self._get_clip_src_url(clip['thumbnail_url'])
        logging.info(f"Clip source URL: {clip_src_url}")
        resp = requests.get(clip_src_url, stream=True)
        if (resp.status_code >= 400):
            logging.error(f"Error when downloading clip {resp.status_code}")
            resp.raise_for_status()
        with open(f'{path}/{clip["id"]}.mp4', 'wb') as f:
            for chunk in resp.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
        logging.info(f"Downloaded {clip['id']}.mp4")


    def splice(self, path='./'):
        """Splices the clips in clips_list into one video."""
        pass
