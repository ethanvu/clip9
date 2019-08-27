"""Tests clipget.py"""

import json

import pytest
import requests
import responses

from clip9.constants import BASE_HELIX_URL
from clip9.constants import BASE_TWITCHMETRICS_URL
from clip9.clipget import ClipGetter


example_users_list = [{
    '_id': 5582097,
    'broadcaster_language': 'en',
    'created_at': '2009-04-13T21:22:28Z',
    'display_name': 'Sarbandia',
    'followers': 1182,
    'game': 'Hearthstone: Heroes of Warcraft',
    'language': 'en',
    'logo': 'https://static-cdn.jtvnw.net/jtv_user_pictures/sarbandia-profile_image-6693b5952f31c847-300x300.jpeg',
    'mature': False,
    'name': 'sarbandia',
    'partner': False,
    'profile_banner': 'https://static-cdn.jtvnw.net/jtv_user_pictures/sarbandia-profile_banner-247cdbe62dbcf4d9-480.jpeg',
    'profile_banner_background_color': None,
    'status': 'Midrange shaman laddering',
    'updated_at': '2016-12-15T19:02:40Z',
    'url': 'https://www.twitch.tv/sarbandia',
    'video_banner': None,
    'views': 8168
}]

example_twitchmetrics_viewership_resp = [
    ['2019-08-19T00:20:01.000Z', 643, 'Counter-Strike: Global Offensive'],
    ['2019-08-19T00:30:01.000Z', 694, 'Counter-Strike: Global Offensive'],
    ['2019-08-19T00:40:01.000Z', 742, 'Counter-Strike: Global Offensive']
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
            'view_count': 10,
            'created_at': '2017-11-30T22:34:18Z',
            'thumbnail_url': 'https://clips-media-assets.twitch.tv/157589949-preview-480x272.jpg'
        },
    ],
    'pagination': {
        'cursor': 'eyJiIjpudWxsLCJhIjoiIn0'
    }
}


@responses.activate
def test__get_avg_viewers_in_past_week_user_exists_ret_avg():
    responses.add(responses.GET,
                  f'{BASE_TWITCHMETRICS_URL}c/{example_users_list[0]["_id"]}-'
                  f'{example_users_list[0]["name"]}/recent_viewership_values',
                  body=json.dumps(example_twitchmetrics_viewership_resp),
                  status=200,
                  content_type='application/json')
    avg = ClipGetter._get_avg_viewers_in_past_week(
        example_users_list[0]['_id'],
        example_users_list[0]['name']
    )
    assert 693 == avg


@responses.activate
def test__get_avg_viewers_in_past_week_user_doesnt_exist_ret_0():
    responses.add(responses.GET,
                  f'{BASE_TWITCHMETRICS_URL}c/{example_users_list[0]["_id"]}-'
                  f'{example_users_list[0]["name"]}/recent_viewership_values',
                  body=example_twitchmetrics_viewership_resp_doesnt_exist,
                  status=404,
                  content_type='text/html')
    avg = ClipGetter._get_avg_viewers_in_past_week(
        example_users_list[0]['_id'],
        example_users_list[0]['name']
    )
    assert 0 == avg


@responses.activate
def test__get_avg_viewers_in_past_week_user_didnt_stream_ret_0():
    responses.add(responses.GET,
                  f'{BASE_TWITCHMETRICS_URL}c/{example_users_list[0]["_id"]}-'
                  f'{example_users_list[0]["name"]}/recent_viewership_values',
                  body=json.dumps(example_twitchmetrics_viewership_resp_empty),
                  status=200,
                  content_type='application/json')
    avg = ClipGetter._get_avg_viewers_in_past_week(
        example_users_list[0]['_id'],
        example_users_list[0]['name']
    )
    assert 0 == avg



def test__get_clip_rating_low_clip_views_high_avg_ret_gt_1():
    rating = ClipGetter._get_clip_rating(250, 1000)
    assert 1 < rating


def test__get_clip_rating_low_clip_views_high_avg_ret_lt_1():
    rating = ClipGetter._get_clip_rating(150, 1000)
    assert 1 > rating


@responses.activate
def test__get_good_clips_ret_all_clips():
    responses.add(responses.GET,
                  f'{BASE_TWITCHMETRICS_URL}c/{example_users_list[0]["_id"]}-'
                  f'{example_users_list[0]["name"]}/recent_viewership_values',
                  body=json.dumps(example_twitchmetrics_viewership_resp_empty),
                  status=200,
                  content_type='application/json')
    responses.add(responses.GET,
                  f'{BASE_HELIX_URL}clips?'
                  f'broadcaster_id={example_users_list[0]["_id"]}',
                  body=json.dumps(example_clips_resp),
                  status=200,
                  content_type='application/json')
    #clips = ClipGetter._get_good_clips
    pass


def temp():
    getter = ClipGetter(example_users_list, 'staff', '2019-08-19T00:00:00Z',
                        '2019-08-20T00:00:00Z')
