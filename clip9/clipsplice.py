"""Module for ClipSplicer class."""

import logging

from moviepy.editor import concatenate_videoclips, VideoFileClip
import requests
from requests_html import HTMLSession

class ClipSplicer():
    """Downloads and splices Twitch clips into a video."""

    def __init__(self, clips_list):
        self.clips_list = clips_list


    def _get_clip_src_url(self, embed_url):
        """Gets the source URL of a clip given its embed URL.

        :param embed_url: Embed URL of the clip,
                          e.g. https://clips.twitch.tv/
                          embed?clip=AwkwardHelplessSalamanderSwiftRage
        :returns: Source URL of a clip.  This URL can be used to download the
                  the clip.
        :raises requests.HTTPError: When the source URL can't be found.
        """
        logging.info(f"Getting clip source URL from {embed_url}")
        session = HTMLSession()
        resp = session.get(embed_url)

        if (resp.status_code >= 400):
            resp.raise_for_status()

        i = 1
        elem = None
        while ((i <= 3) and ((elem is None) or ('src' not in elem.attrs))):
            logging.info(f"Rendering {embed_url}: try {i}")
            resp.html.render(sleep=i)
            elem = resp.html.xpath('/html/body/div[1]/div[1]/video',
                                   first=True)
            i += 1

        if (elem is None):
            raise requests.HTTPError(f"Couldn't find video element after "
                                     f"rendering {embed_url}")
        elif ('src' not in elem.attrs):
            raise requests.HTTPError(f"Couldn't find src attribute in video "
                                     f"element after rendering {embed_url}.")

        logging.info(f"Found video src {elem.attrs['src']}")
        logging.debug(f"Attributes: {elem.attrs}")
        return elem.attrs['src']


    def _download_clip(self, clip, path):
        """Downloads a clip as an mp4 file.

        :param clip: Info of a clip recieved from the Twitch Helix API.
        :param path: Path to save the clip in.
        :raises requests.HTTPError: When there is an error when downloading.
        """
        logging.info(f"Downloading clip {clip['id']}")
        clip_src_url = self._get_clip_src_url(clip['embed_url'])
        logging.info(f"Clip source URL: {clip_src_url}")
        resp = requests.get(clip_src_url, stream=True)

        if (resp.status_code >= 400):
            logging.warning(f"Error when downloading clip: {resp.status_code}")
            resp.raise_for_status()

        with open(f'{path}/{clip["id"]}.mp4', 'wb') as f:
            for chunk in resp.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
        logging.info(f"Downloaded {clip['id']}.mp4")


    def splice(self, result_file_name, clips_dir='./'):
        """Splices the clips in clips_list into an mp4, ogv, webm, or
        avi file.

        :param result_file_name: File name of the resulting video,
                                 e.g. ./result.mp4 or /var/tmp/final.avi
        :param clips_dir: Directory path to save the clip files in.
        """
        logging.info(f"Splicing {len(self.clips_list)} clips")
        file_list = []
        fail_list = []
        for clip in self.clips_list:
            try:
                self._download_clip(clip, clips_dir)
                clip_file = VideoFileClip(f'{clips_dir}/{clip["id"]}.mp4')
                file_list.append(clip_file)
            except requests.HTTPError as e:
                logging.error
                fail_list.append(clip['id'])
        if (fail_list):
            logging.warning(f"Some clips couldn't be downloaded: {fail_list}")

        if (len(file_list) > 0):
            result = concatenate_videoclips(file_list)
            logging.info(f"Writing {result_file_name}")
            if (result_file_name[-4:] == '.avi'):
                result.write_videofile(f'{result_file_name}', codec='png')
            else:
                result.write_videofile(f'{result_file_name}')
        else:
            logging.info("No clips to splice")
