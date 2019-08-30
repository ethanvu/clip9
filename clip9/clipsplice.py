"""Module for ClipSplicer class."""

import logging
import re


class ClipSplicer():
    """Downloads and splices Twitch clips into a video."""

    def __init__(self, clips_list):
        self.clips_list = clips_list
    
    def _get_clip_src_url(self, thumbnail_url):
        """Gets the source url of a clip given its thumbnail url."""
        nums = re.findall('[0-9][0-9][0-9][0-9]+', thumbnail_url)
        return f'https://clips-media-assets2.twitch.tv/AT-{nums[0]}-640x360.mp4'
