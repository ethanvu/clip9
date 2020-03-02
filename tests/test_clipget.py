"""Tests the clipget module."""

import json

import pytest
import requests
import responses

from constants import BASE_HELIX_URL
from constants import BASE_TWITCHMETRICS_URL
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
    'language': 'en',
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

example_user_list_empty = []

example_twitchmetrics_viewership_resp = [
    ['2019-08-19T00:20:01.000Z', 950, 'Counter-Strike: Global Offensive'],
    ['2019-08-19T00:30:01.000Z', 1000, 'Counter-Strike: Global Offensive'],
    ['2019-08-19T00:40:01.000Z', 1050, 'Counter-Strike: Global Offensive']
]

example_twitchmetrics_viewership_resp_doesnt_exist = """<!DOCTYPE html>
<html>
<head>
  <title>Page not found (404) - Twitchmetrics</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <link href="/error_page.css" rel="stylesheet" type="text/css">
</head>

<body>
<!-- This file lives in public/500.html -->
  <div class="dialog">
    <img src="/OhMyDog.png">
    <h1>Page not found</h1>
    <p>
      This page probably isn't what you're looking for.
    </p>
    <p>
      <a href="/">click here</a> to go back home for now
    </p>
  </div>
</body>
</html>
"""

example_twitchmetrics_viewership_resp_empty = []

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

example_clips_resp_invalid_started_or_ended_at = {
    'error': 'Bad Request',
    'status': 400,
    'message': 'parsing time "a" as "2006-01-02T15:04:05Z07:00": cannot parse "a" as "2006"'
}


@responses.activate
def test__get_avg_viewers_in_past_week_user_exists_ret_avg():
    expected_avg = 1000
    responses.add(responses.GET,
                  f'{BASE_TWITCHMETRICS_URL}/c/{example_users_list[0]["_id"]}-'
                  f'{example_users_list[0]["name"]}/recent_viewership_values',
                  body=json.dumps(example_twitchmetrics_viewership_resp),
                  status=200,
                  content_type='application/json')

    getter = ClipGetter(example_users_list)
    avg = getter._get_avg_viewers_in_past_week(example_users_list[0]['_id'],
                                               example_users_list[0]['name'])
    assert expected_avg == avg


@responses.activate
def test__get_avg_viewers_in_past_week_user_doesnt_exist_ret_0():
    expected_avg = 0
    responses.add(responses.GET,
                  f'{BASE_TWITCHMETRICS_URL}/c/{example_users_list[0]["_id"]}-'
                  f'{example_users_list[0]["name"]}/recent_viewership_values',
                  body=example_twitchmetrics_viewership_resp_doesnt_exist,
                  status=404,
                  content_type='text/html')

    getter = ClipGetter(example_users_list)
    avg = getter._get_avg_viewers_in_past_week(example_users_list[0]['_id'],
                                               example_users_list[0]['name'])
    assert expected_avg == avg


@responses.activate
def test__get_avg_viewers_in_past_week_user_didnt_stream_ret_0():
    expected_avg = 0
    responses.add(responses.GET,
                  f'{BASE_TWITCHMETRICS_URL}/c/{example_users_list[0]["_id"]}-'
                  f'{example_users_list[0]["name"]}/recent_viewership_values',
                  body=json.dumps(example_twitchmetrics_viewership_resp_empty),
                  status=200,
                  content_type='application/json')

    getter = ClipGetter(example_users_list)
    avg = getter._get_avg_viewers_in_past_week(example_users_list[0]['_id'],
                                               example_users_list[0]['name'])
    assert expected_avg == avg


@responses.activate
def test__get_avg_viewers_in_past_week_cant_find_user_ret_0():
    expected_avg = 0
    responses.add(responses.GET,
                  f'{BASE_TWITCHMETRICS_URL}/c/{example_users_list[0]["_id"]}-'
                  f'{example_users_list[0]["name"]}/recent_viewership_values',
                  status=404,
                  content_type='text/html')

    getter = ClipGetter(example_users_list)
    avg = getter._get_avg_viewers_in_past_week(example_users_list[0]['_id'],
                                               example_users_list[0]['name'])
    assert expected_avg == avg


@responses.activate
def test__get_avg_viewers_in_past_week_gt_400_status_code_throws_exception():
    responses.add(responses.GET,
                  f'{BASE_TWITCHMETRICS_URL}/c/{example_users_list[0]["_id"]}-'
                  f'{example_users_list[0]["name"]}/recent_viewership_values',
                  status=400,
                  content_type='text/html')

    getter = ClipGetter(example_users_list)
    with pytest.raises(requests.HTTPError):
        getter._get_avg_viewers_in_past_week(example_users_list[0]['_id'],
                                             example_users_list[0]['name'])


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


@responses.activate
def test__get_good_clips_valid_client_id_ret_clips():
    responses.add(responses.GET,
                  f'{BASE_TWITCHMETRICS_URL}/c/{example_users_list[0]["_id"]}-'
                  f'{example_users_list[0]["name"]}/recent_viewership_values',
                  body=json.dumps(example_twitchmetrics_viewership_resp),
                  status=200,
                  content_type='application/json')
    responses.add(responses.GET,
                  f'{BASE_HELIX_URL}/clips?'
                  f'broadcaster_id={example_users_list[0]["_id"]}',
                  body=json.dumps(example_clips_resp),
                  status=200,
                  content_type='application/json')

    getter = ClipGetter(example_users_list)
    clips = getter._get_good_clips(example_users_list[0]["_id"],
                                   example_users_list[0]["name"],
                                   client_id=example_client_id)
    assert len(clips) == 1
    assert clips[0]['id'] == 'RandomClip1'


@responses.activate
def test__get_good_clips_valid_oauth_token_ret_clips():
    responses.add(responses.GET,
                  f'{BASE_TWITCHMETRICS_URL}/c/{example_users_list[0]["_id"]}-'
                  f'{example_users_list[0]["name"]}/recent_viewership_values',
                  body=json.dumps(example_twitchmetrics_viewership_resp),
                  status=200,
                  content_type='application/json')
    responses.add(responses.GET,
                  f'{BASE_HELIX_URL}/clips?'
                  f'broadcaster_id={example_users_list[0]["_id"]}',
                  body=json.dumps(example_clips_resp),
                  status=200,
                  content_type='application/json')

    getter = ClipGetter(example_users_list)
    clips = getter._get_good_clips(example_users_list[0]["_id"],
                                   example_users_list[0]["name"],
                                   oauth_token=example_app_access_token)
    assert len(clips) == 1
    assert clips[0]['id'] == 'RandomClip1'


@responses.activate
def test__get_good_clips_didnt_stream_ret_no_clips():
    responses.add(responses.GET,
                  f'{BASE_TWITCHMETRICS_URL}/c/{example_users_list[0]["_id"]}-'
                  f'{example_users_list[0]["name"]}/recent_viewership_values',
                  body=json.dumps(example_twitchmetrics_viewership_resp_empty),
                  status=200,
                  content_type='application/json')

    getter = ClipGetter(example_users_list)
    clips = getter._get_good_clips(example_users_list[0]["_id"],
                                   example_users_list[0]["name"],
                                   oauth_token=example_app_access_token)
    assert len(clips) == 0


@responses.activate
def test__get_good_clips_no_clips_ret_no_clips():
    responses.add(responses.GET,
                  f'{BASE_TWITCHMETRICS_URL}/c/{example_users_list[0]["_id"]}-'
                  f'{example_users_list[0]["name"]}/recent_viewership_values',
                  body=json.dumps(example_twitchmetrics_viewership_resp),
                  status=200,
                  content_type='application/json')
    responses.add(responses.GET,
                  f'{BASE_HELIX_URL}/clips?'
                  f'broadcaster_id={example_users_list[0]["_id"]}',
                  body=json.dumps(example_clips_resp_no_clips),
                  status=200,
                  content_type='application/json')

    getter = ClipGetter(example_users_list)
    clips = getter._get_good_clips(example_users_list[0]["_id"],
                                   example_users_list[0]["name"],
                                   oauth_token=example_app_access_token)
    assert len(clips) == 0


@responses.activate
def test__get_good_clips_invalid_client_id_and_token_throw_exception():
    responses.add(responses.GET,
                  f'{BASE_TWITCHMETRICS_URL}/c/{example_users_list[0]["_id"]}-'
                  f'{example_users_list[0]["name"]}/recent_viewership_values',
                  body=json.dumps(example_twitchmetrics_viewership_resp),
                  status=200,
                  content_type='application/json')
    responses.add(responses.GET,
                  f'{BASE_HELIX_URL}/clips?'
                  f'broadcaster_id={example_users_list[0]["_id"]}',
                  body=json.dumps(example_clips_resp_invalid_client_id_and_token),
                  status=401,
                  content_type='application/json')

    getter = ClipGetter(example_users_list)
    with pytest.raises(requests.HTTPError):
        getter._get_good_clips(example_users_list[0]["_id"],
                               example_users_list[0]["name"])


@responses.activate
def test__get_good_clips_valid_started_at_ret_clips():
    started_at = '2019-08-19T00:00:00Z'
    responses.add(responses.GET,
                  f'{BASE_TWITCHMETRICS_URL}/c/{example_users_list[0]["_id"]}-'
                  f'{example_users_list[0]["name"]}/recent_viewership_values',
                  body=json.dumps(example_twitchmetrics_viewership_resp),
                  status=200,
                  content_type='application/json')
    responses.add(responses.GET,
                  f'{BASE_HELIX_URL}/clips?'
                  f'broadcaster_id={example_users_list[0]["_id"]}'
                  f'&started_at={started_at}',
                  body=json.dumps(example_clips_resp),
                  status=200,
                  content_type='application/json')

    getter = ClipGetter(example_users_list, started_at=started_at)
    clips = getter._get_good_clips(example_users_list[0]["_id"],
                                   example_users_list[0]["name"],
                                   oauth_token=example_app_access_token)
    assert len(clips) == 1
    assert clips[0]['id'] == 'RandomClip1'


@responses.activate
def test__get_good_clips_valid_ended_at_ret_clips():
    ended_at = '2019-08-18T00:00:00Z'
    responses.add(responses.GET,
                  f'{BASE_TWITCHMETRICS_URL}/c/{example_users_list[0]["_id"]}-'
                  f'{example_users_list[0]["name"]}/recent_viewership_values',
                  body=json.dumps(example_twitchmetrics_viewership_resp),
                  status=200,
                  content_type='application/json')
    responses.add(responses.GET,
                  f'{BASE_HELIX_URL}/clips?'
                  f'broadcaster_id={example_users_list[0]["_id"]}'
                  f'&ended_at={ended_at}',
                  body=json.dumps(example_clips_resp),
                  status=200,
                  content_type='application/json')

    getter = ClipGetter(example_users_list, ended_at=ended_at)
    clips = getter._get_good_clips(example_users_list[0]["_id"],
                                   example_users_list[0]["name"],
                                   oauth_token=example_app_access_token)
    assert len(clips) == 1
    assert clips[0]['id'] == 'RandomClip1'


@responses.activate
def test__get_good_clips_valid_started_and_ended_at_ret_clips():
    started_at = '2019-08-19T00:00:00Z'
    ended_at = '2019-08-21T00:00:00Z'
    responses.add(responses.GET,
                  f'{BASE_TWITCHMETRICS_URL}/c/{example_users_list[0]["_id"]}-'
                  f'{example_users_list[0]["name"]}/recent_viewership_values',
                  body=json.dumps(example_twitchmetrics_viewership_resp),
                  status=200,
                  content_type='application/json')
    responses.add(responses.GET,
                  f'{BASE_HELIX_URL}/clips?'
                  f'broadcaster_id={example_users_list[0]["_id"]}'
                  f'&started_at={started_at}'
                  f'&ended_at={ended_at}',
                  body=json.dumps(example_clips_resp),
                  status=200,
                  content_type='application/json')

    getter = ClipGetter(example_users_list, started_at=started_at,
                        ended_at=ended_at)
    clips = getter._get_good_clips(example_users_list[0]["_id"],
                                   example_users_list[0]["name"],
                                   oauth_token=example_app_access_token)
    assert len(clips) == 1
    assert clips[0]['id'] == 'RandomClip1'


@responses.activate
def test__get_good_clips_invalid_started_at_throw_exception():
    started_at = 'a'
    responses.add(responses.GET,
                  f'{BASE_TWITCHMETRICS_URL}/c/{example_users_list[0]["_id"]}-'
                  f'{example_users_list[0]["name"]}/recent_viewership_values',
                  body=json.dumps(example_twitchmetrics_viewership_resp),
                  status=200,
                  content_type='application/json')
    responses.add(responses.GET,
                  f'{BASE_HELIX_URL}/clips?'
                  f'broadcaster_id={example_users_list[0]["_id"]}'
                  f'&started_at={started_at}',
                  body=json.dumps(
                      example_clips_resp_invalid_started_or_ended_at
                  ),
                  status=400,
                  content_type='application/json')

    getter = ClipGetter(example_users_list, started_at=started_at)
    with pytest.raises(requests.HTTPError):
        getter._get_good_clips(example_users_list[0]["_id"],
                               example_users_list[0]["name"],
                               oauth_token=example_app_access_token)


@responses.activate
def test__get_good_clips_invalid_ended_at_throw_exception():
    ended_at = 'a'
    responses.add(responses.GET,
                  f'{BASE_TWITCHMETRICS_URL}/c/{example_users_list[0]["_id"]}-'
                  f'{example_users_list[0]["name"]}/recent_viewership_values',
                  body=json.dumps(example_twitchmetrics_viewership_resp),
                  status=200,
                  content_type='application/json')
    responses.add(responses.GET,
                  f'{BASE_HELIX_URL}/clips?'
                  f'broadcaster_id={example_users_list[0]["_id"]}'
                  f'&ended_at={ended_at}',
                  body=json.dumps(
                      example_clips_resp_invalid_started_or_ended_at
                  ),
                  status=400,
                  content_type='application/json')

    getter = ClipGetter(example_users_list, ended_at=ended_at)
    with pytest.raises(requests.HTTPError):
        getter._get_good_clips(example_users_list[0]["_id"],
                               example_users_list[0]["name"],
                               oauth_token=example_app_access_token)


@responses.activate
def test_get_clips_all_lang_valid_client_id_ret_clips():
    responses.add(responses.GET,
                  f'{BASE_TWITCHMETRICS_URL}/c/{example_users_list[0]["_id"]}-'
                  f'{example_users_list[0]["name"]}/recent_viewership_values',
                  body=json.dumps(example_twitchmetrics_viewership_resp),
                  status=200,
                  content_type='application/json')
    responses.add(responses.GET,
                  f'{BASE_HELIX_URL}/clips?'
                  f'broadcaster_id={example_users_list[0]["_id"]}',
                  body=json.dumps(example_clips_resp),
                  status=200,
                  content_type='application/json')
    responses.add(responses.GET,
                  f'{BASE_TWITCHMETRICS_URL}/c/{example_users_list[1]["_id"]}-'
                  f'{example_users_list[1]["name"]}/recent_viewership_values',
                  body=json.dumps(example_twitchmetrics_viewership_resp),
                  status=200,
                  content_type='application/json')
    responses.add(responses.GET,
                  f'{BASE_HELIX_URL}/clips?'
                  f'broadcaster_id={example_users_list[1]["_id"]}',
                  body=json.dumps(example_clips_resp2),
                  status=200,
                  content_type='application/json')

    getter = ClipGetter(example_users_list)
    clips = getter.get_clips(client_id=example_client_id)
    assert len(clips) == 2
    assert clips[0]['id'] == 'RandomClip1'
    assert clips[1]['id'] == 'RandomClip3'


@responses.activate
def test_get_clips_all_lang_valid_token_ret_clips():
    responses.add(responses.GET,
                  f'{BASE_TWITCHMETRICS_URL}/c/{example_users_list[0]["_id"]}-'
                  f'{example_users_list[0]["name"]}/recent_viewership_values',
                  body=json.dumps(example_twitchmetrics_viewership_resp),
                  status=200,
                  content_type='application/json')
    responses.add(responses.GET,
                  f'{BASE_HELIX_URL}/clips?'
                  f'broadcaster_id={example_users_list[0]["_id"]}',
                  body=json.dumps(example_clips_resp),
                  status=200,
                  content_type='application/json')
    responses.add(responses.GET,
                  f'{BASE_TWITCHMETRICS_URL}/c/{example_users_list[1]["_id"]}-'
                  f'{example_users_list[1]["name"]}/recent_viewership_values',
                  body=json.dumps(example_twitchmetrics_viewership_resp),
                  status=200,
                  content_type='application/json')
    responses.add(responses.GET,
                  f'{BASE_HELIX_URL}/clips?'
                  f'broadcaster_id={example_users_list[1]["_id"]}',
                  body=json.dumps(example_clips_resp2),
                  status=200,
                  content_type='application/json')

    getter = ClipGetter(example_users_list)
    clips = getter.get_clips(oauth_token=example_app_access_token)
    assert len(clips) == 2
    assert clips[0]['id'] == 'RandomClip1'
    assert clips[1]['id'] == 'RandomClip3'


@responses.activate
def test_get_clips_invalid_client_id_and_token_throws_exception():
    responses.add(responses.GET,
                  f'{BASE_TWITCHMETRICS_URL}/c/{example_users_list[0]["_id"]}-'
                  f'{example_users_list[0]["name"]}/recent_viewership_values',
                  body=json.dumps(example_twitchmetrics_viewership_resp),
                  status=200,
                  content_type='application/json')
    responses.add(responses.GET,
                  f'{BASE_HELIX_URL}/clips?'
                  f'broadcaster_id={example_users_list[0]["_id"]}',
                  body=json.dumps(
                      example_clips_resp_invalid_client_id_and_token
                  ),
                  status=401,
                  content_type='application/json')

    getter = ClipGetter(example_users_list)
    with pytest.raises(requests.HTTPError):
        getter.get_clips()


@responses.activate
def test_get_clips_lang_en_ret_less_clips():
    responses.add(responses.GET,
                  f'{BASE_TWITCHMETRICS_URL}/c/{example_users_list[0]["_id"]}-'
                  f'{example_users_list[0]["name"]}/recent_viewership_values',
                  body=json.dumps(example_twitchmetrics_viewership_resp),
                  status=200,
                  content_type='application/json')
    responses.add(responses.GET,
                  f'{BASE_HELIX_URL}/clips?'
                  f'broadcaster_id={example_users_list[0]["_id"]}',
                  body=json.dumps(example_clips_resp),
                  status=200,
                  content_type='application/json')

    getter = ClipGetter(example_users_list, lang='en')
    clips = getter.get_clips(oauth_token=example_app_access_token)
    assert len(clips) == 1
    assert clips[0]['id'] == 'RandomClip1'
