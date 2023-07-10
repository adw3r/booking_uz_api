import datetime
import time
from pathlib import Path

import requests
import telebot

from module import parser, enums, config

ME = 265753495

ACCEPTABLE_TIME = '00:00'

TIME_FORMAT = '%H:%M'
ACCEPTABLE_TIME = datetime.datetime.strptime(ACCEPTABLE_TIME, TIME_FORMAT)
bot = telebot.TeleBot(config.BOT_TOKEN)
logger = config.logger
WAGON_RES = Path(config.ROOT_FOLDER, 'wagon_res.json')


def check_acceptable_trains(parse_results: dict, dep_date: str, dep_from: enums.CityEnum,
                            dep_to: enums.CityEnum):  # todo
    results = []
    acceptable = False

    for result in parse_results:
        get_from_date__get = result.get('from_date').get('time')
        time_res = datetime.datetime.strptime(get_from_date__get, TIME_FORMAT)
        for place in result['places']:
            if place.get('title') == enums.WagonEnum.platskart.value or time_res >= ACCEPTABLE_TIME:
                acceptable = True
        if acceptable:
            results.append(result)
            acceptable = False
    if results:
        for res in results:
            types = parser.get_train_wagons(
                wagon_num=res['num'], from_value=dep_from, to_value=dep_to, departure_date=dep_date) \
                .json() \
                .get('data')
            res['types'] = types

    return results


def _create_wagon_link(train_num: str, dep_date, dep_from: enums.CityEnum, dep_to: enums.CityEnum):
    link = f'https://booking.uz.gov.ua/?' \
           f'from={dep_from.value}&' \
           f'to={dep_to.value}&' \
           f'date={dep_date}&' \
           f'train={train_num}&' \
           f'url=train-wagons'
    return link


def check_departures():
    departures = [
        {
            'date': '2023-07-13',
            'path': {'dep_from': enums.CityEnum.kyiv, 'dep_to': enums.CityEnum.lviv},
            'acceptable_time': datetime.datetime.strptime('20:00', TIME_FORMAT)
        },
    ]
    for departure in departures:
        dep_date = departure['date']
        dep_from: enums.CityEnum = departure["path"]['dep_from']
        dep_to: enums.CityEnum = departure["path"]['dep_to']

        get_trains_response: requests.Response = parser.get_trains(
            from_value=dep_from, to_value=dep_to, departure_date=dep_date
        )
        if 'error' in get_trains_response.text:
            logger.error(get_trains_response.text)
            return
        trains_list: list[dict] = get_trains_response.json().get('data').get('list')
        for train in trains_list:
            if not train.get('types'):
                continue
            train_time_from = train.get('from')
            train_time_to = train.get('to')
            train_from_time = datetime.datetime.strptime(train_time_from.get('time'), TIME_FORMAT)
            if train_from_time >= departure['acceptable_time']:
                train_url = _create_wagon_link(train["num"], dep_date=dep_date, dep_from=dep_from, dep_to=dep_to)
                get_train_wagons_response: requests.Response = parser.get_train_wagons(wagon_num=train['num'], from_value=dep_from, to_value=dep_to, departure_date=dep_date)
                cost = ', '.join([str(type_['cost'])[:-2] for type_ in get_train_wagons_response.json()['data']['types']])
                available = ', '.join([str(type_['free']) for type_ in get_train_wagons_response.json()['data']['types']])
                title = ', '.join([str(type_['title']) for type_ in get_train_wagons_response.json()['data']['types']])
                tg_bot_message = f'dep_time: {train_time_from["date"]} {str(train_from_time.time())}\n' \
                                 f'arrive_at: {train_time_to["date"]} {str(train_time_to["time"])}\n' \
                                 f'url: {train_url}\n' \
                                 f'cost: {cost}\n' \
                                 f'available seets: {available}\n' \
                                 f'title: {title}'
                logger.info(tg_bot_message)
                bot.send_message(ME, tg_bot_message)
            else:
                bot.send_message(ME, 'No available departures was found on {}'.format(departure))


if __name__ == '__main__':
    while True:
        check_departures()
        time.sleep(60 * 30)
