import telebot
from decouple import config
from telebot.types import Message
from help_command import help_command


SECRET_KEY = config("SECRET_KEY")
bot = telebot.TeleBot(SECRET_KEY)


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
        help_command(message.chat, bot)

    elif message.text == '/lowprice':
        pass

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
