import requests

from module import captcha_solvers, enums
from module.config import logger

PAGEURL = 'https://booking.uz.gov.ua'
GOOGLEKEY = '6LeNkKoUAAAAACciOzccHLPuCS9aFEHPa3Taz4Zf'


def get_trains(from_value: enums.CityEnum, to_value: enums.CityEnum, departure_date: str) -> requests.Response:
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
        'from': from_value.value,
        'to': to_value.value,
        'date': departure_date,
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


def get_train_wagons(wagon_num: str, from_value: enums.CityEnum, to_value: enums.CityEnum,
                     departure_date: str) -> requests.Response:
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
        'from': from_value.value,  # 2200001
        'to': to_value.value,  # 2218000
        'train': wagon_num,
        'date': departure_date,
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
