# Devman-Check-Notifier-Bot
Бот для получения уведомлений о проверке работ на сайте <https://dvmn.org/>

## Как запустить

Создайте в корне проекта, файл `.env` Пропишите в нем:

```
TG_TOKEN=ТОКЕН ВАШЕГО БОТА 
DEVMAN_TOKEN=ТОКЕН DEVMAN
TG_CHAT_ID=ВАШ_CHAT_ID
```
где:

`TG_TOKEN` - получить при создании телеграм бота в боте [BotFather](https://t.me/BotFather)

`DEVMAN_TOKEN` - получить в документации [API Девмана](https://dvmn.org/api/docs/)

`TG_CHAT_ID` - получить с помощью телеграм бота [userinfobot](https://t.me/userinfobot)


Для изоляции проекта рекомендуется развернуть виртуальное окружение:

для Linux и MacOS
```bash
python3 -m venv env
source env/bin/activate
```

для Windows
```bash
python -m venv env
venv\Scripts\activate.bat
```

Python3 должен быть уже установлен. Затем используйте pip (или pip3, есть конфликт с Python2) для установки зависимостей:

```bash
pip install -r requirements.txt
```



## Использование

Для запуска бота:

```bash
python cheker_bot.py
```


