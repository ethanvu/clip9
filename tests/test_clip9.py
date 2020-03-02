"""Tests the clip9 module."""

from configparser import ConfigParser
import sys

import pytest

import clip9

def test__parse_args_team_output_file_no_start_time_success():
    sys.argv = ['clip9.py', 'result.mp4', 'cloud9']
    args = clip9._parse_args()
    assert args.output_file == 'result.mp4'
    assert args.team == 'cloud9'
    assert args.started_at is None
    assert args.ended_at is None
    assert args.clips_dir == './'
    assert args.lang is None
    assert args.log_file is None
    assert args.debug is False

def test__parse_args_no_team_exit():
    sys.argv = ['clip9.py', 'result.mp4']
    with pytest.raises(SystemExit):
        clip9._parse_args()

def test__parse_args_extra_arg_exit():
    sys.argv = ['clip9.py', 'result.mp4', 'cloud9', 'a']
    with pytest.raises(SystemExit):
        clip9._parse_args()

def test__parse_args_started_at_success():
    sys.argv = ['clip9.py', 'result.mp4', 'cloud9', '--started_at',
                '2008-09-08T22:47:31Z']
    args = clip9._parse_args()
    assert args.output_file == 'result.mp4'
    assert args.team == 'cloud9'
    assert args.started_at == '2008-09-08T22:47:31Z'
    assert args.ended_at is None
    assert args.clips_dir == './'
    assert args.lang is None
    assert args.log_file is None

def test__parse_args_started_at_short_success():
    sys.argv = ['clip9.py', 'result.mp4', 'cloud9', '-s',
                '2008-09-08T22:47:31Z']
    args = clip9._parse_args()
    assert args.output_file == 'result.mp4'
    assert args.team == 'cloud9'
    assert args.started_at == '2008-09-08T22:47:31Z'
    assert args.ended_at is None
    assert args.clips_dir == './'
    assert args.lang is None
    assert args.log_file is None
    assert args.debug is False

def test__parse_args_ended_at_success():
    sys.argv = ['clip9.py', 'result.mp4', 'cloud9', '--ended_at',
                '2008-09-08T22:47:31Z']
    args = clip9._parse_args()
    assert args.output_file == 'result.mp4'
    assert args.team == 'cloud9'
    assert args.started_at is None
    assert args.ended_at == '2008-09-08T22:47:31Z'
    assert args.clips_dir == './'
    assert args.lang is None
    assert args.log_file is None
    assert args.debug is False

def test__parse_args_ended_at_short_success():
    sys.argv = ['clip9.py', 'result.mp4', 'cloud9', '-e',
                '2008-09-08T22:47:31Z']
    args = clip9._parse_args()
    assert args.output_file == 'result.mp4'
    assert args.team == 'cloud9'
    assert args.started_at is None
    assert args.ended_at == '2008-09-08T22:47:31Z'
    assert args.clips_dir == './'
    assert args.lang is None
    assert args.log_file is None
    assert args.debug is False

def test__parse_args_clip_dir_success():
    sys.argv = ['clip9.py', 'result.mp4', 'cloud9', '--clips_dir', './clips']
    args = clip9._parse_args()
    assert args.output_file == 'result.mp4'
    assert args.team == 'cloud9'
    assert args.started_at is None
    assert args.ended_at is None
    assert args.clips_dir == './clips'
    assert args.lang is None
    assert args.log_file is None
    assert args.debug is False

def test__parse_args_clip_dir_short_success():
    sys.argv = ['clip9.py', 'result.mp4', 'cloud9', '-c', './clips']
    args = clip9._parse_args()
    assert args.output_file == 'result.mp4'
    assert args.team == 'cloud9'
    assert args.started_at is None
    assert args.ended_at is None
    assert args.clips_dir == './clips'
    assert args.lang is None
    assert args.log_file is None
    assert args.debug is False

def test__parse_args_lang_success():
    sys.argv = ['clip9.py', 'result.mp4', 'cloud9', '--lang', 'en']
    args = clip9._parse_args()
    assert args.output_file == 'result.mp4'
    assert args.team == 'cloud9'
    assert args.started_at is None
    assert args.ended_at is None
    assert args.clips_dir == './'
    assert args.lang == {'en'}
    assert args.log_file is None
    assert args.debug is False

def test__parse_args_lang_short_success():
    sys.argv = ['clip9.py', 'result.mp4', 'cloud9', '-l', 'en']
    args = clip9._parse_args()
    assert args.output_file == 'result.mp4'
    assert args.team == 'cloud9'
    assert args.started_at is None
    assert args.ended_at is None
    assert args.clips_dir == './'
    assert args.lang == {'en'}
    assert args.log_file is None
    assert args.debug is False

def test__parse_args_multi_lang_success():
    sys.argv = ['clip9.py', 'result.mp4', 'cloud9', '-l', 'en', 'ko']
    args = clip9._parse_args()
    assert args.output_file == 'result.mp4'
    assert args.team == 'cloud9'
    assert args.started_at is None
    assert args.ended_at is None
    assert args.clips_dir == './'
    assert args.lang == {'en', 'ko'}
    assert args.log_file is None
    assert args.debug is False

def test__parse_args_log_file_success():
    sys.argv = ['clip9.py', 'result.mp4', 'cloud9', '--log_file', 'clip9.log']
    args = clip9._parse_args()
    assert args.output_file == 'result.mp4'
    assert args.team == 'cloud9'
    assert args.started_at is None
    assert args.ended_at is None
    assert args.clips_dir == './'
    assert args.lang is None
    assert args.log_file == 'clip9.log'
    assert args.debug is False

def test__parse_args_log_file_short_success():
    sys.argv = ['clip9.py', 'result.mp4', 'cloud9', '-L', 'clip9.log']
    args = clip9._parse_args()
    assert args.output_file == 'result.mp4'
    assert args.team == 'cloud9'
    assert args.started_at is None
    assert args.ended_at is None
    assert args.clips_dir == './'
    assert args.lang is None
    assert args.log_file == 'clip9.log'
    assert args.debug is False

def test__parse_args_debug_success():
    sys.argv = ['clip9.py', 'result.mp4', 'cloud9', '--debug']
    args = clip9._parse_args()
    assert args.output_file == 'result.mp4'
    assert args.team == 'cloud9'
    assert args.started_at is None
    assert args.ended_at is None
    assert args.clips_dir == './'
    assert args.lang is None
    assert args.log_file is None
    assert args.debug is True

def test__parse_args_debug_short_success():
    sys.argv = ['clip9.py', 'result.mp4', 'cloud9', '-d']
    args = clip9._parse_args()
    assert args.output_file == 'result.mp4'
    assert args.team == 'cloud9'
    assert args.started_at is None
    assert args.ended_at is None
    assert args.clips_dir == './'
    assert args.lang is None
    assert args.log_file is None
    assert args.debug is True

def test__parse_credentials_cfg_proper_config_ret_creds():
    cfg_string = ('[credentials]\n'
                  'TWITCH_CLIENT_ID=uo6dggojyb8d6soh92zknwmi5ej1q2\n'
                  'TWITCH_CLIENT_SECRET=nyo51xcdrerl8z9m56w9w6wg\n')
    config = ConfigParser()
    config.read_string(cfg_string)
    credentials = clip9._parse_credentials_cfg(config)
    assert credentials['TWITCH_CLIENT_ID'] == 'uo6dggojyb8d6soh92zknwmi5ej1q2'
    assert credentials['TWITCH_CLIENT_SECRET'] == 'nyo51xcdrerl8z9m56w9w6wg'

def test__parse_credentials_cfg_no_creds_header_exit():
    cfg_string = ('[a]\n'
                  'TWITCH_CLIENT_ID=uo6dggojyb8d6soh92zknwmi5ej1q2\n'
                  'TWITCH_CLIENT_SECRET=nyo51xcdrerl8z9m56w9w6wg\n')
    config = ConfigParser()
    config.read_string(cfg_string)
    credentials = clip9._parse_credentials_cfg(config)
    assert credentials is None

def test__parse_credentials_cfg_no_id_key_exit():
    cfg_string = ('[credentials]\n'
                  'TWITCH_CLIENT_SECRET=nyo51xcdrerl8z9m56w9w6wg\n')
    config = ConfigParser()
    config.read_string(cfg_string)
    credentials = clip9._parse_credentials_cfg(config)
    assert credentials is None

def test__parse_credentials_cfg_no_secret_key_exit():
    cfg_string = ('[credentials]\n'
                  'TWITCH_CLIENT_ID=uo6dggojyb8d6soh92zknwmi5ej1q2\n')
    config = ConfigParser()
    config.read_string(cfg_string)
    credentials = clip9._parse_credentials_cfg(config)
    assert credentials is None
