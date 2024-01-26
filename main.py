import vk_api
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio
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
