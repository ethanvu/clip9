"""Module for ClipSplicer class."""

import logging

from moviepy.editor import concatenate_videoclips, VideoFileClip
import requests

from constants import BASE_GQL_URL

class ClipSplicer():
    """Downloads and splices Twitch clips into a video."""

    def __init__(self, clips_list):
        self.clips_list = clips_list

    def _get_clip_src_url(self, clip_id):
        """Gets the source URL of a clip given its embed URL.

        :param clip_id: ID of the clip, e.g AwkwardHelplessSalamanderSwiftRage
        :returns: Source URL of a clip.  This URL can be used to download the
                  the clip.
        :raises requests.HTTPError: When the source URL can't be found.
        """
        logging.info("Getting clip source URL for %s", clip_id)
        header = {"Client-Id": "kimne78kx3ncx6brgo4mv6wki5h1ko"}
        data = [{
            "operationName": "VideoAccessToken_Clip",
            "variables": {"slug": clip_id},
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": ("9bfcc0177bffc730bd5a5a89005869d2773480cf1"
                                   "738c592143b5173634b7d15")
                }
            }
        }]
        resp = requests.post(BASE_GQL_URL, headers=header, json=data)

        if resp.status_code >= 400:
            logging.error("Error when getting info for clip %s", clip_id)
            resp.raise_for_status()

        json = resp.json()
        if 'errors' in json[0]:
            raise requests.HTTPError(f"Errors when finding info for clip "
                                     f"{clip_id}: {json[0]['errors']}")

        clip_info = json[0]['data']['clip']
        if clip_info is None:
            raise requests.HTTPError(f"Couldn't find clip {clip_id}")

        return clip_info['videoQualities'][0]['sourceURL']

    def _download_clip(self, clip, path):
        """Downloads a clip as an mp4 file.

        :param clip: Info of a clip recieved from the Twitch Helix API.
        :param path: Path to save the clip in.
        :raises requests.HTTPError: When there is an error when downloading.
        """
        logging.info("Downloading clip %s", clip['id'])
        clip_src_url = self._get_clip_src_url(clip['id'])
        resp = requests.get(clip_src_url, stream=True)

        if resp.status_code >= 400:
            logging.error("Error when downloading clip: %s", resp.status_code)
            resp.raise_for_status()

        with open(f'{path}/{clip["id"]}.mp4', 'wb') as f:
            for chunk in resp.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
        logging.info("Downloaded %s.mp4", clip['id'])

    def _splice_clips(self, result_file_name, file_list):
        result = concatenate_videoclips(file_list)
        if result_file_name[-4:] == '.avi':
            result.write_videofile(f'{result_file_name}', codec='png')
        else:
            result.write_videofile(f'{result_file_name}')

    def splice(self, result_file_name, clips_dir='./'):
        """Splices the clips in clips_list into an mp4, ogv, webm, or
        avi file.

        :param result_file_name: File name of the resulting video,
                                 e.g. ./result.mp4 or /var/tmp/final.avi
        :param clips_dir: Directory path to save the clip files in.
        """
        logging.info("Splicing %s clips", len(self.clips_list))
        file_list = []
        fail_list = []
        for clip in self.clips_list:
            try:
                self._download_clip(clip, clips_dir)
                clip_file = VideoFileClip(f'{clips_dir}/{clip["id"]}.mp4',
                                          target_resolution=(1080, 1920))
                file_list.append(clip_file)
            except requests.HTTPError:
                logging.exception("HTTPError when downloading %s", clip['id'])
                fail_list.append(clip['id'])
        if fail_list:
            logging.warning("Some clips couldn't be downloaded: %s", fail_list)

        if len(file_list) > 0:
            logging.info("Writing %s", result_file_name)
            self._splice_clips(result_file_name, file_list)
        else:
            logging.info("No clips to splice")
