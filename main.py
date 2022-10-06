from telebot.types import Message
import commands
from loader import bot
from states import UserState
import database


@bot.message_handler(content_types=['text'])
def get_text_messages(message: Message):
    if message.text.lower() == 'привет' or message.text == '/hello-world':
        bot.send_message(message.from_user.id, "That's a hello-world message for beginning of a project "
                                               "that is about to happen.")

    elif message.text == '/start':
        bot.send_message(message.from_user.id,
                         'Привет! Я Аркаша. Я люблю путешествовать и знаю много отелей, если тебе интересно, '
                         'то давай найдем тебе отельчик:)\nНапиши /help, чтобы познакомиться с доступными командами.')

    elif message.text == '/help':
        database.db_worker.add_query(message.from_user.id, 'help')
        commands.help_command(message.chat, bot)

    elif message.text == '/lowprice':
        bot.set_state(message.from_user.id, UserState.check_in_date)
        request_id = database.db_worker.add_query(message.from_user.id, 'lowprice')
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['command'] = 'lowprice'
            data['db_request_id'] = request_id
        commands.common.check_in(message)

    elif message.text == '/bestdeal':
        bot.set_state(message.from_user.id, UserState.check_in_date, message.chat.id)
        request_id = database.db_worker.add_query(message.from_user.id, 'bestdeal')

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['command'] = 'bestdeal'
            data['db_request_id'] = request_id

        commands.common.check_in(message)

    elif message.text == '/highprice':
        bot.set_state(message.from_user.id, UserState.check_in_date, message.chat.id)
        request_id = database.db_worker.add_query(message.from_user.id, 'highprice')
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['command'] = 'highprice'
            data['db_request_id'] = request_id

        bot.set_state(message.from_user.id, UserState.check_in_date, message.chat.id)
        commands.common.check_in(message)

    elif message.text == '/history':
        commands.history.send_history(message.from_user.id)

    else:
        bot.send_message(message.from_user.id,
                         "Неизвестная команда, попробуй написать /help, чтоб мы с тобой были на одной волне!:)")


bot.polling(none_stop=True, interval=0)
