import json
import time
from pathlib import Path

import requests

from module import captcha_solvers
from module.config import logger, ROOT_FOLDER
from module.utils import ResultsDB

PAGEURL = 'https://booking.uz.gov.ua'
GOOGLEKEY = '6LeNkKoUAAAAACciOzccHLPuCS9aFEHPa3Taz4Zf'
DATE = '2023-07-13'
WAGON_RES = Path(ROOT_FOLDER, 'wagon_res.json')


def get_results_response():
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://booking.uz.gov.ua',
        'Referer': 'https://booking.uz.gov.ua/?from=2200001&to=2218000&date=2023-07-13&time=00%3A00&url=train-list',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Cookie': '__uzma=8c25d6ad-daba-499a-82d6-6e09147248d8; __uzmb=1688642918; __uzme=0111; HTTPSERVERID=server2; cookiesession1=678B286ED3B9CEA7703D77B60603A5A7; _gv_lang=uk; _gv_sessid=7701tdvltntjb6db9d0v9rh8a4; _ga=GA1.3.428927995.1688642921; _gid=GA1.3.542270101.1688642921; __uzmc=2245838579321; __uzmd=1688654561',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'cache-version': '761',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    data = {
        'from': '2200001',
        'to': '2218000',
        'date': DATE,
        'time': '00:00',
        'get_tpl': '1',
    }

    response = requests.post('https://booking.uz.gov.ua/train_search/', data=data, headers=headers)
    if 'captcha' in response.text:
        logger.error(f'{response.text=}')
        cap = captcha_solvers.CapMonsterSolver.solve(GOOGLEKEY, PAGEURL)
        data['captcha'] = cap
        response = requests.post('https://booking.uz.gov.ua/train_search/', data=data, headers=headers)
    return response


def get_wagon(wagon_num: str):

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://booking.uz.gov.ua',
        'Referer': 'https://booking.uz.gov.ua/?from=2200001&to=2218000&date=2023-07-13&time=00%3A00&train=055%D0%9E&wagon_type_id=%D0%A12&url=train-wagons',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'cache-version': '761',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Cookie': '__uzma=8c25d6ad-daba-499a-82d6-6e09147248d8; __uzmb=1688642918; __uzme=0111; HTTPSERVERID=server2; cookiesession1=678B286ED3B9CEA7703D77B60603A5A7; _gv_lang=uk; _gv_sessid=7701tdvltntjb6db9d0v9rh8a4; _ga=GA1.3.428927995.1688642921; _gid=GA1.3.542270101.1688642921; __uzmc=9840639191893; __uzmd=1688654647'
    }

    data = {
        'from': '2200001',
        'to': '2218000',
        'train': wagon_num,
        'date': DATE,
        'wagon_num': '12',
        'wagon_type': 'С',
        'wagon_class': '2',
    }

    response = requests.post('https://booking.uz.gov.ua/train_wagons/', headers=headers, data=data)

    if 'captcha' in response.text:
        logger.error(f'{response.text=}')
        cap = captcha_solvers.CapMonsterSolver.solve(GOOGLEKEY, PAGEURL)
        data['captcha'] = cap
        response = requests.post('https://booking.uz.gov.ua/train_wagons/', headers=headers, data=data)
    return response


def get_cost(wagon_num):
    resp = get_wagon(wagon_num)
    types = resp.json()
    with open(WAGON_RES, 'w') as file:
        json.dump(types, file)
    with open(WAGON_RES) as file:
        res = json.load(file)
    return res['data']['types']


def parse_results():
    while True:
        results_response: requests.Response = get_results_response()
        response_json: dict = results_response.json()
        formatted_results = ResultsDB.format_results(response_json)
        logger.info(formatted_results)
        if formatted_results:
            ResultsDB.dump_json_results(formatted_results)
        time.sleep(60 * 1)


if __name__ == '__main__':
    parse_results()
