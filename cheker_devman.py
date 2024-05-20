import time

from environs import Env
from loguru import logger
import requests


def get_checks_long_polling(headers, timestamp):
    params = {'timestamp': timestamp}
    url = 'https://dvmn.org/api/long_polling/'
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def main():
    env = Env()
    env.read_env()

    devman_token = env.str('DEVMAN_TOKEN')
    headers = {"Authorization": f'Token {devman_token}'}
    timestamp = None
    while True:
        try:
            checks = get_checks_long_polling(headers, timestamp)
            if 'found' in checks['status']:
                logger.info(f'Проверена работа - {checks['new_attempts']}')
                timestamp = checks['last_attempt_timestamp']
            elif 'timeout' in checks['status']:
                timestamp = checks['timestamp_to_request']
        except requests.exceptions.ReadTimeout:
            logger.warning('Превышено время ожидания запроса')
        except requests.exceptions.ConnectionError:
            logger.error('Ошибка соединения')
            time.sleep(5)


if __name__ == '__main__':
    main()
