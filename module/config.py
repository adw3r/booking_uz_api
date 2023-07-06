import configparser
import os
import sys
from pathlib import Path

import loguru
from dotenv import load_dotenv

config = configparser.ConfigParser()
load_dotenv()

ROOT_FOLDER = Path(__file__).absolute().parent.parent
CONFIG_FILE = Path(ROOT_FOLDER, 'config.ini')
config.read_file(CONFIG_FILE.open())
URL = os.environ['URL']

LOGGING_LEVEL = config['general'].getint('LOGGING_LEVEL')

CAPMONSTER_HOST = os.environ.get('CAPMONSTER_HOST')
CAPMONSTER_KEY = os.environ.get('CAPMONSTER_KEY')
BOT_TOKEN = os.environ.get('BOT_TOKEN')
PROXIES_API_HOST = config['general']['PROXIES_API_HOST']


logger = loguru.logger

logger_config = {
    "handlers": [
        {
            "sink": sys.stdout, 'level': 'INFO'
        },
        {
            "sink": Path(ROOT_FOLDER, 'logs', "logs.log"),
            'level': 'DEBUG',
            'rotation': '10 mb',
        },
    ],
}
logger.configure(**logger_config)
