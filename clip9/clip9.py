"""Main script to get 'good' clips from streamers in a Twitch Team,
splices them into a video, and then upload it to YouTube.
"""

from argparse import ArgumentParser
from configparser import ConfigParser
import logging
import os
import sys


def handle_exception(type, value, traceback):
    logging.error(f"Uncaught exception", exc_info=(type, value, traceback))


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
    parser.add_argument('-l', '--log_file',
                        action='store',
                        help="Name of the log file.")
    args = parser.parse_args()
    if (args.clips_dir is None):
        args.clips_dir = './'
    return args


def main():
    args = _parse_args()
    logging.basicConfig(level=logging.DEBUG, filename=args.log_file, 
                        format='[%(asctime)s]%(levelname)s: %(message)s')
    sys.excepthook = handle_exception

    logging.info("-------STARTING CLIP9 MAIN SCRIPT-------")

    cfg_file_name = f'{os.path.dirname(sys.argv[0])}/../credentials.cfg'
    logging.info(f'config file name: {cfg_file_name}')
    logging.info("Loading credentials.cfg")
    config = ConfigParser()
    config.read(cfg_file_name)
    logging.info("credentials.cfg loaded")
    credentials = config['credentials']

    if ('TWITCH_CLIENT_ID' not in credentials):
        logging.error("credentials.cfg does not contain TWITCH_CLIENT_ID")
        exit(1)
    logging.info("Loaded TWITCH_CLIENT_ID")

    if ('TWITCH_CLIENT_SECRET' not in credentials):
        logging.error("credentials.cfg does not contain TWITCH_CLIENT_SECRET")
        exit(1)
    logging.info("Loaded TWITCH_CLIENT_SECRET")

    twitch_client_id = credentials['TWITCH_CLIENT_ID']
    twitch_client_secret = credentials['TWITCH_CLIENT_SECRET']


if __name__ == '__main__':
    main()
