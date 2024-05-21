import time

from environs import Env
from loguru import logger
import requests
import telegram


def get_checks_long_polling(devman_token, timestamp):
    headers = {"Authorization": f'Token {devman_token}'}
    params = {'timestamp': timestamp}
    url = 'https://dvmn.org/api/long_polling/'
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def format_success_message(checks):
    success_message_template = (
        f'У вас проверили работу "{checks["new_attempts"][0]["lesson_title"]}"\n\n'
        f'Преподавателю все понравилось, можно приступать к следующему уроку!\n\n'
        f'{checks["new_attempts"][0]["lesson_url"]}')
    return success_message_template


def format_unsuccess_message(checks):
    unsuccess_message_template = (
        f'У вас проверили работу "{checks["new_attempts"][0]["lesson_title"]}"\n\n'
        f'К сожалению, в работе нашлись ошибки.\n\n'
        f'{checks["new_attempts"][0]["lesson_url"]}')
    return unsuccess_message_template


def main():
    env = Env()
    env.read_env()

    tg_token = env.str('TG_TOKEN')
    chat_id = env.str('TG_CHAT_ID')
    devman_token = env.str('DEVMAN_TOKEN')

    bot = telegram.Bot(token=tg_token)

    timestamp = None
    while True:
        try:
            checks = get_checks_long_polling(devman_token, timestamp)
            logger.info(f'Ответ от сервера: {checks}')

            if 'found' in checks['status']:
                for attempt in checks['new_attempts']:
                    if attempt['is_negative']:
                        bot.send_message(text=format_unsuccess_message(checks), chat_id=chat_id,)
                    else:
                        bot.send_message(text=format_success_message(checks), chat_id=chat_id,)
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
