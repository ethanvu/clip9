"""Main script to get 'good' clips from streamers in a Twitch Team,
splices them into a video, and then upload it to YouTube.
"""

from argparse import ArgumentParser
from configparser import ConfigParser
import logging
import os
import sys
import time

from clipget import ClipGetter
from clipsplice import ClipSplicer
from oauthtoken import OauthToken
from teamusers import TeamUsers


def handle_exception(type, value, traceback):
    logging.error(f"Exception", exc_info=(type, value, traceback))


def _parse_args():
    parser = ArgumentParser(description="Gets 'good' clips from a group of "
                            "Twitch users and splices them into a video.")
    parser.add_argument('output_file',
                        action='store',
                        help="File name of the output file.  Supports mp4, "
                             "ogv, webm, and avi formats.")
    parser.add_argument('team',
                        action='store',
                        help="Name of Twitch team of users to get clips from.")
    parser.add_argument('-s', '--started_at',
                        action='store',
                        help="Start time of timeframe to get clips from.  "
                        "Default is the beginning of time. Only takes RFC "
                        "3339 format, e.g. 2019-08-19T00:00:00Z.")
    parser.add_argument('-e', '--ended_at',
                        action='store',
                        help="End time of timeframe to get clips from.  "
                        "If start_time is specified, the default end_time is "
                        "one week after that.  If start_time isn't specified, "
                        "end_time is ignored.  Only takes RFC 3339 format, "
                        "e.g. 2019-08-19T00:00:00Z.")
    parser.add_argument('-c', '--clips_dir',
                        action='store',
                        help="Directory to download the clips into.")
    parser.add_argument('-l', '--lang',
                        action='store',
                        help="Language of clips to get.")
    parser.add_argument('-L', '--log_file',
                        action='store',
                        help="Name of the log file.")
    args = parser.parse_args()
    if (args.clips_dir is None):
        args.clips_dir = './'
    return args


def _parse_credentials_cfg(cfg_file_name):
    logging.info(f'Loading {cfg_file_name}')
    if (not os.path.isfile(cfg_file_name)):
        logging.error(f"{cfg_file_name} doesn't exist")
        exit(1)

    config = ConfigParser()
    config.read(cfg_file_name)
    logging.info(f'Loaded {cfg_file_name}')
    credentials = config['credentials']

    if ('TWITCH_CLIENT_ID' not in credentials):
        logging.error("credentials.cfg does not contain TWITCH_CLIENT_ID")
        exit(1)
    logging.info("Loaded TWITCH_CLIENT_ID")

    if ('TWITCH_CLIENT_SECRET' not in credentials):
        logging.error("credentials.cfg does not contain TWITCH_CLIENT_SECRET")
        exit(1)
    logging.info("Loaded TWITCH_CLIENT_SECRET")

    return credentials


def main():
    start_time = time.time()
    args = _parse_args()
    logging.basicConfig(level=logging.INFO, filename=args.log_file, 
                        format='[%(asctime)s]%(levelname)s: %(message)s')
    sys.excepthook = handle_exception

    logging.info("-------STARTING CLIP9 MAIN SCRIPT-------")

    cfg_file_name = f'{os.path.dirname(sys.argv[0])}/../credentials.cfg'
    credentials = _parse_credentials_cfg(cfg_file_name)
    client_id = credentials['TWITCH_CLIENT_ID']
    client_secret = credentials['TWITCH_CLIENT_SECRET']

    token = OauthToken(client_id, client_secret)
    if (not token.validate()):
        logging.error("Token isn't valid")
        exit(1)
    try:
        team_users = TeamUsers()
        team_users.get(args.team, client_id=client_id, oauth_token=token.token)
        users_list = team_users.users_list
        getter = ClipGetter(users_list, started_at=args.started_at,
                            ended_at=args.ended_at, lang=args.lang)
        clips_list = getter.get_clips(client_id, token.token)
        splicer = ClipSplicer(clips_list)
        splicer.splice(args.output_file, args.clips_dir)
        logging.info("Successfully generated a video of good clips")
    except Exception as e:
        logging.error("There was an exception during execution")
        raise e
    finally:
        token.revoke()
        elapsed_time = time.time() - start_time
        logging.info(f"Execution time: {elapsed_time} seconds")


if __name__ == '__main__':
    main()
