from telebot.types import Message
import commands
from loader import bot


@bot.message_handler(content_types=['text'])
def get_text_messages(message: Message):
    if message.text.lower() == 'привет' or message.text == '/hello-world':
        bot.send_message(message.from_user.id, "That's a hello-world message for beginning of a project "
                                               "that is about to happen.")
    if message.text == '/help':
        pass

    if message.text == '/lowprice':
        commands.lowprice_command(message, bot)

    if message.text == '/bestdeal':
        pass

    if message.text == '/highprice':
        pass

    if message.text == '/history':
        pass


bot.polling(none_stop=True, interval=0)
