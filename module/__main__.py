import time
from datetime import datetime

import requests
import telebot

from module import parser, enums, config
from module.enums import DeparturePath
from module.exceptions import UnacceptableResponse
from module.utils import Departure, DateFormats, filter_trains, MessageFormatter

ME = 265753495

bot = telebot.TeleBot(config.BOT_TOKEN)
logger = config.logger
departures: list[Departure] = [
    Departure(
        date=datetime.strptime('2023-08-10', DateFormats.dep_format.value),
        path=DeparturePath(
            dep_from=enums.CityEnum.kyiv,
            dep_to=enums.CityEnum.lviv
        ),
        acceptable_time=datetime.strptime('18:00', DateFormats.time_format.value)
    )
]


def check_departures():
    for departure in departures:
        trains_response: requests.Response = parser.get_trains(departure)
        if 'error' in trains_response.text:
            logger.error(trains_response.text)
            raise UnacceptableResponse('Response is unacceptable {}'.format(trains_response.text))
        available_trains = filter_trains(departure, trains_response.json().get('data').get('list'))
        for train in available_trains:
            train_wagons_response: requests.Response = parser.get_train_wagons(departure, wagon_num=train['num'])
            if 'error' in train_wagons_response.text:
                logger.error(trains_response.text)
                raise UnacceptableResponse('Response is unacceptable {}'.format(train_wagons_response.text))
            formatted_message = MessageFormatter(
                train=train,
                train_wagons=train_wagons_response.json()['data']['types'],
                departure=departure
            )
            logger.info(formatted_message.message)
            bot.send_message(ME, formatted_message.message)


def inf_main():
    while True:
        try:
            check_departures()
            time.sleep(60 * 30)
        except UnacceptableResponse as err:
            logger.error(err)


if __name__ == '__main__':
    inf_main()
