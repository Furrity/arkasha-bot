from typing import List
from random import randint, choice
import sqlite3
from datetime import datetime

# сюда прописывать все команды для базы данных
COMMAND_LIST = ['lowprice', 'highprice', 'bestdeal', 'help', 'history']


def setup():
    """
    Данный метод создает базу данных, если ее еще нет.
    Затем наполняет ее нужными таблицами, если они еще не созданы.
    """
    conn = sqlite3.connect('query.db')

    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_query 
    (user_id INTEGER NOT NULL, 
    timestamp INTEGER, 
    command_rowid TEXT)""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS command
    (command_name TEXT UNIQUE);""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS query_hotel
    (user_query_rowid INTEGER NOT NULL,
    hotel_rowid INTEGER);""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hotel (
    hotel_description TEXT);""")

    conn.commit()
    conn.close()


def add_commands():
    """Данный метод заполняет таблицу `command` в базе данных описанными выше командами."""
    conn = sqlite3.connect('query.db')
    cursor = conn.cursor()

    for command in COMMAND_LIST:

        cursor.execute("""
        INSERT OR IGNORE INTO command VALUES (?);""",
                       (command,))

    conn.commit()
    conn.close()


def add_query(user_id: int, command: str) -> int:
    """
    Сохраняет в таблицу `user_query` запрос пользователя.
    Возвращает rowid той записи, которая была создана."""
    conn = sqlite3.connect('query.db')
    cursor = conn.cursor()

    cursor.execute("""SELECT rowid, * FROM command
                       WHERE command_name = ?;""", (command,))
    command_id = cursor.fetchone()[0]

    cursor.execute("""
    INSERT INTO user_query VALUES 
    (?, ?, ?)""", (user_id, datetime.timestamp(datetime.now()), command_id))
    query_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return query_id


def add_hotel(query_id: int, hotel_description: str):
    """Добавляет отель в таблицу `hotel` и связывает его в таблице `query_hotel`"""
    conn = sqlite3.connect('query.db')
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO hotel VALUES (?)""", (hotel_description,))

    hotel_id = cursor.lastrowid

    cursor.execute("""INSERT INTO query_hotel VALUES (?, ?);""", (query_id, hotel_id))

    conn.commit()
    conn.close()


def _select_all():
    """Метод для разработки показывает все строки из таблицы `user_query`"""
    conn = sqlite3.connect('query.db')

    cursor = conn.cursor()

    cursor.execute("""SELECT rowid, * FROM user_query""")
    conn.commit()
    conn.close()


def _select_all_command_names():
    """Метод для разработки. Выводит все строки из таблицы `command`"""
    conn = sqlite3.connect('query.db')

    cursor = conn.cursor()

    cursor.execute("""SELECT rowid, * FROM command""")

    conn.commit()
    conn.close()


def show_history(user_id: int) -> List[tuple]:
    """
    Делает запрос к базе данных.
    На вход получает id пользователя.
    Возвращает список. В списке находятся кортежи со следующими данными:
    [0] Название команды, которую вызвал пользователь
    [1] Timestamp времени вызова команды.
    [2] Описание отеля, как это было в сообщении пользователю."""
    conn = sqlite3.connect('query.db')
    cursor = conn.cursor()

    cursor.execute("""
    SELECT command.command_name, user_query.timestamp, hotel.hotel_description
    FROM query_hotel
    JOIN user_query  ON user_query.rowid = query_hotel.user_query_rowid
    JOIN hotel ON hotel.rowid = query_hotel.hotel_rowid
    JOIN command ON command.rowid = user_query.command_rowid
    WHERE user_query.user_id = ?
    ORDER BY user_query.timestamp DESC
    LIMIT 10;
    """, (user_id,))
    result = cursor.fetchall()

    conn.commit()
    conn.close()
    return result


def _populate_db():
    """Метод для разработки. Наполняет базу данных случайными записями."""
    for i in range(100):
        user: int = randint(0, 10)
        q = add_query(user, choice(('lowprice', 'highprice', 'bestdeal')))
        for j in range(randint(0, 10)):
            add_hotel(q, f'hotel_description = {j}')
