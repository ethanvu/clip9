"""Tests the clipsplice module."""

from clip9.clipsplice import ClipSplicer

from pathlib import Path

import pytest
import requests
import responses

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


def test__get_clip_src_url_valid_thumbnail_url_ret_src():
    splicer = ClipSplicer(example_clip_list)
    src_url = splicer._get_clip_src_url(example_clip_list[0]['thumbnail_url'])
    assert ('https://clips-media-assets2.twitch.tv/AT-157589949-640x360.mp4'
            == src_url)


def test__get_clip_src_url_invalid_thumbnail_url_hostname_throws_exception():
    splicer = ClipSplicer(example_clip_list)
    with pytest.raises(ValueError):
        src_url = splicer._get_clip_src_url('https://twitch.tv/'
                                            '157589949-preview-480x272.jpg')


def test__get_clip_src_url_invalid_thumbnail_url_path_nums_throws_exception():
    splicer = ClipSplicer(example_clip_list)
    with pytest.raises(ValueError):
        src_url = splicer._get_clip_src_url('https://clips-media-assets.'
                                            'twitch.tv/15-preview-480x272.jpg')


def test__get_clip_src_url_invalid_thumbnail_url_path_else_throws_exception():
    splicer = ClipSplicer(example_clip_list)
    with pytest.raises(ValueError):
        src_url = splicer._get_clip_src_url('https://clips-media-assets.'
                                            'twitch.tv/157589949-preview.jpg')


@responses.activate
def test__download_clip_valid_url_success():
    path = './'
    responses.add(responses.GET,
                  'https://clips-media-assets2.twitch.tv/'
                  'AT-157589949-640x360.mp4',
                  body='a',
                  status=200,
                  content_type='binary/octet-stream')
    splicer = ClipSplicer(example_clip_list)
    splicer._download_clip(example_clip_list[0], path)
    clip_file = Path(f'{path}{example_clip_list[0]["id"]}.mp4')
    assert clip_file.is_file()
    clip_file.unlink()


@responses.activate
def test__download_clip_invalid_path_throws_exception():
    path = 'badpath/'
    responses.add(responses.GET,
                  'https://clips-media-assets2.twitch.tv/'
                  'AT-157589949-640x360.mp4',
                  body='a',
                  status=200,
                  content_type='binary/octet-stream')
    splicer = ClipSplicer(example_clip_list)
    with pytest.raises(FileNotFoundError):
        splicer._download_clip(example_clip_list[0], path)


@responses.activate
def test__download_clip_invalid_url_throws_exception():
    responses.add(responses.GET,
                  'https://clips-media-assets2.twitch.tv/'
                  'AT-157589949-640x360.mp4',
                  body=exmaple_clip_resp_bad_clip_num,
                  status=403,
                  content_type='application/xml')
    splicer = ClipSplicer(example_clip_list)
    with pytest.raises(requests.HTTPError):
        splicer._download_clip(example_clip_list[0], './')
