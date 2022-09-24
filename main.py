from telebot.types import Message
import commands
from loader import bot
from states import Lowprice


@bot.message_handler(content_types=['text'])
def get_text_messages(message: Message):
    if message.text.lower() == 'привет' or message.text == '/hello-world':
        bot.send_message(message.from_user.id, "That's a hello-world message for beginning of a project "
                                               "that is about to happen.")
    if message.text == '/help':
        pass

    if message.text == '/lowprice':
        bot.set_state(message.from_user.id, Lowprice.check_in_date, message.chat.id)
        commands.lowprice.check_in(message)

    if message.text == '/bestdeal':
        pass

    if message.text == '/highprice':
        pass

    if message.text == '/history':
        pass


bot.polling(none_stop=True, interval=0)
