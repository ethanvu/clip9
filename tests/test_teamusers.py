"""Tests teamusers.py."""

import json

import pytest
import requests
import responses

from clip9.constants import BASE_KRAKEN_URL
from clip9.teamusers import TeamUsers


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

example_team_pass_resp = {
    '_id': 10,
    'background': None,
    'banner': 'https://static-cdn.jtvnw.net/jtv_user_pictures/team-staff-banner_image-606ff5977f7dc36e-640x125.png',
    'created_at': '2011-10-25T23:55:47Z',
    'display_name': 'Twitch staff stream here. Drop in and sah \"hi\" some time :)',
    'logo': 'https://static-cdn.jtvnw.net/jtv_user_pictures/team-staff-tea,_logo_image-76418c0c93a9d48b-300x300.png',
    'name': 'staff',
    'updated_at': '2014-10-16T00:44:11Z',
    'users': example_users_list
}

example_team_fail_resp_invalid_team = {
    'error': 'Not Found',
    'status': 404,
    'message': 'Team does not exist'
}

example_team_fail_resp_invalid_client_id = {
    'error': 'Bad Request',
    'status': 400,
    'message': 'Invalid client id specified'
}

example_team_fail_resp_missing_client_id = {
    'error': 'Bad Request',
    'status': 400,
    'message': 'No client id specified'
}

example_team_fail_resp_invalid_client_id_and_token = {
    'status': 404,
    'message': 'client does not exist'
}


@responses.activate
def test_get_valid_team_and_client_id_gets_users():
    team_name = 'staff'
    responses.add(responses.GET,
                  f'{BASE_KRAKEN_URL}teams/{team_name}',
                  body=json.dumps(example_team_pass_resp),
                  status=200,
                  content_type='application/json')

    team_users = TeamUsers()
    team_users.get(team_name, client_id=example_client_id)
    users_list = team_users.users_list
    assert example_users_list == users_list


@responses.activate
def test_get_valid_team_and_oauth_token_gets_users():
    team_name = 'staff'
    responses.add(responses.GET,
                  f'{BASE_KRAKEN_URL}teams/{team_name}',
                  body=json.dumps(example_team_pass_resp),
                  status=200,
                  content_type='application/json')

    team_users = TeamUsers()
    team_users.get(team_name, oauth_token=example_app_access_token)
    users_list = team_users.users_list
    assert example_users_list == users_list


@responses.activate
def test_get_valid_team_client_id_and_oauth_token_gets_users():
    team_name = 'staff'
    responses.add(responses.GET,
                  f'{BASE_KRAKEN_URL}teams/{team_name}',
                  body=json.dumps(example_team_pass_resp),
                  status=200,
                  content_type='application/json')

    team_users = TeamUsers()
    team_users.get(team_name,
                   client_id=example_client_id,
                   oauth_token=example_app_access_token)
    users_list = team_users.users_list
    assert example_users_list == users_list


@responses.activate
def test_get_invalid_team_throws_exception():
    team_name = 'aaaaaa'
    responses.add(responses.GET,
                  f'{BASE_KRAKEN_URL}teams/{team_name}',
                  body=json.dumps(example_team_fail_resp_invalid_team),
                  status=404,
                  content_type='application/json')

    team_users = TeamUsers()
    with pytest.raises(requests.HTTPError):
        team_users.get(team_name, client_id=example_client_id)


def test_get_missing_team_throws_exception():
    team_name = None
    team_users = TeamUsers()
    with pytest.raises(TypeError):
        team_users.get(team_name, client_id=example_client_id)


@responses.activate
def test_get_invalid_client_id_throws_exception():
    team_name = 'staff'
    responses.add(responses.GET,
                  f'{BASE_KRAKEN_URL}teams/{team_name}',
                  body=json.dumps(example_team_fail_resp_invalid_client_id),
                  status=400,
                  content_type='application/json')

    team_users = TeamUsers()
    with pytest.raises(requests.HTTPError):
        team_users.get(team_name, client_id=example_client_id)


@responses.activate
def test_get_invalid_client_id_valid_token_throws_exception():
    team_name = 'staff'
    responses.add(responses.GET,
                  f'{BASE_KRAKEN_URL}teams/{team_name}',
                  body=json.dumps(example_team_pass_resp),
                  status=200,
                  content_type='application/json')

    team_users = TeamUsers()
    team_users.get(team_name,
                   client_id='a',
                   oauth_token=example_app_access_token)
    users_list = team_users.users_list
    assert example_users_list == users_list


@responses.activate
def test_get_valid_client_id_invalid_token_gets_users():
    team_name = 'staff'
    responses.add(responses.GET,
                  f'{BASE_KRAKEN_URL}teams/{team_name}',
                  body=json.dumps(example_team_pass_resp),
                  status=200,
                  content_type='application/json')

    team_users = TeamUsers()
    team_users.get(team_name,
                   client_id=example_client_id,
                   oauth_token='a')
    users_list = team_users.users_list
    assert example_users_list == users_list


@responses.activate
def test_get_invalid_token_throws_exception():
    team_name = 'staff'
    responses.add(responses.GET,
                  f'{BASE_KRAKEN_URL}teams/{team_name}',
                  body=json.dumps(example_team_fail_resp_missing_client_id),
                  status=400,
                  content_type='application/json')

    team_users = TeamUsers()
    with pytest.raises(requests.HTTPError):
        team_users.get(team_name, client_id=example_client_id)


@responses.activate
def test_get_invalid_client_id_and_token_throws_exception():
    team_name = 'staff'
    responses.add(responses.GET,
                  f'{BASE_KRAKEN_URL}teams/{team_name}',
                  body=json.dumps(example_team_fail_resp_invalid_client_id),
                  status=400,
                  content_type='application/json')

    team_users = TeamUsers()
    with pytest.raises(requests.HTTPError):
        team_users.get(team_name)


@responses.activate
def test_get_missing_client_id_and_token_throws_exception():
    team_name = 'staff'
    responses.add(responses.GET,
                  f'{BASE_KRAKEN_URL}teams/{team_name}',
                  body=json.dumps(example_team_fail_resp_missing_client_id),
                  status=400,
                  content_type='application/json')

    team_users = TeamUsers()
    with pytest.raises(requests.HTTPError):
        team_users.get(team_name)
