"""Tests the clipsplice module."""

from unittest.mock import patch, mock_open

import pytest
from pytest_mock import mocker
import requests
import responses

from clipsplice import ClipSplicer
from constants import BASE_GQL_URL

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

example_clip_resp = """[{
    "data": {
        "clip": {
            "id": "157589949",
            "videoQualities": [
                {
                    "frameRate": 30,
                    "quality": "1080",
                    "sourceURL": "https://clips-media-assets2.twitch.tv/157589949.mp4",
                    "__typename": "ClipVideoQuality"
                },
                {
                    "frameRate": 30,
                    "quality": "720",
                    "sourceURL": "https://clips-media-assets2.twitch.tv/AT-157589949-1280x720.mp4",
                    "__typename": "ClipVideoQuality"
                },
                {
                    "frameRate": 30,
                    "quality": "480",
                    "sourceURL": "https://clips-media-assets2.twitch.tv/AT-157589949-854x480.mp4",
                    "__typename": "ClipVideoQuality"
                },
                {
                    "frameRate": 30,
                    "quality": "360",
                    "sourceURL": "https://clips-media-assets2.twitch.tv/AT-157589949-640x360.mp4",
                    "__typename": "ClipVideoQuality"
                }
            ],
            "__typename": "Clip"
        }
    },
    "extensions": {
        "durationMilliseconds": 64,
        "operationName": "VideoAccessToken_Clip",
        "requestID": "01EMDC8BCBWFYHVEV3PHBEEPYJ"
    }
}]"""

example_no_clip_resp = """[{
    "data": {"clip": null},
    "extensions": {
        "durationMilliseconds": 22,
        "operationName": "VideoAccessToken_Clip",
        "requestID": "01EMDDWHDV20X41P202C8AWJCP"
    }
}]"""

example_clip_error_resp = """[{
    "errors": [{
        "message": "Variable \\"slug\\" has invalid value null.\\nExpected type \\"ID!\\", found null.",
        "locations": [{"line": 1,"column": 29}]
    }],
    "extensions": {
        "durationMilliseconds": 1,
        "operationName": "VideoAccessToken_Clip",
        "requestID": "01EMDF967011BS701SZMR5EYF7"
    }
}]"""

example_clip_resp_bad_clip_num = """<?xml version="1.0" encoding="UTF-8"?>
<Error>
    <Code>AccessDenied</Code>
    <Message>Access Denied</Message>
    <RequestId>AF1E1AFC1E201EFF</RequestId>
    <HostId>LXM6CCdLUm9HptbJqr3+cx8tUe5YR5K6v0BXBS+yiIfc04Pcvb3a83t+oFmcCmd3QR2ehVz3bxw=</HostId>
</Error>
"""

class Element:
    """Represents an HTML element.  This is for testing purposes."""

    def __init__(self, attrs):
        self.attrs = attrs

@responses.activate
def test__get_clip_src_url_valid_clip_ret_src(mocker):
    expected_url = 'https://clips-media-assets2.twitch.tv/157589949.mp4'
    responses.add(responses.POST,
                  BASE_GQL_URL,
                  body=example_clip_resp,
                  status=200,
                  content_type='application/json')

    splicer = ClipSplicer(example_clip_list)
    src_url = splicer._get_clip_src_url(example_clip_list[0]['id'])
    assert expected_url == src_url

@responses.activate
def test__get_clip_src_url_clip_not_found_throws_exception(mocker):
    clip_id = 'a'
    responses.add(responses.POST,
                  BASE_GQL_URL,
                  body=example_no_clip_resp,
                  status=200,
                  content_type='application/json')

    splicer = ClipSplicer(example_clip_list)
    with pytest.raises(requests.HTTPError):
        splicer._get_clip_src_url(clip_id)

@responses.activate
def test__get_clip_src_url_failed_connection_throws_exception(mocker):
    responses.add(responses.POST,
                  BASE_GQL_URL,
                  status=400)

    splicer = ClipSplicer(example_clip_list)
    with pytest.raises(requests.HTTPError):
        splicer._get_clip_src_url(example_clip_list[0]['id'])

@responses.activate
def test__get_clip_src_url_clip_id_is_none_throws_exception(mocker):
    responses.add(responses.POST,
                  BASE_GQL_URL,
                  body=example_clip_error_resp,
                  status=200,
                  content_type='application/json')

    splicer = ClipSplicer(example_clip_list)
    with pytest.raises(requests.HTTPError):
        splicer._get_clip_src_url(None)

@responses.activate
def test__download_clip_valid_url_success(mocker):
    src_url = 'https://clips-media-assets2.twitch.tv/157589949.mp4'
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
    src_url = 'https://clips-media-assets2.twitch.tv/157589949.mp4'
    path = './'
    mocker.patch('clipsplice.ClipSplicer._get_clip_src_url',
                 return_value=src_url)
    responses.add(responses.GET,
                  src_url,
                  body=example_clip_resp_bad_clip_num,
                  status=403,
                  content_type='application/xml')

    splicer = ClipSplicer(example_clip_list)
    with pytest.raises(requests.HTTPError):
        splicer._download_clip(example_clip_list[0], path)

@responses.activate
def test__download_clip_invalid_path_throws_exception(mocker):
    src_url = 'https://clips-media-assets2.twitch.tv/157589949.mp4'
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
