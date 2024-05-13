from bot.config import RESPONCE, RESPONCE_STT
import requests
from bot.creds import get_creds  # модуль для получения токенов

iam_token, folder_id = get_creds()  # получаем iam_token и folder_id из файлов\

HEADERS = {
        'Authorization': f'Bearer {iam_token}',
    }


def text_to_speech(text):
    headers = HEADERS
    data = {
        'text': text,
        'lang': 'ru-RU',
        'voice': 'filipp',  #
        'folderId': folder_id,
    }
    # Выполняем запрос
    response = requests.post(RESPONCE, headers=headers, data=data)

    if response.status_code == 200:
        return True, response.content  # Возвращаем голосовое сообщение
    else:
        return False, "При запросе в SpeechKit возникла ошибка"



def speech_to_text(data):
    params = "&".join([
        "topic=general",  # используем основную версию модели
        f"folderId={folder_id}",
        "lang=ru-RU"  # распознаём голосовое сообщение на русском языке
    ])

    # Аутентификация через IAM-токен
    headers = HEADERS

    # Выполняем запрос
    response = requests.post(
        f"{RESPONCE_STT}{params}",
        headers=headers,
        data=data
    )

    # Читаем json в словарь
    decoded_data = response.json()
    # Проверяем, не произошла ли ошибка при запросе
    if decoded_data.get("error_code") is None:
        return True, decoded_data.get("result")  # Возвращаем статус и текст из аудио
    else:
        return False, "При запросе в SpeechKit возникла ошибка"