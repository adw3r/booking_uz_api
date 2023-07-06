import json
from pathlib import Path

from module.config import ROOT_FOLDER, logger

RESULTS_JSON = Path(ROOT_FOLDER, 'results.json')


class ResultsDB:

    @staticmethod
    def format_results(raw_results: dict) -> list[dict]:
        formatted_results = []
        try:
            list_of_results = raw_results.get('data').get('list')
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

    @staticmethod
    def dump_json_results(results: dict | list[dict]):
        with open(RESULTS_JSON, 'w', encoding='utf-8') as file:
            json.dump(results, file)

    @staticmethod
    def load_json_results() -> dict:
        with open(RESULTS_JSON, encoding='utf-8') as file:
            return json.load(file)
