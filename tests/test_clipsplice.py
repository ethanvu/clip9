"""Tests the clipsplice module."""

from pathlib import Path
from unittest.mock import patch, mock_open

import pytest
from pytest_mock import mocker
import requests
import requests_html
import responses

from clipsplice import ClipSplicer


example_clip_list = [
    {
        'id': 'AwkwardHelplessSalamanderSwiftRage',
        'url': 'https://clips.twitch.tv/AwkwardHelplessSalamanderSwiftRage',
        'embed_url': 'https://clips.twitch.tv/'
                     'embed?clip=AwkwardHelplessSalamanderSwiftRage',
        'broadcaster_id': '67955580',
        'broadcaster_name': 'ChewieMelodies',
        'creator_id': '53834192',
        'creator_name': 'BlackNova03',
        'video_id': '205586603',
        'game_id': '488191',
        'language': 'en',
        'title': 'babymetal',
        'view_count': 10,
        'created_at': '2017-11-30T22:34:18Z',
        'thumbnail_url': 'https://clips-media-assets.twitch.tv/'
                         '157589949-preview-480x272.jpg'
    },
    {
        'id': 'CharmingBelovedFloofNerfRedBlaster',
        'url': 'https://clips.twitch.tv/CharmingBelovedFloofNerfRedBlaster',
        'embed_url': 'https://clips.twitch.tv/embed?'
                     'clip=CharmingBelovedFloofNerfRedBlaster',
        'broadcaster_id': '67955580',
        'broadcaster_name': 'ChewieMelodies',
        'creator_id': '43819111',
        'creator_name': 'TheLoneWolf09',
        'video_id': '',
        'game_id': '488191',
        'language': 'en',
        'title': 'Playing songs by ear ♪♫',
        'view_count': 901,
        'created_at': '2017-05-10T00:53:06Z',
        'thumbnail_url': 'https://clips-media-assets2.twitch.tv/'
                         '25242479696-offset-18536-preview-480x272.jpg'
    }
]

exmaple_clip_resp_bad_clip_num = """<?xml version="1.0" encoding="UTF-8"?>
<Error>
    <Code>AccessDenied</Code>
    <Message>Access Denied</Message>
    <RequestId>AF1E1AFC1E201EFF</RequestId>
    <HostId>LXM6CCdLUm9HptbJqr3+cx8tUe5YR5K6v0BXBS+yiIfc04Pcvb3a83t+oFmcCmd3QR2ehVz3bxw=</HostId>
</Error>
"""

example_embed_url_resp = """<!DOCTYPE html>
<html class="twitch-player">
<head>
    <title>Twitch</title>
</head>
<body style="margin: 0">
    <div class="player" id="video-playback">
        <div class="player-video">
            <video autoplay="" preload="auto" webkit-playsinline="" playsinline="" src="https://clips-media-assets2.twitch.tv/AT-157589949-640x360.mp4"></video>
        </div>
    </div>
</body>
</html>
"""

example_embed_url_resp_no_src = """<!DOCTYPE html>
<html class="twitch-player">
<head>
    <title>Twitch</title>
</head>
<body style="margin: 0">
    <div class="player" id="video-playback">
        <div class="player-video">
            <video autoplay="" preload="auto" webkit-playsinline="" playsinline=""></video>
        </div>
    </div>
</body>
</html>
"""

example_embed_url_resp_no_video = """<!DOCTYPE html>
<html class="twitch-player">
<head>
    <title>Twitch</title>
</head>
<body style="margin: 0">
    <div class="player" id="video-playback">
        <div class="player-video">
        </div>
    </div>
</body>
</html>
"""

class Element:
    """Represents an HTML element.  This is for testing purposes."""

    def __init__(self, attrs):
        self.attrs = attrs


@responses.activate
def test__get_clip_src_url_valid_thumbnail_url_ret_src(mocker):
    responses.add(responses.GET,
                  example_clip_list[0]['embed_url'],
                  body=example_embed_url_resp,
                  status=200,
                  content_type='text/html')
    mocker.patch('requests_html.HTML.render')

    splicer = ClipSplicer(example_clip_list)
    src_url = splicer._get_clip_src_url(example_clip_list[0]['embed_url'])
    assert ('https://clips-media-assets2.twitch.tv/AT-157589949-640x360.mp4'
            == src_url)


@responses.activate
def test__get_clip_src_url_valid_url_with_retry_ret_src(mocker):
    responses.add(responses.GET,
                  example_clip_list[0]['embed_url'],
                  body=example_embed_url_resp,
                  status=200,
                  content_type='text/html')
    mocker.patch('requests_html.HTML.render')
    attrs = {
        'src': 'https://clips-media-assets2.twitch.tv/AT-157589949-640x360.mp4'
    }
    elem = Element(attrs=attrs)
    mocker.patch('requests_html.HTML.xpath', side_effect=[None, elem])

    splicer = ClipSplicer(example_clip_list)
    src_url = splicer._get_clip_src_url(example_clip_list[0]['embed_url'])
    assert ('https://clips-media-assets2.twitch.tv/AT-157589949-640x360.mp4'
            == src_url)


@responses.activate
def test__get_clip_src_url_elem_not_found_throws_exception(mocker):
    embed_url = 'https://clips.twitch.tv/embed?clip=a'
    responses.add(responses.GET,
                  embed_url,
                  body=example_embed_url_resp_no_src,
                  status=200,
                  content_type='text/html')
    mocker.patch('requests_html.HTML.render')

    splicer = ClipSplicer(example_clip_list)
    with pytest.raises(requests.HTTPError):
        splicer._get_clip_src_url(embed_url)


@responses.activate
def test__get_clip_src_url_missing_src_throws_exception(mocker):
    embed_url = 'https://clips.twitch.tv/'
    responses.add(responses.GET,
                  embed_url,
                  body=example_embed_url_resp_no_video,
                  status=200,
                  content_type='text/html')
    mocker.patch('requests_html.HTML.render')

    splicer = ClipSplicer(example_clip_list)
    with pytest.raises(requests.HTTPError):
        splicer._get_clip_src_url(embed_url)


@responses.activate
def test__get_clip_src_url_failed_connection_throws_exception(mocker):
    embed_url = 'https://clips.twitch.tv/embed?clip=a'
    responses.add(responses.GET,
                  example_clip_list[0]['embed_url'],
                  status=400)
    mocker.patch('requests_html.HTML.render')

    splicer = ClipSplicer(example_clip_list)
    with pytest.raises(requests.HTTPError):
        splicer._get_clip_src_url(example_clip_list[0]['embed_url'])


@responses.activate
def test__download_clip_valid_url_success(mocker):
    src_url = 'https://clips-media-assets2.twitch.tv/AT-157589949-640x360.mp4'
    path = './'
    mocker.patch('clipsplice.ClipSplicer._get_clip_src_url',
                 return_value=src_url)
    responses.add(responses.GET,
                  src_url,
                  body='a',
                  status=200,
                  content_type='binary/octet-stream')
    m = mocker.patch('builtins.open', mocker.mock_open())

    splicer = ClipSplicer(example_clip_list)
    splicer._download_clip(example_clip_list[0], path)
    m.assert_called_with(f'{path}/{example_clip_list[0]["id"]}.mp4', 'wb')
    m().write.assert_called_once_with(b'a')


@responses.activate
def test__download_clip_invalid_url_throws_exception(mocker):
    src_url = 'https://clips-media-assets2.twitch.tv/AT-157589949-640x360.mp4'
    path = './'
    mocker.patch('clipsplice.ClipSplicer._get_clip_src_url',
                 return_value=src_url)
    responses.add(responses.GET,
                  src_url,
                  body=exmaple_clip_resp_bad_clip_num,
                  status=403,
                  content_type='application/xml')

    splicer = ClipSplicer(example_clip_list)
    with pytest.raises(requests.HTTPError):
        splicer._download_clip(example_clip_list[0], path)


@responses.activate
def test__download_clip_invalid_path_throws_exception(mocker):
    src_url = 'https://clips-media-assets2.twitch.tv/AT-157589949-640x360.mp4'
    path = '/badpath/'
    mocker.patch('clipsplice.ClipSplicer._get_clip_src_url',
                 return_value=src_url)
    responses.add(responses.GET,
                  src_url,
                  body='a',
                  status=200,
                  content_type='application/xml')

    splicer = ClipSplicer(example_clip_list)
    with pytest.raises(FileNotFoundError):
        splicer._download_clip(example_clip_list[0], path)


@pytest.mark.filterwarnings('ignore::UserWarning')
def test_splice_valid_clips_mp4_success(mocker):
    result_file_name = './result.mp4'
    clips_dir = 'tests/resources/'
    mocker.patch('clipsplice.ClipSplicer._download_clip')

    splicer = ClipSplicer(example_clip_list)
    splicer.splice(result_file_name, clips_dir=clips_dir)
    result_file = Path(f'{result_file_name}')
    assert result_file.is_file()
    result_file.unlink()


@pytest.mark.filterwarnings('ignore::UserWarning')
def test_splice_valid_clips_ogv_success(mocker):
    result_file_name = './result.ogv'
    clips_dir = 'tests/resources/'
    mocker.patch('clipsplice.ClipSplicer._download_clip')

    splicer = ClipSplicer(example_clip_list)
    splicer.splice(result_file_name, clips_dir=clips_dir)
    result_file = Path(f'{result_file_name}')
    assert result_file.is_file()
    result_file.unlink()


@pytest.mark.filterwarnings('ignore::UserWarning')
def test_splice_valid_clips_webm_success(mocker):
    result_file_name = './result.webm'
    clips_dir = 'tests/resources/'
    mocker.patch('clipsplice.ClipSplicer._download_clip')

    splicer = ClipSplicer(example_clip_list)
    splicer.splice(result_file_name, clips_dir=clips_dir)
    result_file = Path(f'{result_file_name}')
    assert result_file.is_file()
    result_file.unlink()


@pytest.mark.filterwarnings('ignore::UserWarning')
def test_splice_valid_clips_avi_success(mocker):
    result_file_name = './result.avi'
    clips_dir = 'tests/resources/'
    mocker.patch('clipsplice.ClipSplicer._download_clip')

    splicer = ClipSplicer(example_clip_list)
    splicer.splice(result_file_name, clips_dir=clips_dir)
    result_file = Path(f'{result_file_name}')
    assert result_file.is_file()
    result_file.unlink()


def test_splice_invalid_clips_no_result_file(mocker):
    result_file_name = './result.mp4'
    mocker.patch('clipsplice.ClipSplicer._download_clip',
                 side_effect=requests.HTTPError)

    splicer = ClipSplicer(example_clip_list)
    splicer.splice(result_file_name)
    result_file = Path(f'{result_file_name}')
    assert not result_file.is_file()


def test_splice_no_clips_no_result_file():
    result_file_name = './result.mp4'

    splicer = ClipSplicer([])
    splicer.splice(result_file_name)
    result_file = Path(f'{result_file_name}')
    assert not result_file.is_file()
