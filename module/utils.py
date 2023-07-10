import abc
import json
from datetime import datetime
from pathlib import Path

import requests

from module import enums
from module.config import logger
from module.enums import Departure, DateFormats


class ResponseFormatterInterface(abc.ABC):

    @staticmethod
    @abc.abstractmethod
    def format(response: requests.Response) -> dict | list[dict]:
        ...


def filter_trains(departure: Departure, trains: list[dict]):
    return [
        train
        for train in trains
        if
        datetime.strptime(train.get('from').get('time'), DateFormats.time_format.value) >= departure.acceptable_time and
        train.get('types')
    ]


class MyFormatter(ResponseFormatterInterface):

    @staticmethod
    def format(response: requests.Response) -> dict | list[dict]:
        formatted_results = []
        try:
            list_of_results = response.json().get('data').get('list')
        except AttributeError as error:
            logger.error(error)
            return formatted_results
        for res in list_of_results:
            res_from = res.get('from')
            res_to = res.get('to')
            res_types = res.get('types')
            num = res.get('num')
            if res_types:
                result = {
                    'from_date': {'date': res_from['date'], 'time': res_from['time']},
                    'to_date': {'date': res_to['date'], 'time': res_to['time']},
                    'places': [{'title': type['title'], 'places': type['places']} for type in res_types],
                    'num': num,
                    # '_full_info': res
                }
                formatted_results.append(result)
        return formatted_results


class ResultsDB(ResponseFormatterInterface):

    @staticmethod
    def dump(file_name: str | Path, results: dict | list[dict]):
        with open(file_name, 'w', encoding='utf-8') as file:
            json.dump(results, file)

    @staticmethod
    def load(file_name: str | Path) -> dict:
        with open(file_name, encoding='utf-8') as file:
            return json.load(file)


class MessageFormatter:
    message: str

    def __init__(self, train: dict, train_wagons: dict, departure: Departure):
        train_url = self.create_wagon_link(train["num"], dep_date=departure.date,
                                           dep_from=departure.path.dep_from,
                                           dep_to=departure.path.dep_to)
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
