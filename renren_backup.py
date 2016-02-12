import ConfigParser

from modules.albums import *


def get_config():
    config_parser = ConfigParser.RawConfigParser()
    config_parser.read('config.ini.local')
    return config_parser


if __name__ == '__main__':
    config = get_config()
    need_backup_albums = config.get('type', 'album')
    if need_backup_albums == 'yes':
        backup_albums(config)
