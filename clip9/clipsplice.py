"""Module for ClipSplicer class."""

import logging

import requests
from requests_html import HTMLSession

class ClipSplicer():
    """Downloads and splices Twitch clips into a video."""

    def __init__(self, clips_list):
        self.clips_list = clips_list


    def _get_clip_src_url(self, embed_url):
        """Gets the source url of a clip given its embed url."""
        logging.info(f"Getting clip source URL from {embed_url}")
        session = HTMLSession()
        resp = session.get(embed_url)

        if (resp.status_code >= 400):
            resp.raise_for_status()

        resp.html.render(sleep=1)
        elem = resp.html.xpath('/html/body/div[1]/div[1]/video', first=True)

        if (elem is None):
            raise ValueError("Couldn't find the proper video tag.")
        elif ('src' not in elem.attrs):
            raise ValueError("Couldn't src attribute.  May need to rerender.")

        logging.info(f"Found video elem.  Attributes: {elem.attrs}")
        return elem.attrs['src']


    def _download_clip(self, clip, path):
        """Downloads a clip as an MP4 file.

        :param clip: Info of a clip recieved from the Twitch Helix API.
        :param path: Path to save the clip in.
        """
        logging.info(f"Downloading clip {clip['id']}")
        clip_src_url = self._get_clip_src_url(clip['embed_url'])
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


    def splice(self, result_base_name, clips_path='./', result_path='./'):
        """Splices the clips in clips_list into one video."""
        pass
