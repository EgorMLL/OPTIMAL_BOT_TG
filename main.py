from creds import get_bot_token
from validators import *
from config import TOKEN, MAX_TTS_SYMBOLS, MAX_USER_TTS_SYMBOLS, LOGS, COUNT_LAST_MSG
import telebot
from db import prepare_db, insert_row, count_all_symbol, insert_row_stt, create_database, add_message, select_n_last_messages
from speechkit import text_to_speech, speech_to_text
from telebot.types import ReplyKeyboardMarkup
from yandex_gpt import ask_gpt


API_TOKEN = TOKEN
bot = telebot.TeleBot(get_bot_token())







markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет! Я бот, который переводит текст в голосовое сообщение! Попробуй меня, введя команду /tts')


@bot.message_handler(commands=['debug'])
def send_logs(message):
    with open("/logs.txt", "rb") as f:
        bot.send_document(message.chat.id, f)

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.from_user.id, "Чтобы приступить к общению, отправь мне голосовое сообщение или текст")

@bot.message_handler(commands=['tts'])
def tts_handler(message):
    bot.send_message(message.chat.id, 'Отправь следующим сообщеним текст, чтобы я его озвучил!')
    logging.debug("Функция TTS_handler сработала.")
    bot.register_next_step_handler(message, tts)

@bot.message_handler(commands=['stt'])
def stt_handler(message):
    bot.send_message(message.chat.id, 'Отправь следующим сообщеним аудио сообщение, чтобы я его перевёл в текст!')
    logging.debug("Функция TTS_handler сработала.")
    bot.register_next_step_handler(message, stt)





def tts(message):
    text = message.text

    a = len(text)
    user_id = message.from_user.id

    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Отправь текстовое сообщение')
        bot.register_next_step_handler(message, tts)
        return

    if a >= MAX_TTS_SYMBOLS:
        msg = f"Превышен лимит SpeechKit TTS на запрос {MAX_TTS_SYMBOLS}."
        bot.send_message(message.chat.id, msg)
        logging.info("У пользоваеля превышен лимит символов.")
        bot.register_next_step_handler(message, tts)
        return

    if count_all_symbol(message.chat.id)[0] >= MAX_USER_TTS_SYMBOLS:
        msg = f"Превышен лимит токенов на пользователя в сумме {MAX_TTS_SYMBOLS} символов! Вы больше не сможете отправлять текст."
        bot.send_message(message.chat.id, msg)
        logging.info("У пользоваеля превышен общий лимит символов.")
        bot.register_next_step_handler(message, tts)
        return


    insert_row(user_id, text, len(text))


    status, content = text_to_speech(text)
    logging.debug("Функция TTS и все её проверки сработали.")


    if status:
        bot.send_voice(message.chat.id, content)
        logging.info("Голосовое сообщение было успешно отправлено.")
    else:
        bot.send_message(message.chat.id, content)
        logging.info("Ошибка! Голосовое сообщение не отправлено.")


def stt(message):
    user_id = message.from_user.id


    if not message.voice:
        return


    stt_blocks = is_stt_block_limit(message, message.voice.duration)
    if not stt_blocks:
        return

    file_id = message.voice.file_id
    file_info = bot.get_file(file_id)
    file = bot.download_file(file_info.file_path)

    # Получаем статус и содержимое ответа от SpeechKit
    status, text = speech_to_text(file)  # преобразовываем голосовое сообщение в текст

    # Если статус True - отправляем текст сообщения и сохраняем в БД, иначе - сообщение об ошибке
    if status:
        # Записываем сообщение и кол-во аудиоблоков в БД
        insert_row_stt(user_id, text, stt_blocks)
        bot.send_message(user_id, text, reply_to_message_id=message.id)
    else:
        bot.send_message(user_id, text)


# Декоратор для обработки голосовых сообщений, полученных ботом
# Декоратор для обработки голосовых сообщений, полученных ботом
@bot.message_handler(content_types=['voice'])
def handle_voice(message):

        user_id = message.from_user.id

        # Проверка на максимальное количество пользователей
        status_check_users, error_message = check_number_of_users(user_id)
        if not status_check_users:
            bot.send_message(user_id, error_message)
            return

    # Проверка на доступность аудиоблоков
        stt_blocks = is_stt_block_limit(message.from_user.id, message.voice.duration)
        if error_message:
            bot.send_message(user_id, error_message)
            return

    # Обработка голосового сообщения
        file_id = message.voice.file_id
        file_info = bot.get_file(file_id)
        file = bot.download_file(file_info.file_path)
        status_stt, stt_text = speech_to_text(file)
        if not status_stt:
            bot.send_message(user_id, stt_text)
            return

    # Запись в БД
        add_message(user_id=user_id, full_message=[stt_text, 'user', 0, 0, stt_blocks])

    # Проверка на доступность GPT-токенов
        last_messages, total_spent_tokens = select_n_last_messages(user_id, COUNT_LAST_MSG)
        total_gpt_tokens, error_message = is_gpt_token_limit(last_messages, total_spent_tokens)
        if error_message:
            bot.send_message(user_id, error_message)
            return

    # Запрос к GPT и обработка ответа
        status_gpt, answer_gpt, tokens_in_answer = ask_gpt(last_messages)
        if not status_gpt:
            bot.send_message(user_id, answer_gpt)
            return
        total_gpt_tokens += tokens_in_answer

    # Проверка на лимит символов для SpeechKit
        tts_symbols = is_tts_symbol_limit(user_id, answer_gpt)

    # Запись ответа GPT в БД
        add_message(user_id=user_id, full_message=[answer_gpt, 'assistant', total_gpt_tokens, tts_symbols, 0])

        if error_message:
            bot.send_message(user_id, error_message)
            return


        status_tts, voice_response = text_to_speech(answer_gpt)
        if status_tts:
            bot.send_voice(user_id, voice_response, reply_to_message_id=message.id)
        else:
            bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)





@bot.message_handler(content_types=['text'])
def handle_text(message):
    try:
        user_id = message.from_user.id


        status_check_users, error_message = check_number_of_users(user_id)
        if not status_check_users:
            bot.send_message(user_id, error_message)
            return


        full_user_message = [message.text, 'user', 0, 0, 0]
        add_message(user_id=user_id, full_message=full_user_message)


        last_messages, total_spent_tokens = select_n_last_messages(user_id, COUNT_LAST_MSG)

        total_gpt_tokens, error_message = is_gpt_token_limit(last_messages, total_spent_tokens)
        if error_message:
            # если что-то пошло не так — уведомляем пользователя и прекращаем выполнение функции
            bot.send_message(user_id, error_message)
            return

        # GPT: отправляем запрос к GPT
        status_gpt, answer_gpt, tokens_in_answer = ask_gpt(last_messages)
        # GPT: обрабатываем ответ от GPT
        if not status_gpt:
            # если что-то пошло не так — уведомляем пользователя и прекращаем выполнение функции
            bot.send_message(user_id, answer_gpt)
            return
        # сумма всех потраченных токенов + токены в ответе GPT
        total_gpt_tokens += tokens_in_answer

        # БД: добавляем ответ GPT и потраченные токены в базу данных
        full_gpt_message = [answer_gpt, 'assistant', total_gpt_tokens, 0, 0]
        add_message(user_id=user_id, full_message=full_gpt_message)

        bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)  # отвечаем пользователю текстом
    except Exception as e:
        logging.error(e)  # если ошибка — записываем её в логи
        bot.send_message(message.from_user.id, "Не получилось ответить. Попробуй написать другое сообщение")



@bot.message_handler(func=lambda: True)
def handler(message):
    bot.send_message(message.from_user.id, "Отправь мне голосовое или текстовое сообщение, и я тебе отвечу")


prepare_db()
create_database()

if __name__ == "__main__":
    logging.debug("Бот запущен")
    bot.polling(non_stop=True)