import time

import requests
import telegram
from environs import Env
from loguru import logger


def get_checks_long_polling(devman_token, timestamp):
    headers = {'Authorization': f'Token {devman_token}'}
    params = {'timestamp': timestamp}
    url = 'https://dvmn.org/api/long_polling/'
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def send_message_template(bot, chat_id, attempt):
    if attempt['is_negative']:
        message_template = (
            f'У вас проверили работу "{attempt["lesson_title"]}"\n\n'
            f'К сожалению, в работе нашлись ошибки.\n\n'
            f'{attempt["lesson_url"]}')
    else:
        message_template = (
            f'У вас проверили работу "{attempt["lesson_title"]}"\n\n'
            f'Преподавателю все понравилось, можно приступать к следующему уроку!\n\n'
            f'{attempt["lesson_url"]}')

    bot.send_message(chat_id=chat_id, text=message_template)


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
                    send_message_template(bot, chat_id, attempt)

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
