import vk_api
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio
import sqlite3
import base
import parse
from config import *


# Создание объектов телеграм-бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Функция для получения постов из группы ВКонтакте
def get_vk_posts():
    vk_session = vk_api.VkApi(LOGIN, PASWORD)
    vk_session.auth()
    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        print(error_msg)
    vk = vk_session.get_api()
    
    # ВАШ_GROUP_ID - замените на ID группы, из которой хотите получать посты
    posts = vk.wall.get(owner_id=int(GROUP_ID), count=1)

    return posts

# Обработка команды /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await base.add_chat_id(message.chat.id)
    await message.reply("Привет! Я буду рассылать тебе посты из группы ВКонтакте.")

# Функция для рассылки поста пользователям
async def send_post_to_users(post):
    users = await base.get_all_chat_ids() 
    for user_id in users:
        await bot.send_message(chat_id=user_id, text=str(post))
        for name in post.jury:
            keyboard = types.InlineKeyboardMarkup(row_width=5)  # Создание объекта клавиатуры

            # Создание callback кнопок с числами от 1 до 10
            buttons = [types.InlineKeyboardButton(str(i), callback_data=f'{i}_{name}') for i in range(1, 11)]
            keyboard.add(*buttons)

            await bot.send_message(chat_id=user_id, text=str(post), reply_markup=keyboard)

# Обработчик callback кнопок
@dp.callback_query_handler(lambda c: True)
async def process_callback_button(callback_query: types.CallbackQuery):
    selected_number = callback_query.data.split('_')[0]
    await base.insert_row(callback_query.data.split('_')[1], int(callback_query.data.split('_')[0]))

    reply_markup = types.ReplyKeyboardRemove()  # Создание объекта для удаления клавиатуры

    await bot.send_message(
        callback_query.from_user.id,
        f"Вы выбрали число: {selected_number}",
        reply_markup=reply_markup
    )

    await callback_query.answer()


# Количество судей на одной странице
PER_PAGE = 10

# Функция для получения судей на определенной странице
def get_judges_page(judges, page):
    start_index = (page - 1) * PER_PAGE
    end_index = start_index + PER_PAGE
    return judges[start_index:end_index]

# Функция для форматирования статистики
def format_stat(judges):
    return '\n'.join([f'{judge[0]}: {judge[1]}' for judge in judges])

# Функция обработки команды /stat
@dp.message_handler(commands=['stat'])
async def stat(message: types.Message):
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    query = "SELECT name, AVG(score) FROM main GROUP BY name"
    cursor.execute(query)
    rows = cursor.fetchall()

    if not rows:
        await message.reply('Статистика пуста!')
        return

    # Создание списка судей
    judges = [(row[0], row[1]) for row in rows]

    # Сохранение списка судей в контексте
    context = dp.current_state(chat=message.chat.id, user=message.from_user.id)
    await context.update_data(judges=judges)

    # Извлечение первой страницы судей
    page = 1
    judges_page = get_judges_page(judges, page)
    stat_message = format_stat(judges_page)

    # Создание клавиатуры
    buttons = []
    if len(judges) > PER_PAGE:
        buttons.append(types.InlineKeyboardButton('Вперед', callback_data='next'))

    reply_markup = types.InlineKeyboardMarkup([[button] for button in buttons])

    # Отправка сообщения со статистикой и клавиатурой
    await message.reply(stat_message, reply_markup=reply_markup)

@dp.callback_query_handler()
async def inline_buttons_callback(callback_query: types.CallbackQuery):
    callback_data = callback_query.data

    if callback_data == 'next':
        await callback_query.answer('Переходим на следующую страницу...')

        # Получение контекста с сохраненными данными
        context = dp.current_state(chat=callback_query.message.chat.id, user=callback_query.from_user.id)
        data = await context.get_data()

        # Извлечение текущей страницы
        page = data.get('page', 1)

        # Получение списка судей
        judges = data.get('judges')

        # Переход на следующую страницу
        page += 1
        judges_page = get_judges_page(judges, page)

        if judges_page:
            stat_message = format_stat(judges_page)

            # Обновление сообщения со статистикой
            await bot.edit_message_text(
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                text=stat_message,
                reply_markup=get_keyboard(page, judges, len(judges))
            )
            await context.update_data(page=page)

        else:
            await bot.send_message(
                chat_id=callback_query.message.chat.id,
                text='Статистика закончилась!'
            )

    else:
         await callback_query.answer('Произошла ошибка!')

def get_keyboard(page, judges, total_judges):
    buttons = []
    if page > 1:
        buttons.append(types.InlineKeyboardButton('Назад', callback_data='prev'))
    if page * PER_PAGE < total_judges:
        buttons.append(types.InlineKeyboardButton('Вперед', callback_data='next'))

    return types.InlineKeyboardMarkup([[button] for button in buttons])

# Функция для запуска мониторинга постов из группы ВКонтакте
async def start_monitoring():
    while True:
        posts = get_vk_posts()
        
        if posts['items']:
            post = parse.data_for_url(posts['items'][0].split()[0])
            await send_post_to_users(post)
        
        # ВАШ_INTERVAL - замените на желаемый интервал мониторинга (например, 60 секунд)
        await asyncio.sleep(60)

async def on_startup(_):
    asyncio.ensure_future(start_monitoring())
    await base.create_table()
    await base.create_users_table()

# Запуск телеграм-бота
if __name__ == '__main__':
    executor.start_polling(dp, 
                           skip_updates=True,
                           on_startup=on_startup
                           )
