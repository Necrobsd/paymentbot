from django_telegrambot.apps import DjangoTelegramBot
from telegram import (KeyboardButton, ReplyKeyboardMarkup,
                      InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (CommandHandler, MessageHandler,
                          Filters, CallbackQueryHandler)

from bot.models import Product

baskets = {}  # Корзина с товарами
COUNTER = 0

main_keyboard = ReplyKeyboardMarkup([
    [KeyboardButton('Меню')],
    [KeyboardButton('Корзина')],
],resize_keyboard=True)


def start(bot, update):
    update.message.reply_text('Добро пожаловать!', reply_markup=main_keyboard)


def show_menu(bot, update):
    chat_id = update.message.chat_id
    products = Product.objects.all()
    if products.exists():
        for product in products:
            keyboard = [
                [InlineKeyboardButton("Добавить в корзину", callback_data=product.id)]
            ]
            bot.sendPhoto(
                chat_id,
                photo=open(product.image.path, 'rb'),
                caption=f'*{product.name}*\n_{product.description}_\n'
                        f'Цена: {product.price} руб.',
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    else:
        update.message.reply_text('Товары еще не добавлены')


def add_to_basket(bot, update):
    query = update.callback_query
    chat_id = query.message.chat_id
    product = Product.objects.get(id=query.data)
    basket = baskets.get(chat_id)
    if basket is not None:
        product_counter = basket.get(product.id, 0)
        product_counter += 1
        basket[product.id] = product_counter
        baskets[chat_id] = basket
    else:
        basket = {}
        product_counter = 1
        basket[product.id] = product_counter
        baskets[chat_id] = basket
    keyboard = [
        [InlineKeyboardButton(f"Добавить еще в корзину ({product_counter}шт)",
                              callback_data=product.id)]
    ]
    bot.edit_message_reply_markup(text="Добавлена в корзину",
                                  chat_id=query.message.chat_id,
                                  message_id=query.message.message_id,
                                  reply_markup=InlineKeyboardMarkup(keyboard))


def text_processing(bot, update):
    text = update.message.text
    if text == 'Меню':
        show_menu(bot, update)
    if text == 'Корзина':
        pass


def error(bot, update, error):
    """Log Errors caused by Updates."""
    print('Update "%s" caused error "%s"', update, error)


def main():
    dp = DjangoTelegramBot.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(add_to_basket))
    dp.add_handler(MessageHandler(Filters.text, text_processing))
    dp.add_error_handler(error)