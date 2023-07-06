import time
import datetime
import telebot


from module import config, utils, parser
from module.config import logger

ACCEPTABLE_TIME = '19:00'
WAGON_TYPE = 'Плацкарт'


TIME_FORMAT = '%H:%M'
ACCEPTABLE_TIME = datetime.datetime.strptime(ACCEPTABLE_TIME, TIME_FORMAT)

bot = telebot.TeleBot(config.BOT_TOKEN)


def check_results():
    parse_results = utils.ResultsDB.load_json_results()
    results = []
    acceptable = False
    for result in parse_results:
        get_from_date__get = result.get('from_date').get('time')
        time_res = datetime.datetime.strptime(get_from_date__get, TIME_FORMAT)

        for place in result['places']:
            if place.get('title') == WAGON_TYPE or time_res >= ACCEPTABLE_TIME:
                acceptable = True

        if acceptable:
            results.append(result)
            acceptable = False
    if results:
        for res in results:
            types = parser.get_cost(res['num'])
            res['types'] = types

    return results


if __name__ == '__main__':
    while True:
        results = check_results()
        if results:
            for res in results:
                logger.info(res)
                del res['from_date']
                res['url'] = f'https://booking.uz.gov.ua/?from=2200001&to=2218000&date=2023-07-13&train={res["num"]}&url=train-wagons'
                del res['num']
                bot.send_message(265753495, str(res))
        time.sleep(60*15)
