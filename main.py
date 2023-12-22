from datetime import datetime
import telebot

BOT_TOKEN = '6852512731:AAErzbgrNKWkqFhybZ8cfV12isM56CouLnk'

bot = telebot.TeleBot(BOT_TOKEN)

# Словарь для хранения данных о заказах пользователей
orders_data = {}



# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'Здравствуйте! Для заказа введите /order.')


@bot.message_handler(commands=['order'])
def order(message):
    user_id = message.from_user.id
    bot.reply_to(message, 'Для начала, введите дату доставки (в формате ДД.ММ.ГГГГ):')
    # в процессе заказа
    orders_data[user_id] = {'step': 'date'}


# Обработчик текстовых сообщений (принимаем дату)
@bot.message_handler(
    func=lambda message: message.text and orders_data.get(message.from_user.id) and orders_data[message.from_user.id][
        'step'] == 'date')
def handle_date(message):
    try:
        date = datetime.strptime(message.text, '%d.%m.%Y')
        # Сохраняем дату в данных о заказе
        user_id = message.from_user.id
        orders_data[user_id]['date'] = date.strftime('%d.%m.%Y')
        # запрос адреса
        orders_data[user_id]['step'] = 'address'
        bot.reply_to(message, 'Отлично! Теперь введите адрес доставки:')
    except ValueError:
        bot.reply_to(message, 'Некорректный формат даты. Введите дату в формате ДД.ММ.ГГГГ.')


# Обработчик текстовых сообщений (принимаем адрес)
@bot.message_handler(
    func=lambda message: message.text and orders_data.get(message.from_user.id) and orders_data[message.from_user.id][
        'step'] == 'address')
def handle_address(message):
    # Сохраняем адрес в данных о заказе
    user_id = message.from_user.id
    orders_data[user_id]['address'] = message.text
    # запрос номера телефона
    orders_data[user_id]['step'] = 'phone'
    bot.reply_to(message, 'Хорошо! Теперь введите номер телефона для связи (в формате +996):')


# Обработчик текстовых сообщений (принимаем номер телефона)
@bot.message_handler(
    func=lambda message: message.text and orders_data.get(message.from_user.id) and orders_data[message.from_user.id][
        'step'] == 'phone')
def handle_phone(message):
    # Сохраняем номер телефона в данных о заказе
    user_id = message.from_user.id
    orders_data[user_id]['phone'] = message.text
    # запрос описания торта
    orders_data[user_id]['step'] = 'description'
    bot.reply_to(message, 'Отлично! Теперь введите описание торта или прикрепите фотографию (если есть):')


# Обработчик текстовых сообщений (принимаем описание торта)
@bot.message_handler(
    func=lambda message: (message.text or message.photo) and orders_data.get(message.from_user.id) and
                         orders_data[message.from_user.id][
                             'step'] == 'description')
def handle_description(message):
    # Сохраняем описание торта в данных о заказе
    user_id = message.from_user.id
    orders_data[user_id]['description'] = message.text
    # Здесь можно было б обработать фотографию

    # Подтверждение заказа и вывод информации
    orders_data[user_id]['step'] = 'confirmation'
    bot.reply_to(message, f'Дата доставки: {orders_data[user_id]["date"]}\n'
                          f'Адрес доставки: {orders_data[user_id]["address"]}\n'
                          f'Номер телефона: {orders_data[user_id]["phone"]}\n'
                          f'Описание торта: {orders_data[user_id]["description"]}\n\n'
                          f'Подтвердите заказ /confirm.')


# Обработчик команды /confirm
@bot.message_handler(commands=['confirm'])
def confirm_order(message):
    user_id = message.from_user.id
    if user_id in orders_data and orders_data[user_id].get('step') == 'confirmation':
        bot.reply_to(message, 'Ваш заказ подтвержден!')
        # Сбрасываем состояние пользователя после подтверждения заказа
        del orders_data[user_id]
    else:
        bot.reply_to(message, 'Нет активного заказа для подтверждения. Начните заказ снова /order.')


# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)
