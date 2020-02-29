"""Tests the clipget module."""

import json
from unittest.mock import Mock

import pytest
import requests
import responses
from twitch import TwitchHelix
from twitch.resources import Clip
from twitch.resources import Video

from constants import BASE_HELIX_URL
from clipget import ClipGetter


example_client_id = 'uo6dggojyb8d6soh92zknwmi5ej1q2'
example_app_access_token = 'prau3ol6mg5glgek8m89ec2s9q5i3i'

example_users_list = [{
    '_id': 5582097,
    'broadcaster_language': 'en',
    'created_at': '2009-04-13T21:22:28Z',
    'display_name': 'Sarbandia',
    'followers': 1182,
    'game': 'Hearthstone: Heroes of Warcraft',
    'language': 'en',
    'logo': 'https://static-cdn.jtvnw.net/jtv_user_pictures/'
            'sarbandia-profile_image-6693b5952f31c847-300x300.jpeg',
    'mature': False,
    'name': 'sarbandia',
    'partner': False,
    'profile_banner': 'https://static-cdn.jtvnw.net/jtv_user_pictures/'
                      'sarbandia-profile_banner-247cdbe62dbcf4d9-480.jpeg',
    'profile_banner_background_color': None,
    'status': 'Midrange shaman laddering',
    'updated_at': '2016-12-15T19:02:40Z',
    'url': 'https://www.twitch.tv/sarbandia',
    'video_banner': None,
    'views': 8168
}, {
    '_id': 5582098,
    'broadcaster_language': 'es',
    'created_at': '2009-04-13T21:22:28Z',
    'display_name': 'Sarbandia2',
    'followers': 1182,
    'game': 'Hearthstone: Heroes of Warcraft',
    'language': 'es',
    'logo': 'https://static-cdn.jtvnw.net/jtv_user_pictures/'
            'sarbandia-profile_image-6693b5952f31c847-300x300.jpeg',
    'mature': False,
    'name': 'sarbandia2',
    'partner': False,
    'profile_banner': 'https://static-cdn.jtvnw.net/jtv_user_pictures/'
                      'sarbandia-profile_banner-247cdbe62dbcf4d9-480.jpeg',
    'profile_banner_background_color': None,
    'status': 'Midrange shaman laddering',
    'updated_at': '2016-12-15T19:02:40Z',
    'url': 'https://www.twitch.tv/sarbandia2',
    'video_banner': None,
    'views': 8168
}]

example_clips_resp = {
    'data': [
        {
            'id': 'RandomClip1',
            'url': 'https://clips.twitch.tv/AwkwardHelplessSalamanderSwiftRage',
            'embed_url': 'https://clips.twitch.tv/embed?clip=RandomClip1',
            'broadcaster_id': '5582097',
            'broadcaster_name': 'Sabradina',
            'creator_id': '123456',
            'creator_name': 'MrMarshall',
            'video_id': '1234567',
            'game_id': '33103',
            'language': 'en',
            'title': 'random1',
            'view_count': 250,
            'created_at': '2019-08-19T22:34:18Z',
            'thumbnail_url': 'https://clips-media-assets.twitch.tv/157589949-preview-480x272.jpg'
        },
        {
            'id': 'RandomClip2',
            'url': 'https://clips.twitch.tv/AwkwardHelplessSalamanderPogChamp',
            'embed_url': 'https://clips.twitch.tv/embed?clip=RandomClip2',
            'broadcaster_id': '5582097',
            'broadcaster_name': 'Sabradina',
            'creator_id': '123456',
            'creator_name': 'MrMarshall',
            'video_id': '1234567',
            'game_id': '33103',
            'language': 'en',
            'title': 'random1',
            'view_count': 150,
            'created_at': '2019-8-20T22:35:18Z',
            'thumbnail_url': 'https://clips-media-assets.twitch.tv/157589950-preview-480x272.jpg'
        },
    ],
    'pagination': {
        'cursor': 'eyJiIjpudWxsLCJhIjoiIn0'
    }
}

example_clips_resp2 = {
    'data': [
        {
            'id': 'RandomClip3',
            'url': 'https://clips.twitch.tv/AwkwardHelplessSalamanderSwiftRage',
            'embed_url': 'https://clips.twitch.tv/embed?clip=RandomClip1',
            'broadcaster_id': '5582098',
            'broadcaster_name': 'Sabradina2',
            'creator_id': '123456',
            'creator_name': 'MrMarshall',
            'video_id': '1234567',
            'game_id': '33103',
            'language': 'es',
            'title': 'random2',
            'view_count': 250,
            'created_at': '2019-08-19T22:34:18Z',
            'thumbnail_url': 'https://clips-media-assets.twitch.tv/157589949-preview-480x272.jpg'
        },
    ],
    'pagination': {
        'cursor': 'eyJiIjpudWxsLCJhIjoiIn0'
    }
}

example_clips_resp_no_clips = {
    'data': [],
    'pagination': {}
}

example_clips_resp_invalid_client_id_and_token = {
    'error': 'Unauthorized',
    'status': 401,
    'message': 'Must provide a valid Client-ID or OAuth token'
}


@responses.activate
def test__get_clips_valid_client_id_ret_clips():
    responses.add(responses.GET,
                  f'{BASE_HELIX_URL}/clips?'
                  f'broadcaster_id={example_users_list[0]["_id"]}&'
                  f'first=100',
                  body=json.dumps(example_clips_resp),
                  status=200,
                  content_type='application/json')
    getter = ClipGetter(example_users_list)

    clips = getter._get_clips(example_users_list[0]["_id"],
                              example_users_list[0]["name"],
                              client_id=example_client_id)
    assert len(clips) == 2
    assert clips[0]['id'] == 'RandomClip1'
    assert clips[1]['id'] == 'RandomClip2'


@responses.activate
def test__get_clips_valid_oauth_token_ret_clips():
    responses.add(responses.GET,
                  f'{BASE_HELIX_URL}/clips?'
                  f'broadcaster_id={example_users_list[0]["_id"]}&'
                  f'first=100',
                  body=json.dumps(example_clips_resp),
                  status=200,
                  content_type='application/json')

    getter = ClipGetter(example_users_list)
    clips = getter._get_clips(example_users_list[0]["_id"],
                              example_users_list[0]["name"],
                              oauth_token=example_app_access_token)
    assert len(clips) == 2
    assert clips[0]['id'] == 'RandomClip1'
    assert clips[1]['id'] == 'RandomClip2'


@responses.activate
def test__get_clips_no_clips_ret_no_clips():
    responses.add(responses.GET,
                  f'{BASE_HELIX_URL}/clips?'
                  f'broadcaster_id={example_users_list[0]["_id"]}&'
                  f'first=100',
                  body=json.dumps(example_clips_resp_no_clips),
                  status=200,
                  content_type='application/json')

    getter = ClipGetter(example_users_list)
    clips = getter._get_clips(example_users_list[0]["_id"],
                              example_users_list[0]["name"],
                              oauth_token=example_app_access_token)
    assert len(clips) == 0


@responses.activate
def test__get_clips_invalid_client_id_and_token_throw_exception():
    responses.add(responses.GET,
                  f'{BASE_HELIX_URL}/clips?'
                  f'broadcaster_id={example_users_list[0]["_id"]}&'
                  f'first=100',
                  body=json.dumps(example_clips_resp_invalid_client_id_and_token),
                  status=401,
                  content_type='application/json')

    getter = ClipGetter(example_users_list)
    with pytest.raises(requests.HTTPError):
        getter._get_clips(example_users_list[0]["_id"],
                          example_users_list[0]["name"])


def test__get_clip_video_views_clip_empty_video_id_ret_900():
    clip = Clip()
    clip.id = 'AwkwardHelplessSalamanderSwiftRage'
    clip.video_id = ''
    getter = ClipGetter(example_users_list)

    views = getter._get_clip_video_views(clip)
    assert 900 == views


def test__get_clip_video_views_clip_video_id_ret_views():
    clip = Clip()
    clip.id = 'AwkwardHelplessSalamanderSwiftRage'
    clip.video_id = '205586603'
    video = Video()
    video.view_count = 10
    getter = ClipGetter(example_users_list)
    getter.client = TwitchHelix(client_id=example_client_id)
    getter.client.get_videos = Mock(return_value=[video])

    views = getter._get_clip_video_views(clip)
    assert 10 == views


def test__get_clip_rating_low_clip_views_high_avg_ret_gt_1():
    expected_rating = 1
    getter = ClipGetter(example_users_list)
    rating = getter._get_clip_rating(250, 1000)
    assert expected_rating < rating


def test__get_clip_rating_low_clip_views_high_avg_ret_lt_1():
    expected_rating = 1
    getter = ClipGetter(example_users_list)
    rating = getter._get_clip_rating(150, 1000)
    assert expected_rating > rating


def test__get_good_clips_1_good_clip_ret_clips():
    getter = ClipGetter(example_users_list)
    getter._get_clip_video_views = Mock(return_value=1350)

    clips = getter._get_good_clips(example_clips_resp['data'])
    assert len(clips) == 1
    assert clips[0]['id'] == 'RandomClip1'


def test__get_good_clips_2_good_clip_ret_clips():
    getter = ClipGetter(example_users_list)
    getter._get_clip_video_views = Mock(return_value=450)

    clips = getter._get_good_clips(example_clips_resp['data'])
    assert len(clips) == 2
    assert clips[0]['id'] == 'RandomClip1'
    assert clips[1]['id'] == 'RandomClip2'


def test__get_good_clips_no_clips_ret_no_clips():
    getter = ClipGetter(example_users_list)

    clips = getter._get_good_clips(example_clips_resp_no_clips['data'])
    assert len(clips) == 0


@responses.activate
def test_get_clips_all_lang_valid_client_id_ret_clips():
    getter = ClipGetter(example_users_list)
    ret_clips = [example_clips_resp['data'], example_clips_resp2['data']]
    getter._get_clips = Mock(side_effect=ret_clips)
    ret_good = [[example_clips_resp['data'][0]],
                [example_clips_resp2['data'][0]]]
    getter._get_good_clips = Mock(side_effect=ret_good)

    clips = getter.get_clips(client_id=example_client_id)
    assert len(clips) == 2
    assert clips[0]['id'] == 'RandomClip1'
    assert clips[1]['id'] == 'RandomClip3'


@responses.activate
def test_get_clips_all_lang_valid_token_ret_clips():
    getter = ClipGetter(example_users_list)
    ret_clips = [example_clips_resp['data'], example_clips_resp2['data']]
    getter._get_clips = Mock(side_effect=ret_clips)
    ret_good = [[example_clips_resp['data'][0]],
                [example_clips_resp2['data'][0]]]
    getter._get_good_clips = Mock(side_effect=ret_good)

    clips = getter.get_clips(oauth_token=example_app_access_token)
    assert len(clips) == 2
    assert clips[0]['id'] == 'RandomClip1'
    assert clips[1]['id'] == 'RandomClip3'


@responses.activate
def test_get_clips_lang_en_ret_less_clips():
    getter = ClipGetter(example_users_list, lang={'en'})
    ret_clips = [example_clips_resp['data']]
    getter._get_clips = Mock(side_effect=ret_clips)
    ret_good = [[example_clips_resp['data'][0]]]
    getter._get_good_clips = Mock(side_effect=ret_good)

    clips = getter.get_clips(oauth_token=example_app_access_token)
    assert len(clips) == 1
    assert clips[0]['id'] == 'RandomClip1'
