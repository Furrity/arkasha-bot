from loader import bot
from database import db_worker
from datetime import datetime


def send_history(user_id: int):
    user_history_list: list = db_worker.show_history(user_id)
    for query in user_history_list:

        message: str = ''
        message += 'Команда: ' + query[0] + '\n\n'
        message += 'Время вызова команды: ' + str(datetime.fromtimestamp(query[1])) + '\n\n'
        if query[2]:
            message += "Отель:\n" + query[2]

        bot.send_message(user_id, message)
    db_worker.add_query(user_id, command='history')
