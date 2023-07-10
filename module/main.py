import time
from datetime import datetime
from pathlib import Path

import requests
import telebot

from module import parser, enums, config

ME = 265753495

ACCEPTABLE_TIME = '00:00'

TIME_FORMAT = '%H:%M'
ACCEPTABLE_TIME = datetime.strptime(ACCEPTABLE_TIME, TIME_FORMAT)
bot = telebot.TeleBot(config.BOT_TOKEN)
logger = config.logger
WAGON_RES = Path(config.ROOT_FOLDER, 'wagon_res.json')



class UnacceptableResponse(Exception):
    ...


def check_departures():
    departures = [
        {
            'date': '2023-07-13',
            'path': {'dep_from': enums.CityEnum.kyiv, 'dep_to': enums.CityEnum.lviv},
            'acceptable_time': datetime.strptime('20:00', TIME_FORMAT)
        },
    ]
    for departure in departures:
        trains_response: requests.Response = parser.get_trains(
            dep_from=departure["path"]['dep_from'],
            dep_to=departure["path"]['dep_to'],
            departure_date=departure['date']
        )
        if 'error' in trains_response.text:
            logger.error(trains_response.text)
            raise UnacceptableResponse('Response is unacceptable {}'.format(trains_response.text))
        available_trains = filter_trains(departure, trains_response.json().get('data').get('list'))
        for train in available_trains:
            train_wagons_response: requests.Response = parser.get_train_wagons(
                wagon_num=train['num'],
                dep_from=departure["path"]['dep_from'],
                dep_to=departure["path"]['dep_to'],
                departure_date=departure['date']
            )
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


def filter_trains(departure: dict, trains: list[dict]):
    return [
        train
        for train in trains
        if datetime.strptime(train.get('from').get('time'), TIME_FORMAT) >= departure['acceptable_time'] and
           train.get('types')
    ]


class MessageFormatter:
    message: str

    def __init__(self, train: dict, train_wagons: dict, departure: dict):
        train_url = self.create_wagon_link(train["num"], dep_date=departure['date'],
                                           dep_from=departure["path"]['dep_from'],
                                           dep_to=departure["path"]['dep_to'])
        cost = self.__create_string(train_wagons, 'cost')
        available = self.__create_string(train_wagons, 'free')
        title = self.__create_string(train_wagons, 'title')
        tg_bot_message = f'dep_time: {train.get("from")["date"]} {train.get("from").get("time")}\n' \
                         f'arrive_at: {train.get("to")["date"]} {str(train.get("to")["time"])}\n' \
                         f'url: {train_url}\n' \
                         f'cost: {cost}\n' \
                         f'available seets: {available}\n' \
                         f'title: {title}'
        self.message = tg_bot_message

    @staticmethod
    def create_wagon_link(train_num: str, dep_date, dep_from: enums.CityEnum, dep_to: enums.CityEnum):
        link = f'https://booking.uz.gov.ua/?' \
               f'from={dep_from.value}&' \
               f'to={dep_to.value}&' \
               f'date={dep_date}&' \
               f'train={train_num}&' \
               f'url=train-wagons'
        return link

    @staticmethod
    def __create_string(train_wagons, key: str):
        return ', '.join([str(wagon[key]) for wagon in train_wagons])


if __name__ == '__main__':
    while True:
        try:
            check_departures()
            time.sleep(60 * 30)
        except UnacceptableResponse as err:
            logger.error(err)
