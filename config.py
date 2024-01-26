import os

from aiogram import Bot
from dotenv import load_dotenv

load_dotenv()
# DATABASE_NAME = os.getenv('DATABASE_NAME')
DEBUG = bool(os.getenv('DEBUG'))
BOT_TOKEN = os.getenv('BOT_TOKEN')
BASE_NAME = os.getenv('BASE_NAME')
GROUP_ID = os.getenv('GROUP_ID')
LOGIN = GROUP_ID = os.getenv('LOGIN')
PASWORD = os.getenv('PASWORD')