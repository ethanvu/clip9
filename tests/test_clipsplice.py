"""Tests the clipsplice module"""

from clip9.clipsplice import ClipSplicer

import pytest

example_clip_list = [
    {
        'id': 'AwkwardHelplessSalamanderSwiftRage',
        'url': 'https://clips.twitch.tv/AwkwardHelplessSalamanderSwiftRage',
        'embed_url': 'https://clips.twitch.tv/embed?clip=AwkwardHelplessSalamanderSwiftRage',
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
        'thumbnail_url': 'https://clips-media-assets.twitch.tv/157589949-preview-480x272.jpg'
    }
]


def test__get_clip_src_url_valid_thumbnail_url_ret_src():
    splicer = ClipSplicer(example_clip_list)
    src_url = splicer._get_clip_src_url(example_clip_list[0]['thumbnail_url'])
    assert ('https://clips-media-assets2.twitch.tv/AT-157589949-640x360.mp4'
            == src_url)
