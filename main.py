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
            buttons = [types.InlineKeyboardButton(str(i), callback_data=f'score_{i}_{name}') for i in range(1, 11)]
            keyboard.add(*buttons)

            await bot.send_message(chat_id=user_id, text=str(post), reply_markup=keyboard)

# Обработчик callback кнопок
@dp.callback_query_handler(lambda c: c.data.split('_')[0] == 'score')
async def process_callback_button(callback_query: types.CallbackQuery):
    selected_number = callback_query.data.split('_')[1]
    await base.insert_row(callback_query.data.split('_')[2], int(callback_query.data.split('_')[1]))

    reply_markup = types.ReplyKeyboardRemove()  # Создание объекта для удаления клавиатуры

    await bot.send_message(
        callback_query.from_user.id,
        f"Вы выбрали число: {selected_number}",
        reply_markup=reply_markup
    )

    await callback_query.answer()

# Обработчик callback кнопок
@dp.callback_query_handler(lambda c: c.data.split('_')[0] == 'page')
async def process_callback_button_page(callback: types.CallbackQuery):
    index = int(callback.data.split('_')[1])
    await callback.answer(f'Страница {index + 1}')
    await send_page(callback.message, index)

# Количество судей на одной странице
PER_PAGE = 10

# Функция для форматирования статистики
def format_stat(judges):
    return '\n'.join([f'{judge[0]}: {judge[1]}' for judge in judges])

async def send_page(message, index):
    rows = await base.get_stat_from_db()
    if not rows:
        await message.reply('Статистика пуста!')
        return
    len_pages = len(rows) // PER_PAGE 
    if len(rows) % PER_PAGE > 0:
        len_pages += 1
    state = rows[index * PER_PAGE: (index + 1) * PER_PAGE]
    buttonprev = types.InlineKeyboardButton('prev', callback_data=f'page_{index - 1}')
    buttonnext = types.InlineKeyboardButton('next', callback_data=f'page_{index + 1}')

    # Создание клавиатуры
    if index > 0 and index < len_pages - 1:
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(buttonprev, buttonnext)
    elif index > 0:
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(buttonprev)
    elif index < len_pages - 1:
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(buttonnext)
    else:
        keyboard = None
    # Отправка сообщения с клавиатурой
    # await message.reply(format_stat(state), reply_markup=keyboard)
    await bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=format_stat(state), reply_markup=keyboard)
        
# Функция обработки команды /stat
@dp.message_handler(commands=['stat'])
async def stat(message: types.Message):
    message = await bot.send_message(chat_id=message.chat.id, text="Собираю статистику")
    await send_page(message, 0)

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
    # asyncio.ensure_future(start_monitoring())
    await base.create_table()
    await base.create_users_table()
    # for i in range(11):
    #     for j in 'fghjghjkghjhgkjhgjkgjkhgjghjkghjghkjgjkhgkhjgkjhgkjhgkjgjkhgtyiuysttbvxzxxcvqwtytyuiopmnbvbnbvdjfgasagcvbzaqwertyuiopasdfghjklzxcvbnm':
    #         await base.insert_row(j, i)
    print('finish start')

# Запуск телеграм-бота
if __name__ == '__main__':
    executor.start_polling(dp, 
                           skip_updates=True,
                           on_startup=on_startup
                           )
