import sqlite3
from config import TABLE_NAME, DB_NAME, LOGS, DB_FILE
import logging  # модуль для сбора логов





con = sqlite3.connect('db.sqlite', check_same_thread=False)
cur = con.cursor()


def execute_selection_query(sql_query, data=None, db_path=DB_NAME):
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        if data:
            cursor.execute(sql_query, data)
        else:
            cursor.execute(sql_query)
        rows = cursor.fetchall()
        connection.close()
        return rows
    except Exception as e:
        logging.error(e)
        return None


def create_table(TABLE_NAME):
    try:
        sql_query = f'''
                CREATE TABLE IF NOT EXISTS {TABLE_NAME} 
                (id INTEGER PRIMARY KEY,
                user_id INTEGER,
                text TEXT,
                tts_symbols INTEGER,
                stt_blocks INTEGER)
            '''
        cur.execute(sql_query)
    except Exception as e:
        logging.error(e)
        return None

def insert_row_stt(user_id, message, stt_symbols, table_name=f'{TABLE_NAME}'):
    try:
        cur.execute(f'''
        INSERT INTO {table_name}
        (user_id, text, stt_blocks)
        VALUES (?, ?, ?)
         ''', (user_id, message, stt_symbols))
        con.commit()
    except Exception as e:
        logging.error(e)
        return None


def insert_row(user_id, message, tts_symbols, table_name=f'{TABLE_NAME}'):
    try:
        cur.execute(f'''
        INSERT INTO {table_name}
        (user_id, text, tts_symbols)
        VALUES (?, ?, ?)
        ''', (user_id, message, tts_symbols))
        con.commit()
    except Exception as e:
        logging.error(e)
        return None


def insert_user_id(user_id, message, table_name=f'{TABLE_NAME}'):
    try:
        cur.execute(f'''
        INSERT INTO {table_name}
        (user_id, text)
        VALUES (?, ?)''',
        (user_id, message))
        con.commit()
    except Exception as e:
        logging.error(e)
        return None

def count_all_symbol(user_id):
    try:
        sql_query = f'''
        SELECT SUM(tts_symbols)
        FROM {TABLE_NAME}
        WHERE user_id = {user_id}
        GROUP BY user_id
        '''
        data = execute_selection_query(sql_query)

        if data:
            return data[0]
        return 0
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return None

def count_all_blocks(user_id):
    try:
        # подключаемся к базе данных
            sql_query = f'''
            SELECT SUM(stt_blocks) 
            FROM {TABLE_NAME} 
            WHERE user_id = {user_id}
            GROUP BY user_id
            '''
            data = execute_selection_query(sql_query)

            if data:
                return data[0]
            return 0
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return None

def prepare_db():
    create_table(TABLE_NAME)




# настраиваем запись логов в файл
logging.basicConfig(filename=LOGS, level=logging.ERROR,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")
path_to_db = DB_FILE  # файл базы данных

# создаём базу данных и таблицу messages
def create_database():
    try:
        # подключаемся к базе данных
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            # создаём таблицу messages
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                message TEXT,
                role TEXT,
                total_gpt_tokens INTEGER,
                tts_symbols INTEGER,
                stt_blocks INTEGER)
            ''')
            logging.info("DATABASE: База данных создана")  # делаем запись в логах
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return None



...

# добавляем новое сообщение в таблицу messages
def add_message(user_id, full_message):
    try:
        # подключаемся к базе данных
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            message, role, total_gpt_tokens, tts_symbols, stt_blocks = full_message
            # записываем в таблицу новое сообщение
            cursor.execute('''
                    INSERT INTO messages (user_id, message, role, total_gpt_tokens, tts_symbols, stt_blocks) 
                    VALUES (?, ?, ?, ?, ?, ?)''',
                           (user_id, message, role, total_gpt_tokens, tts_symbols, stt_blocks)
                           )
            conn.commit()  # сохраняем изменения
            logging.info(f"DATABASE: INSERT INTO messages "
                         f"VALUES ({user_id}, {message}, {role}, {total_gpt_tokens}, {tts_symbols}, {stt_blocks})")
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return None

# считаем количество уникальных пользователей помимо самого пользователя
def count_users(user_id):
    try:
        # подключаемся к базе данных
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            # получаем количество уникальных пользователей помимо самого пользователя
            cursor.execute('''SELECT COUNT(DISTINCT user_id) FROM messages WHERE user_id <> ?''', (user_id,))
            count = cursor.fetchone()[0]
            return count
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return None


# получаем последние <n_last_messages> сообщения
def select_n_last_messages(user_id, n_last_messages=4):
    messages = []  # список с сообщениями
    total_spent_tokens = 0  # количество потраченных токенов за всё время общения
    try:
        # подключаемся к базе данных
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            # получаем последние <n_last_messages> сообщения для пользователя
            cursor.execute('''
            SELECT message, role, total_gpt_tokens FROM messages WHERE user_id=? ORDER BY id DESC LIMIT ?''',
                           (user_id, n_last_messages))
            data = cursor.fetchall()
            # проверяем data на наличие хоть какого-то полученного результата запроса
            # и на то, что в результате запроса есть хотя бы одно сообщение - data[0]
            if data and data[0]:
                # формируем список сообщений
                for message in reversed(data):
                    messages.append({'text': message[0], 'role': message[1]})
                    total_spent_tokens = max(total_spent_tokens, message[2])  # находим максимальное количество потраченных токенов
            # если результата нет, так как у нас ещё нет сообщений - возвращаем значения по умолчанию
            return messages, total_spent_tokens
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return messages, total_spent_tokens

# подсчитываем количество потраченных пользователем ресурсов (<limit_type> - символы или аудиоблоки)
def count_all_limits(user_id, limit_type):
    try:
        # подключаемся к базе данных
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            # считаем лимиты по <limit_type>, которые использовал пользователь
            cursor.execute(f'''SELECT SUM({limit_type}) FROM messages WHERE user_id=?''', (user_id,))
            data = cursor.fetchone()
            # проверяем data на наличие хоть какого-то полученного результата запроса
            # и на то, что в результате запроса мы получили какое-то число в data[0]
            if data and data[0]:
                # если результат есть и data[0] == какому-то числу, то:
                logging.info(f"DATABASE: У user_id={user_id} использовано {data[0]} {limit_type}")
                return data[0]  # возвращаем это число - сумму всех потраченных <limit_type>
            else:
                # результата нет, так как у нас ещё нет записей о потраченных <limit_type>
                return 0  # возвращаем 0
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return 0