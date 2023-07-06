import os
import sys
from pathlib import Path

import loguru
from dotenv import load_dotenv

load_dotenv()

ROOT_FOLDER = Path(__file__).absolute().parent.parent

CAPMONSTER_HOST = os.environ.get('CAPMONSTER_HOST')
CAPMONSTER_KEY = os.environ.get('CAPMONSTER_KEY')
BOT_TOKEN = os.environ.get('BOT_TOKEN')

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
