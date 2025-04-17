import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

TOKEN = "7932212502:AAF-oHrU0sQNXEL33IGY_oWadLmtgzBVoc0"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

user_data = {}

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Привет! Введи ник своего Minecraft-бота:")
    user_data[message.from_user.id] = {}

@dp.message_handler(lambda msg: msg.from_user.id in user_data and "nickname" not in user_data[msg.from_user.id])
async def get_nick(message: types.Message):
    user_data[message.from_user.id]["nickname"] = message.text
    await message.answer("Теперь выбери под-сервер:\n1. Скайблок Фермер\n2. Скайблок Лудоман\n3. Скайблок Генератор+")

@dp.message_handler(lambda msg: msg.from_user.id in user_data and "server" not in user_data[msg.from_user.id])
async def get_server(message: types.Message):
    choice = message.text.strip().lower()
    if choice == "1" or "фермер" in choice:
        user_data[message.from_user.id]["server"] = 11
    elif choice == "2" or "лудоман" in choice:
        user_data[message.from_user.id]["server"] = 13
    elif choice == "3" or "генератор+" in choice:
        user_data[message.from_user.id]["server"] = 15
    else:
        await message.answer("Некорректный выбор. Попробуй снова.")
        return
    
    await message.answer("Теперь введи координаты X Y Z (через пробел):")

@dp.message_handler(lambda msg: msg.from_user.id in user_data and "pos" not in user_data[msg.from_user.id])
async def get_coords(message: types.Message):
    try:
        x, y, z = map(float, message.text.split())
        user_data[message.from_user.id]["pos"] = {"x": x, "y": y, "z": z}
        await message.answer("Теперь введи yaw и pitch (углы камеры, через пробел):")
    except:
        await message.answer("Некорректный формат. Введи X Y Z через пробел.")

@dp.message_handler(lambda msg: msg.from_user.id in user_data and "look" not in user_data[msg.from_user.id])
async def get_angles(message: types.Message):
    try:
        yaw, pitch = map(float, message.text.split())
        user_data[message.from_user.id]["look"] = {"yaw": yaw, "pitch": pitch}

        # Сохраняем в файл (пока для теста)
        with open(f"data_{message.from_user.id}.json", "w") as f:
            json.dump(user_data[message.from_user.id], f, indent=2)

        kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton("Запустить бота", callback_data="start_bot")
        )
        await message.answer("Настройки сохранены. Запустить бота?", reply_markup=kb)

    except:
        await message.answer("Некорректный формат. Введи yaw pitch через пробел.")

@dp.callback_query_handler(lambda c: c.data == "start_bot")
async def launch_bot(callback: types.CallbackQuery):
    uid = callback.from_user.id
    with open(f"data_{uid}.json") as f:
        config = json.load(f)

    # Здесь запускается Node.js бот
    import subprocess
    subprocess.Popen(["node", "bot.js", f"data_{uid}.json"])

    await callback.message.answer("Бот запускается и станет в нужную точку. Ожидай подтверждение...")

if __name__ == "__main__":
    executor.start_polling(dp)
