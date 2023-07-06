import abc
import logging
from time import sleep

import loguru
import requests

from module import config


class SolverInterface:

    @abc.abstractmethod
    def solve(self, *args, **kwargs) -> str | None:
        ...


class CapMonsterSolver(SolverInterface):
    host = f'http://{config.CAPMONSTER_HOST}/in.php'
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance:
            return cls._instance
        else:
            return super().__new__(cls)

    def __init__(self):
        self.state = self.ping()

    @classmethod
    def ping(cls) -> bool:
        try:
            resp = requests.get(cls.host, timeout=1)
            return resp.ok
        except Exception as err:
            loguru.logger.error(err)
            return False

    @classmethod
    def solve(cls, googlekey: str, pageurl: str, time_limit: int = 30, version: str = 'v2', action: str = 'verify',
              score: str = '0.3') -> str | None:
        request: str = cls._send_request(googlekey=googlekey, pageurl=pageurl, version=version, action=action,
                                         score=score).text
        print(request)
        if 'OK' not in request:
            return
        status, request_id = request.split('|')
        request: str = cls._await_for_result(request_id, time_limit=time_limit)
        if 'OK' in request:
            status, captcha_answer = request.split('|')
            return captcha_answer
        else:
            print(request)
            return

    @classmethod
    def _send_request(cls, googlekey: str, pageurl: str, version: str = 'v2', action: str = 'verify',
                      score='0.6') -> requests.Response:
        params = {
            'method': 'userrecaptcha',
            'soft_id': '19',
            'version': version,
            'pageurl': pageurl,
            'googlekey': googlekey,
            'key': config.CAPMONSTER_KEY
        }
        if version == 'v3':
            params['action'] = action
            params['min_score'] = score

        response = requests.get(cls.host, params=params, timeout=10)
        return response

    @classmethod
    def _check_request(cls, request_id: str) -> requests.Response:
        params = {
            'action': 'get',
            'id': request_id,
            'key': config.CAPMONSTER_KEY

        }
        response = requests.get(cls.host, params=params, timeout=10)
        return response

    @classmethod
    def _await_for_result(cls, request_id: str, time_limit: int) -> str:
        for _ in range(time_limit):
            try:
                res = cls._check_request(request_id)
                result = res.text
                match result:
                    case 'CAPCHA_NOT_READY':
                        sleep(1)
                    case _:
                        return result
            except Exception as error:
                logging.exception(error)
                return ''
