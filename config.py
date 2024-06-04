IAM_TOKEN = 't1.9euelZqWls6VnsqPnZSQlpSNl82Xj-3rnpWalZvJyZbPysmVyZ3KjprMzInl8_dLQX1N-e8OQCEI_t3z9wtwek357w5AIQj-zef1656VmpbPkp6bjcjIjJHGy83MkciW7_zF656VmpbPkp6bjcjIjJHGy83MkciWveuelZrLzJ6alcnPkpDHkMvGkpObx7XehpzRnJCSj4qLmtGLmdKckJKPioua0pKai56bnoue0oye.jus-YK3udg9BdbKzzBSWvl2Ll275CgpLZCfqUyMzQUziKIotVlW79fPzaW_GUpbPKHLajkwyZFKHpLgGtvUtDA'
FOLDER_ID = "b1gd9cphe9fc3et8kkvm"
TOKEN = '6766865935:AAHuBKHmMTD0PLATyXwIFv7lkaG_pebuBgk'

MAX_TTS_SYMBOLS = 250
MAX_USER_TTS_SYMBOLS = 5000
MAX_USER_STT_BLOCKS = 10
MAX_USER_GPT_TOKENS = 10000  # 2 000 токенов


HEADERS = {
        'Authorization': f'Bearer {IAM_TOKEN}',
    }

DB_NAME = 'db.sqlite'
TABLE_NAME = 'texts'

RESPONCE_STT = 'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?'
RESPONCE = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'


MAX_USERS = 3  # максимальное кол-во пользователей
MAX_GPT_TOKENS = 120  # максимальное кол-во токенов в ответе GPT
COUNT_LAST_MSG = 4  # кол-во последних сообщений из диалога



LOGSa = 'logs.txt'  # файл для логов
DB_FILEa = 'messages.db'  # файл для базы данных
SYSTEM_PROMPT = [{'role': 'system', 'text': 'Ты веселый собеседник. Общайся с пользователем на "ты" и используй юмор. '
                                            'Поддерживай диалог. Не объясняй пользователю, что ты умеешь и можешь. '
                                            'Отвечай только на вопрос пользователя, лишней информации от себя не добавляй.'
                                            'Твоё имя - OPTIMAL_AI'
                                            'Если пользователь пишет непонятный набор символов, отвечай что ты не понял пользователя, и попроси пользователя ввести запрос конкретней'
                                            'Не будь слишком занудным при общении с пользователем, разукрашивай своё общение различными эмоциональными приёмами, шутками, весели пользователя'
                                            'Не пиши слишком много текста пользователю, отвечай пользователю кратко, если он попросит давать длинные ответы - отвечай длинным текстом'
                                            'Если пользоваетль матерится - говори что не любишь маты, и вежливо попроси пользователя не материться'}]  # список с системным промтом


HOME_DIR = '/home/student/OPTIMAL_BOT_TG'  # путь к папке с проектом
LOGS = f'{HOME_DIR}/logs.txt'  # файл для логов
DB_FILE = f'{HOME_DIR}/messages.db'  # файл для базы данных

IAM_TOKEN_PATH = f'{HOME_DIR}/creds/iam_token.txt'  # файл для хранения iam_token
FOLDER_ID_PATH = f'{HOME_DIR}/creds/folder_id.txt'  # файл для хранения folder_id
BOT_TOKEN_PATH = f'{HOME_DIR}/creds/bot_token.txt'  # файл для хранения bot_token
