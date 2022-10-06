from random import randint, choice
import sqlite3
from datetime import datetime


COMMAND_LIST = ['lowprice', 'highprice', 'bestdeal', 'help', 'history']


def setup():
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
    conn = sqlite3.connect('query.db')
    cursor = conn.cursor()

    for command in COMMAND_LIST:

        cursor.execute("""
        INSERT OR IGNORE INTO command VALUES (?);""",
                       (command,))

    conn.commit()
    conn.close()


def add_query(user_id: int, command: str) -> int:
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
    conn = sqlite3.connect('query.db')
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO hotel VALUES (?)""", (hotel_description,))

    hotel_id = cursor.lastrowid

    cursor.execute("""INSERT INTO query_hotel VALUES (?, ?);""", (query_id, hotel_id))

    conn.commit()
    conn.close()


def select_all():
    conn = sqlite3.connect('query.db')

    cursor = conn.cursor()

    cursor.execute("""SELECT rowid, * FROM user_query""")
    conn.commit()
    conn.close()


def select_all_command_names():
    conn = sqlite3.connect('query.db')

    cursor = conn.cursor()

    cursor.execute("""SELECT rowid, * FROM command""")

    conn.commit()
    conn.close()


def show_history(user_id: int):
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


def populate_db():
    for i in range(100):
        user: int = randint(0, 10)
        q = add_query(user, choice(('lowprice', 'highprice', 'bestdeal')))
        for j in range(randint(0, 10)):
            add_hotel(q, f'hotel_description = {j}')
