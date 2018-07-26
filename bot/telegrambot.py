from django_telegrambot.apps import DjangoTelegramBot
from telegram import (KeyboardButton, ReplyKeyboardMarkup,
                      InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice,
                      ShippingOption)
from telegram.ext import (CommandHandler, MessageHandler,
                          Filters, CallbackQueryHandler, ShippingQueryHandler,
                          PreCheckoutQueryHandler)

from bot.models import Product, Order, OrderItem
from paymentbot.local_settings import PROVIDER_TOKEN

baskets = {}  # Корзина с товарами
COUNTER = 0

main_keyboard = ReplyKeyboardMarkup([
    [KeyboardButton('Меню')],
    [KeyboardButton('Корзина')],
],resize_keyboard=True)

basket_keyboard = ReplyKeyboardMarkup([
    [KeyboardButton('Оплатить')],
    [KeyboardButton('Меню')],
    [KeyboardButton('Очистить корзину')],
],resize_keyboard=True)


def clear_basket(bot, update, send_noitication=False):
    """
    Очистка корзины пользователя
    """
    chat_id = update.message.chat_id
    if chat_id in baskets:
        del baskets[chat_id]
    if send_noitication:
        update.message.reply_text('Корзина очищена.')



def start(bot, update):
    update.message.reply_text('Добро пожаловать!', reply_markup=main_keyboard)


def show_menu(bot, update):
    """
    Вывод списка товаров пользователю
    """
    chat_id = update.message.chat_id
    products = Product.objects.all()
    if products.exists():
        update.message.reply_text("Наше меню:",
                                  reply_markup=main_keyboard)
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
        update.message.reply_text('Товары еще не добавлены',
                                  reply_markup=main_keyboard)


def show_basket(bot, update):
    """
    Отображение товаров в корзине пользователя
    """
    chat_id = update.message.chat_id
    basket = baskets.get(chat_id)
    if basket is None:
        update.message.reply_text('Ваша корзина пуста')
    else:
        total_cost = 0
        text = '*В корзине:*\n'
        for count, (k, v) in enumerate(basket.items(), 1):
            product = Product.objects.get(id=k)
            item_cost = v * product.price
            total_cost += item_cost
            text += f'\n{count}. {product.name}\n' \
                    f'_{product.description}_\n' \
                    f'Цена: {v} x {product.price} = {item_cost}руб.\n'
        text += f'\n\n*Итого: {total_cost}руб.*'
        update.message.reply_text(text,
                                  reply_markup=basket_keyboard,
                                  parse_mode='Markdown')


def add_to_basket(bot, update):
    """
    Добавить товар в корзину пользователя
    """
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
    bot.edit_message_reply_markup(chat_id=query.message.chat_id,
                                  message_id=query.message.message_id,
                                  reply_markup=InlineKeyboardMarkup(keyboard))


def text_processing(bot, update):
    """
    Функция обработчик текствовых команд пользователя
    """
    text = update.message.text
    if text == 'Меню':
        show_menu(bot, update)
    elif text == 'Корзина':
        show_basket(bot, update)
    elif text == 'Оплатить':
        start_with_shipping_callback(bot, update)
    elif text == 'Очистить корзину':
        clear_basket(bot, update, send_noitication=True)


def start_with_shipping_callback(bot, update):
    """
    Функция создания счета на оплату заказа
    """
    chat_id = update.message.chat_id
    basket = baskets.get(chat_id)
    products = Product.objects.filter(id__in=basket.keys())
    title = "Оплата заказа"
    description = "Payment Example using python-telegram-bot"
    # select a payload just for you to recognize its the donation from your bot
    payload = "Custom-Payload"
    # In order to get a provider_token see https://core.telegram.org/bots/payments#getting-a-token
    provider_token = PROVIDER_TOKEN
    start_parameter = "test-payment"
    currency = "RUB"
    # price in rub
    price = 1
    # price * 100 so as to include 2 d.p.
    # check https://core.telegram.org/bots/payments#supported-currencies for more details
    prices = [LabeledPrice(f'{product.name} x {basket.get(product.id)}шт.',
                           int(product.price * 100 * basket.get(product.id)))
              for product in products]

    # optionally pass need_name=True, need_phone_number=True,
    # need_email=True, need_shipping_address=True, is_flexible=True
    bot.sendInvoice(chat_id, title, description, payload,
                    provider_token, start_parameter, currency, prices,
                    need_name=True, need_phone_number=True,
                    need_email=True, need_shipping_address=True)


def shipping_callback(bot, update):
    """
    Запрос адреса доставки
    """
    query = update.shipping_query
    # check the payload, is this from your bot?
    if query.invoice_payload != 'Custom-Payload':
        # answer False pre_checkout_query
        bot.answer_shipping_query(shipping_query_id=query.id, ok=False,
                                  error_message="Something went wrong...")
        return
    else:
        options = list()
        # a single LabeledPrice
        options.append(ShippingOption('1', 'Бесплатная доставка',
                                      [LabeledPrice('Стоимость доставки', 0)]))
        bot.answer_shipping_query(shipping_query_id=query.id, ok=True,
                                  shipping_options=options)


def precheckout_callback(bot, update):
    """
    Функция финального подтверждения платежа
    """
    query = update.pre_checkout_query
    # check the payload, is this from your bot?
    if query.invoice_payload != 'Custom-Payload':
        # answer False pre_checkout_query
        bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=False,
                                      error_message="Ошибка платежа...")
    else:
        bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=True)


def successful_payment_callback(bot, update):
    """
    Функция создания заказа в базе в случае успешной оплаты
    """
    update.message.reply_text("Спасибо за оплату!", reply_markup=main_keyboard)
    order_info = update.message.successful_payment.order_info
    order = Order.objects.create(
        client_name=order_info.name,
        phone=order_info.phone_number,
        email=order_info.email,
        address=order_info.shipping_address.street_line1,
        total_cost=update.message.successful_payment.total_amount / 100,
        is_paid=True
    )
    basket = baskets.get(update.message.chat_id)
    for k, v in basket.items():
        product = Product.objects.get(id=k)
        OrderItem.objects.create(
            order=order,
            product=product,
            count=v
        )
    clear_basket(bot, update)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    print('Update "%s" caused error "%s"', update, error)


def main():
    dp = DjangoTelegramBot.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(add_to_basket))
    dp.add_handler(MessageHandler(Filters.text, text_processing))

    # Optional handler if your product requires shipping
    dp.add_handler(ShippingQueryHandler(shipping_callback))

    # Pre-checkout handler to final check
    dp.add_handler(PreCheckoutQueryHandler(precheckout_callback))

    # Success! Notify your user!
    dp.add_handler(MessageHandler(Filters.successful_payment, successful_payment_callback))
    dp.add_error_handler(error)