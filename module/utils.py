import abc
import json
from pathlib import Path

import requests

from module.config import logger


class ResponseFormatterInterface(abc.ABC):

    @staticmethod
    @abc.abstractmethod
    def format(response: requests.Response) -> dict | list[dict]:
        ...


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
