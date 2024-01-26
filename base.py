import aiosqlite
from config import BASE_NAME

database_file =  BASE_NAME

# Функция для создания таблицы в базе данных
async def create_table():
    async with aiosqlite.connect(database_file) as conn:
        create_table_query = '''
            CREATE TABLE IF NOT EXISTS main (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                score INTEGER
            )
        '''
        await conn.execute(create_table_query)
        await conn.commit()

# Функция для добавления новой строки в базу данных
async def insert_row(name, score):
    async with aiosqlite.connect(database_file) as conn:
        insert_query = '''
            INSERT INTO main (name, score)
            VALUES (?, ?)
        '''
        await conn.execute(insert_query, (name, score))
        await conn.commit()

# Функция для вычисления среднего значения score по имени (name)
async def calculate_average_score_by_name(name):
    async with aiosqlite.connect(database_file) as conn:
        select_query = '''
            SELECT AVG(score) FROM main WHERE name = ?
        '''
        cursor = await conn.execute(select_query, (name,))
        result = await cursor.fetchone()
        return result[0]
    
# Функция для создания таблицы "users", если она не существует
async def create_users_table():
    async with aiosqlite.connect(database_file) as conn:
        create_table_query = '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER
            )
        '''
        await conn.execute(create_table_query)
        await conn.commit()

# Функция для добавления нового значения "chat_id" в таблицу "users" (если его там нет)
async def add_chat_id(chat_id):
    async with aiosqlite.connect(database_file) as conn:
        query = '''
            INSERT INTO users (chat_id)
            SELECT :chat_id
            WHERE NOT EXISTS (
                SELECT 1 FROM users WHERE chat_id = :chat_id
            )
        '''
        await conn.execute(query, {"chat_id": chat_id})
        await conn.commit()

# Функция для получения списка всех "chat_id" из таблицы "users"
async def get_all_chat_ids():
    async with aiosqlite.connect(database_file) as conn:
        query = '''
            SELECT chat_id FROM users
        '''
        cursor = await conn.execute(query)
        result = await cursor.fetchall()
        chat_ids = [record[0] for record in result]
        return chat_ids
