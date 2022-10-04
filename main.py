from telebot.types import Message
import commands
from loader import bot
from states import UserState


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
        commands.help_command(message.chat, bot)

    elif message.text == '/lowprice':
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['command'] = 'lowprice'
        bot.set_state(message.from_user.id, UserState.check_in_date, message.chat.id)
        commands.common.check_in(message)

    elif message.text == '/bestdeal':
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['command'] = 'bestdeal'
        commands.common.check_in(message)

    elif message.text == '/highprice':
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['command'] = 'highprice'
        bot.set_state(message.from_user.id, UserState.check_in_date, message.chat.id)
        commands.common.check_in(message)

    elif message.text == '/history':
        pass

    else:
        bot.send_message(message.from_user.id,
                         "Неизвестная команда, попробуй написать /help, чтоб мы с тобой были на одной волне!:)")


bot.polling(none_stop=True, interval=0)
