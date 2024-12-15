import time
import logging

import requests
import telegram
from environs import Env


logger = logging.getLogger(__name__)


class TelegramLogsHandler(logging.Handler):
    def __init__(self, bot, chat_id):
        super().__init__()
        self.chat_id =chat_id
        self.tg_bot = bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.sendMessage(chat_id=self.chat_id, text=log_entry)


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
    logging.basicConfig(level=logging.ERROR)
    logger.setLevel(logging.DEBUG)

    env = Env()
    env.read_env()

    tg_token = env.str('TG_TOKEN')
    chat_id = env.str('TG_CHAT_ID')
    devman_token = env.str('DEVMAN_TOKEN')

    bot = telegram.Bot(token=tg_token)

    logger.addHandler(TelegramLogsHandler(bot, chat_id))
    logger.info('Бот запущен')

    timestamp = None
    while True:
        try:
            checks = get_checks_long_polling(devman_token, timestamp)
            if 'found' in checks['status']:
                for attempt in checks['new_attempts']:
                    send_message_template(bot, chat_id, attempt)

                timestamp = checks['last_attempt_timestamp']

            elif 'timeout' in checks['status']:
                timestamp = checks['timestamp_to_request']

        except requests.exceptions.Timeout:
            logger.warning('Превышено время ожидания запроса')
        except requests.exceptions.ConnectionError:
            logger.error('Ошибка соединения')
            time.sleep(5)
        except Exception as e:
            logger.error(f'Неизвестная ошибка: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
