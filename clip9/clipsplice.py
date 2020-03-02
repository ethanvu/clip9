"""Module for ClipSplicer class."""

import logging

from moviepy.editor import concatenate_videoclips, VideoFileClip
import pyppeteer
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
        logging.info("Getting clip source URL from %s", embed_url)
        session = HTMLSession()
        resp = session.get(embed_url)

        if resp.status_code >= 400:
            resp.raise_for_status()

        script = """
            () => {
                var controls = document.getElementsByClassName(
                        "pl-controls-bottom")[0];
                controls.click();
                var settings = document.getElementsByClassName(
                        "qa-settings-button")[0];
                settings.click();
                var quality = document.getElementsByClassName(
                        "qa-quality-button")[0];
                quality.click();
                var qualities = document.getElementsByClassName(
                        "pl-quality-option-button");
                var highest_quality = qualities[qualities.length - 1];
                highest_quality.click();
            }
        """
        i = 1
        elem = None
        while ((i <= 3) and ((elem is None) or ('src' not in elem.attrs))):
            logging.info("Rendering %s: try %i", embed_url, i)
            try:
                resp.html.render(script=script, sleep=i)
            except pyppeteer.errors.ElementHandleError as e:
                logging.exception("Error when executing JavaScript to find "
                                  "video source URL on %s: %s", embed_url, e)
                elem = None
                i += 1
                continue
            elem = resp.html.xpath('/html/body/div[1]/div[1]/video',
                                   first=True)
            i += 1
        session.close()

        if elem is None:
            raise requests.HTTPError(f"Couldn't find video element after "
                                     f"rendering {embed_url}")
        if 'src' not in elem.attrs:
            raise requests.HTTPError(f"Couldn't find src attribute in video "
                                     f"element after rendering {embed_url}.")

        logging.debug("Attributes: %s", elem.attrs)
        logging.info("Found video src %s", elem.attrs['src'])
        return elem.attrs['src']

    def _download_clip(self, clip, path):
        """Downloads a clip as an mp4 file.

        :param clip: Info of a clip recieved from the Twitch Helix API.
        :param path: Path to save the clip in.
        :raises requests.HTTPError: When there is an error when downloading.
        """
        logging.info("Downloading clip %s", clip['id'])
        clip_src_url = self._get_clip_src_url(clip['embed_url'])
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
