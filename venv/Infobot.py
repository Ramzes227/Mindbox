import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
import requests
import datetime
import psycopg2
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage


class UserState(StatesGroup):
    hour = State()
    minute = State()


url = 'https://www.cbr.ru/currency_base/daily/'
url_cbr = 'https://www.cbr.ru/'
my_chat_id = 536155973


def get_html(url):
    response = requests.get(url)
    data = response.text
    return data


def get_currencies(data):
    data1 = data.split('<h2 class="h3">	')[1]
    data2 = data1.split('</tbody>')[0]
    data3 = data2.split('<tr>')
    data4 = data3[2:]
    counter, result, final = 1, [], []
    for i in range(len(data4)):
        data4[i] = data4[i].replace('\r\n', '').strip().replace('<td>', '').replace('</td>', '').replace('</tr>', '')
        for j in data4[i].split('          '):
            result.append(j.strip())
    result = list(filter(lambda x: (result.index(x) + 1) % 5 == 3 or (result.index(x) + 1) % 5 == 4 or (result.index(x) + 1) % 5 == 0, result))
    for i in range(len(result) // 3):
        final.append(f'{result[i*3]} {result[i*3+1]} - {result[i*3+2]}RUB')
    return final


def get_news(final):
    usd, euro = final[13], final[14]
    return f'{usd}\n{euro}'


def find_key(data):
    key = data.split('<div class="main-indicator_value">')
    key = key[3][:6]
    return key


def hours(hour):
    result = ''
    if hour == 1 or hour == 21:
        result = f"{hour} час"
    elif hour % 20 == 2 or hour % 20 == 3 or hour == 4:
        result = f"{hour} часа"
    else:
        result = f"{hour} часов"
    return result


def minutes(minute):
    result = ''
    if minute % 10 == 1 and minute != 11:
        result = f"{minute} минута"
    elif (minute % 10 == 2 or minute % 10 == 3 or minute % 10 == 4) \
            and (minute != 12 and minute != 13 and minute != 14):
        result = f"{minute} минуты"
    else:
        result = f"{minute} минут"
    return result


# Укажите здесь токен вашего бота от BotFather
TOKEN = "6220162302:AAFkW7L3dlN9RJrhOqbpRorYBA4gLdV7N5M"

# Инициализируем бота и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Включаем логирование, чтобы видеть информацию об ошибках
logging.basicConfig(level=logging.INFO)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    username = message.from_user.username
    chat_id = message.chat.id

    # Подключаемся к базе данных
    connection = psycopg2.connect(
        database="Users",
        user="postgres",
        password="905509401501",
        host="localhost",
        port="5432"
    )
    cursor = connection.cursor()

    # Проверяем наличие чата в таблице users
    cursor.execute("SELECT COUNT(*) FROM users WHERE chat_id = %s;", (chat_id,))
    user_count = cursor.fetchone()[0]

    if user_count == 0:
        # Вставляем данные в таблицу users
        cursor.execute("INSERT INTO users (username, chat_id, turn_on, hour, minute) VALUES (%s, %s, false, 0, 0);", (username, chat_id))

        # Вставляем данные в таблицу options с значениями по умолчанию (false)
        cursor.execute("INSERT INTO options (chat_id, usd, euro, yen, yuan, gbp, kron, ten) VALUES (%s, false, false, false, false, false, false, false);", (chat_id,))

    connection.commit()
    cursor.close()
    connection.close()

    await message.answer('Приветствуем вас в нашем боте!\n'
                         'При помощи данного бота вы можете настроить получение\n'
                         'необходимой для вас информации в определенное время\n'
                         'Чтобы посмотреть полный список команд, введите /help')


@dp.message_handler(commands=['help'])
async def start(message: types.Message):
    await message.answer('/turn_on - Включить бота\n'
                         '/turn_off - Выключить бота\n'
                         '/set_time - Установить время получения сообщения\n'
                         '/options - Выбор опций для отправки\n'
                         '/settings - Узнать о текущих настройках бота')


@dp.message_handler(commands=['turn_on'])
async def start(message: types.Message):
    # Подключаемся к базе данных и выполняем запрос на добавление
    connection = psycopg2.connect(
        database="Users",
        user="postgres",
        password="905509401501",
        host="localhost",
        port="5432"
    )
    cursor = connection.cursor()
    chat_id = message.chat.id
    # Получаем текущее значение столбца turn_on
    cursor.execute("SELECT turn_on FROM users WHERE chat_id = %s;", (chat_id,))
    result = cursor.fetchone()

    # Проверяем текущее значение и выполняем соответствующее действие
    if result and result[0]:  # Если result не None и значение True
        await bot.send_message(chat_id, "Бот уже запущен")
    else:
        # Обновляем значение столбца turn_on на True
        cursor.execute("UPDATE users SET turn_on = true WHERE chat_id = %s;", (chat_id,))
        connection.commit()
        await bot.send_message(chat_id, "Бот успешно запущен")
    cursor.close()
    connection.close()


@dp.message_handler(commands=['turn_off'])
async def start(message: types.Message):
    # Подключаемся к базе данных и выполняем запрос на добавление
    connection = psycopg2.connect(
        database="Users",
        user="postgres",
        password="905509401501",
        host="localhost",
        port="5432"
    )
    cursor = connection.cursor()
    chat_id = message.chat.id
    # Получаем текущее значение столбца turn_on
    cursor.execute("SELECT turn_on FROM users WHERE chat_id = %s;", (chat_id,))
    result = cursor.fetchone()

    # Проверяем текущее значение и выполняем соответствующее действие
    if result and result[0]:  # Если result не None и значение True
        cursor.execute("UPDATE users SET turn_on = false WHERE chat_id = %s;", (chat_id,))
        connection.commit()
        await bot.send_message(chat_id, "Бот успешно отключен")
    else:
        # Обновляем значение столбца turn_on на True
        await bot.send_message(chat_id, "Бот уже отключен")
    cursor.close()
    connection.close()


@dp.message_handler(commands=['set_time'])
async def set_time(message: types.Message):
    chat_id = message.chat.id
    await bot.send_message(chat_id, "Введите час получения информации (от 0 до 24):")
    await UserState.hour.set()


@dp.message_handler(state=UserState.hour)
async def set_hour(message: types.Message, state: FSMContext):
    try:
        hour = int(message.text)
        if 0 <= hour < 24:
            await state.update_data(username_hour=hour)
            await message.answer("Отлично, теперь введите минуты (от 0 до 60)")
            await UserState.minute.set()
        else:
            await message.answer("Неверное значение часа. Введите значение от 0 до 24:")
    except ValueError:
        await message.answer("Неверный формат числа. Введите корректное значение (от 0 до 24):")


@dp.message_handler(state=UserState.minute)
async def set_minute(message: types.Message, state: FSMContext):
    try:
        minute = int(message.text)
        if 0 <= minute <= 59:
            await state.update_data(username_minute=minute)
            await message.answer("Значения успешно установлены")
            user_data = await state.get_data()
            username_hour = user_data.get('username_hour', 0)
            username_minute = user_data.get('username_minute', 0)
            # Подключение к базе данных и выполнение запроса на обновление
            connection = psycopg2.connect(
                database="Users",
                user="postgres",
                password="905509401501",
                host="localhost",
                port="5432"
            )
            cursor = connection.cursor()
            cursor.execute("UPDATE users SET hour = %s, minute = %s WHERE chat_id = %s;",
                           (username_hour, username_minute, message.chat.id))
            connection.commit()
            connection.close()
            cursor.close()
        else:
            await message.answer("Неверное значение minute. Введите значение от 0 до 59:")
    except ValueError:
        await message.answer("Неверный формат числа. Введите корректное значение minute (от 0 до 59):")
    finally:
        await state.finish()


@dp.message_handler(commands=['options'])
async def options(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    button_currencies = types.InlineKeyboardButton('Курсы валют', callback_data='currencies')
    button_key_rate = types.InlineKeyboardButton('Ключевая ставка ЦБ', callback_data='key_rate')
    chat_id = message.chat.id
    markup.row(button_currencies, button_key_rate)
    await bot.send_message(chat_id, "Выберите желаемые опции:", reply_markup=markup)


@dp.callback_query_handler(lambda call: True)
async def callback_worker(call):
    chat_id = call.message.chat.id
    markup = types.InlineKeyboardMarkup()

    if call.data == 'currencies':
        button_currencies_usd = types.InlineKeyboardButton('Доллар', callback_data='usd')
        button_currencies_euro = types.InlineKeyboardButton('Евро', callback_data='euro')
        button_currencies_yen = types.InlineKeyboardButton('Йена', callback_data='yen')
        button_currencies_yuan = types.InlineKeyboardButton('Юань', callback_data='yuan')
        button_currencies_gbp = types.InlineKeyboardButton('Фунт стерлингов', callback_data='gbp')
        button_currencies_kron = types.InlineKeyboardButton('Крона', callback_data='kron')
        button_currencies_ten = types.InlineKeyboardButton('Тенге', callback_data='ten')
        markup.row(button_currencies_usd, button_currencies_euro)
        markup.row(button_currencies_gbp, button_currencies_kron)
        markup.row(button_currencies_yen, button_currencies_yuan, button_currencies_ten)
        await bot.send_message(chat_id, "Выберите предпочитаемую валюту", reply_markup=markup)

    elif call.data == 'usd':
        connection = psycopg2.connect(
            database="Users",
            user="postgres",
            password="905509401501",
            host="localhost",
            port="5432"
        )
        cursor = connection.cursor()
        cursor.execute("SELECT usd FROM options;")
        usd = cursor.fetchall()
        if usd and usd[0][0]:  # Если result не None и значение True
            cursor.execute("UPDATE options SET usd = false WHERE chat_id = %s;", (chat_id,))
            connection.commit()
            await bot.send_message(chat_id, "Отправка информации по курсу доллара отменена")
        else:
            # Обновляем значение столбца turn_on на True
            cursor.execute("UPDATE options SET usd = true WHERE chat_id = %s;", (chat_id,))
            connection.commit()
            await bot.send_message(chat_id, "Отправка информации по курсу доллара включена")
        connection.close()
        cursor.close()

    elif call.data == 'euro':
        connection = psycopg2.connect(
            database="Users",
            user="postgres",
            password="905509401501",
            host="localhost",
            port="5432"
        )
        cursor = connection.cursor()
        cursor.execute("SELECT euro FROM options;")
        euro = cursor.fetchall()
        if euro and euro[0][0]:  # Если result не None и значение True
            cursor.execute("UPDATE options SET euro = false WHERE chat_id = %s;", (chat_id,))
            connection.commit()
            await bot.send_message(chat_id, "Отправка информации по курсу евро отменена")
        else:
            # Обновляем значение столбца turn_on на True
            cursor.execute("UPDATE options SET euro = true WHERE chat_id = %s;", (chat_id,))
            connection.commit()
            await bot.send_message(chat_id, "Отправка информации по курсу евро включена")
        connection.close()
        cursor.close()

    elif call.data == 'yen':
        connection = psycopg2.connect(
            database="Users",
            user="postgres",
            password="905509401501",
            host="localhost",
            port="5432"
        )
        cursor = connection.cursor()
        cursor.execute("SELECT yen FROM options;")
        yen = cursor.fetchall()
        if yen and yen[0][0]:  # Если result не None и значение True
            cursor.execute("UPDATE options SET yen = false WHERE chat_id = %s;", (chat_id,))
            connection.commit()
            await bot.send_message(chat_id, "Отправка информации по курсу йены отменена")
        else:
            # Обновляем значение столбца turn_on на True
            cursor.execute("UPDATE options SET yen = true WHERE chat_id = %s;", (chat_id,))
            connection.commit()
            await bot.send_message(chat_id, "Отправка информации по курсу йены включена")
        connection.close()
        cursor.close()

    elif call.data == 'yuan':
        connection = psycopg2.connect(
            database="Users",
            user="postgres",
            password="905509401501",
            host="localhost",
            port="5432"
        )
        cursor = connection.cursor()
        cursor.execute("SELECT yuan FROM options;")
        yuan = cursor.fetchall()
        if yuan and yuan[0][0]:  # Если result не None и значение True
            cursor.execute("UPDATE options SET yuan = false WHERE chat_id = %s;", (chat_id,))
            connection.commit()
            await bot.send_message(chat_id, "Отправка информации по курсу юаня отменена")
        else:
            # Обновляем значение столбца turn_on на True
            cursor.execute("UPDATE options SET yuan = true WHERE chat_id = %s;", (chat_id,))
            connection.commit()
            await bot.send_message(chat_id, "Отправка информации по курсу юаня включена")
        connection.close()
        cursor.close()

    elif call.data == 'gbp':
        connection = psycopg2.connect(
            database="Users",
            user="postgres",
            password="905509401501",
            host="localhost",
            port="5432"
        )
        cursor = connection.cursor()
        cursor.execute("SELECT gbp FROM options;")
        gbp = cursor.fetchall()
        if gbp and gbp[0][0]:  # Если result не None и значение True
            cursor.execute("UPDATE options SET gbp = false WHERE chat_id = %s;", (chat_id,))
            connection.commit()
            await bot.send_message(chat_id, "Отправка информации по курсу фунта стерлинга отменена")
        else:
            # Обновляем значение столбца turn_on на True
            cursor.execute("UPDATE options SET gbp = true WHERE chat_id = %s;", (chat_id,))
            connection.commit()
            await bot.send_message(chat_id, "Отправка информации по курсу фунта стерлинга включена")
        connection.close()
        cursor.close()

    elif call.data == 'kron':
        connection = psycopg2.connect(
            database="Users",
            user="postgres",
            password="905509401501",
            host="localhost",
            port="5432"
        )
        cursor = connection.cursor()
        cursor.execute("SELECT kron FROM options;")
        kron = cursor.fetchall()
        if kron and kron[0][0]:  # Если result не None и значение True
            cursor.execute("UPDATE options SET kron = false WHERE chat_id = %s;", (chat_id,))
            connection.commit()
            await bot.send_message(chat_id, "Отправка информации по курсу кроны отменена")
        else:
            # Обновляем значение столбца turn_on на True
            cursor.execute("UPDATE options SET kron = true WHERE chat_id = %s;", (chat_id,))
            connection.commit()
            await bot.send_message(chat_id, "Отправка информации по курсу кроны включена")
        connection.close()
        cursor.close()

    elif call.data == 'ten':
        connection = psycopg2.connect(
            database="Users",
            user="postgres",
            password="905509401501",
            host="localhost",
            port="5432"
        )
        cursor = connection.cursor()
        cursor.execute("SELECT ten FROM options;")
        ten = cursor.fetchall()
        if ten and ten[0][0]:  # Если result не None и значение True
            cursor.execute("UPDATE options SET ten = false WHERE chat_id = %s;", (chat_id,))
            connection.commit()
            await bot.send_message(chat_id, "Отправка информации по курсу тенге отменена")
        else:
            # Обновляем значение столбца turn_on на True
            cursor.execute("UPDATE options SET ten = true WHERE chat_id = %s;", (chat_id,))
            connection.commit()
            await bot.send_message(chat_id, "Отправка информации по курсу тенге включена")
        connection.close()
        cursor.close()


@dp.message_handler(commands=['settings'])
async def start(message: types.Message):
    # Подключаемся к базе данных и выполняем запрос на добавление
    connection = psycopg2.connect(
        database="Users",
        user="postgres",
        password="905509401501",
        host="localhost",
        port="5432"
    )
    cursor = connection.cursor()
    chat_id = message.chat.id
    options = ["Курс доллара", "Курс евро", "Курс йен", "Курс юаня", "Курс фунта стерлингов", "Курс кроны",
               "Курс тенге"]
    cursor.execute("SELECT * FROM users WHERE chat_id = %s;", (chat_id,))
    user = cursor.fetchone()
    cursor.execute("SELECT * FROM options WHERE chat_id = %s;", (chat_id,))
    user_options = cursor.fetchone()[2:]
    awaited_options = ""
    for option, enabled in zip(options, user_options):
        if enabled:
            awaited_options += option + "\n"
    if user[3]:
        await bot.send_message(chat_id,
                               f"Бот включен\nВремя отправки сообщений - {hours(user[4])} {minutes(user[5])}\n"
                               f"Вами были выбраны следующие опции:\n"
                               f"{awaited_options}")
    else:
        await bot.send_message(chat_id,
                               f"Бот выключен\nВремя отправки сообщений - {hours(user[4])} {minutes(user[5])}\n"
                               f"Вами были выбраны следующие опции:"
                               f"{awaited_options}")
    cursor.close()
    connection.close()


async def send_info():
    while True:
        time_now = datetime.datetime.now()
        current_hour, current_minute = time_now.hour, time_now.minute

        # Подключение к базе данных и получение данных
        connection = psycopg2.connect(
            database="Users",
            user="postgres",
            password="905509401501",
            host="localhost",
            port="5432"
        )
        cursor = connection.cursor()

        # Получение данных из базы данных (замените на ваш запрос)
        cursor.execute("SELECT chat_id, hour, minute FROM users;")
        records = cursor.fetchall()

        for record in records:
            id, db_hour, db_minute = record

            if current_hour == db_hour and current_minute == db_minute:
                # Выполните необходимые действия, например, отправьте сообщение
                message_text = f'{get_news(get_currencies(get_html(url)))}\nКлючевая ставка ЦБ - {find_key(get_html(url_cbr))}'
                print("Sending message...")
                await bot.send_message(chat_id=id, text=message_text)

        connection.close()
        await asyncio.sleep(60)

# Запуск бота с асинхронной обработкой
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(send_info())  # Запускаем асинхронную задачу
    executor.start_polling(dp, skip_updates=True)
