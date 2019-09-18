"""Tests the clip9 module."""

from configparser import ConfigParser
import os
import sys

import pytest

from clip9 import clip9


def test__parse_args_team_output_file_no_start_time_success():
    sys.argv = ['clip9.py', 'result.mp4', 'cloud9']
    args = clip9._parse_args()
    assert args.output_file == 'result.mp4'
    assert args.team == 'cloud9'
    assert args.started_at == None
    assert args.ended_at == None
    assert args.clips_dir == './'
    assert args.lang == None
    assert args.log_file == None


def test__parse_args_no_team_exit():
    sys.argv = ['clip9.py', 'result.mp4'] 
    with pytest.raises(SystemExit):
        args = clip9._parse_args()


def test__parse_args_extra_arg_exit():
    sys.argv = ['clip9.py', 'result.mp4', 'cloud9', 'a'] 
    with pytest.raises(SystemExit):
        args = clip9._parse_args()


def test__parse_args_started_at_success():
    sys.argv = ['clip9.py', 'result.mp4', 'cloud9', '--started_at',
                '2008-09-08T22:47:31Z']
    args = clip9._parse_args()
    assert args.output_file == 'result.mp4'
    assert args.team == 'cloud9'
    assert args.started_at == '2008-09-08T22:47:31Z'
    assert args.ended_at == None
    assert args.clips_dir == './'
    assert args.lang == None
    assert args.log_file == None


def test__parse_args_started_at_short_success():
    sys.argv = ['clip9.py', 'result.mp4', 'cloud9', '-s',
                '2008-09-08T22:47:31Z']
    args = clip9._parse_args()
    assert args.output_file == 'result.mp4'
    assert args.team == 'cloud9'
    assert args.started_at == '2008-09-08T22:47:31Z'
    assert args.ended_at == None
    assert args.clips_dir == './'
    assert args.lang == None
    assert args.log_file == None


def test__parse_args_ended_at_success():
    sys.argv = ['clip9.py', 'result.mp4', 'cloud9', '--ended_at',
                '2008-09-08T22:47:31Z']
    args = clip9._parse_args()
    assert args.output_file == 'result.mp4'
    assert args.team == 'cloud9'
    assert args.started_at == None
    assert args.ended_at == '2008-09-08T22:47:31Z'
    assert args.clips_dir == './'
    assert args.lang == None
    assert args.log_file == None


def test__parse_args_ended_at_short_success():
    sys.argv = ['clip9.py', 'result.mp4', 'cloud9', '-e',
                '2008-09-08T22:47:31Z']
    args = clip9._parse_args()
    assert args.output_file == 'result.mp4'
    assert args.team == 'cloud9'
    assert args.started_at == None
    assert args.ended_at == '2008-09-08T22:47:31Z'
    assert args.clips_dir == './'
    assert args.lang == None
    assert args.log_file == None


def test__parse_args_clip_dir_success():
    sys.argv = ['clip9.py', 'result.mp4', 'cloud9', '--clips_dir', './clips']
    args = clip9._parse_args()
    assert args.output_file == 'result.mp4'
    assert args.team == 'cloud9'
    assert args.started_at == None
    assert args.ended_at == None
    assert args.clips_dir == './clips'
    assert args.lang == None
    assert args.log_file == None


def test__parse_args_clip_dir_short_success():
    sys.argv = ['clip9.py', 'result.mp4', 'cloud9', '-c', './clips']
    args = clip9._parse_args()
    assert args.output_file == 'result.mp4'
    assert args.team == 'cloud9'
    assert args.started_at == None
    assert args.ended_at == None
    assert args.clips_dir == './clips'
    assert args.lang == None
    assert args.log_file == None


def test__parse_args_lang_success():
    sys.argv = ['clip9.py', 'result.mp4', 'cloud9', '--lang', 'en']
    args = clip9._parse_args()
    assert args.output_file == 'result.mp4'
    assert args.team == 'cloud9'
    assert args.started_at == None
    assert args.ended_at == None
    assert args.clips_dir == './'
    assert args.lang == 'en'
    assert args.log_file == None


def test__parse_args_lang_short_success():
    sys.argv = ['clip9.py', 'result.mp4', 'cloud9', '-l', 'en']
    args = clip9._parse_args()
    assert args.output_file == 'result.mp4'
    assert args.team == 'cloud9'
    assert args.started_at == None
    assert args.ended_at == None
    assert args.clips_dir == './'
    assert args.lang == 'en'
    assert args.log_file == None


def test__parse_args_log_file_success():
    sys.argv = ['clip9.py', 'result.mp4', 'cloud9', '--log_file', 'clip9.log']
    args = clip9._parse_args()
    assert args.output_file == 'result.mp4'
    assert args.team == 'cloud9'
    assert args.started_at == None
    assert args.ended_at == None
    assert args.clips_dir == './'
    assert args.lang == None
    assert args.log_file == 'clip9.log'


def test__parse_args_log_file_short_success():
    sys.argv = ['clip9.py', 'result.mp4', 'cloud9', '-L', 'clip9.log']
    args = clip9._parse_args()
    assert args.output_file == 'result.mp4'
    assert args.team == 'cloud9'
    assert args.started_at == None
    assert args.ended_at == None
    assert args.clips_dir == './'
    assert args.lang == None
    assert args.log_file == 'clip9.log'


def test__parse_credentials_cfg_file_exists_ret_creds():
    credentials = clip9._parse_credentials_cfg('credentials_template.cfg')
    assert credentials['TWITCH_CLIENT_ID'] == 'uo6dggojyb8d6soh92zknwmi5ej1q2'
    assert credentials['TWITCH_CLIENT_SECRET'] == 'nyo51xcdrerl8z9m56w9w6wg'


def test__parse_credentials_cfg_file_doesnt_exist_exit():
    with pytest.raises(SystemExit):
        credentials = clip9._parse_credentials_cfg('doesnt_exist.cfg')


def test__parse_credentials_cfg_file_no_creds_header_exit():
    with pytest.raises(SystemExit):
        credentials = clip9._parse_credentials_cfg('tests/resources/'
                                                   'no_creds_header.cfg')


def test__parse_credentials_cfg_file_no_id_key_exit():
    with pytest.raises(SystemExit):
        credentials = clip9._parse_credentials_cfg('tests/resources/'
                                                   'no_id_key.cfg')


def test__parse_credentials_cfg_file_no_secret_key_exit():
    with pytest.raises(SystemExit):
        credentials = clip9._parse_credentials_cfg('tests/resources/'
                                                   'no_secret_key.cfg')
