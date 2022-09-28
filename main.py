from telebot.types import Message
import commands
from loader import bot
from states import Lowprice


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
        bot.set_state(message.from_user.id, Lowprice.check_in_date, message.chat.id)
        commands.lowprice.check_in(message)

    elif message.text == '/bestdeal':
        pass

    elif message.text == '/highprice':
        pass

    elif message.text == '/history':
        pass

    else:
        bot.send_message(message.from_user.id,
                         "Неизвестная команда, попробуй написать /help, чтоб мы с тобой были на одной волне!:)")


bot.polling(none_stop=True, interval=0)
