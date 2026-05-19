import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from states import Feedback
from keyboards import start_kb
from db import init_db, save_review

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

@dp.message_handler(commands="start")
async def start(message: types.Message):
    await message.answer("Откуда вы?", reply_markup=start_kb)
    await Feedback.source.set()

@dp.message_handler(state=Feedback.source)
async def get_source(message: types.Message, state: FSMContext):
if "Гостиница" in message.text:
    source = "Гостиница"
elif "Лофт" in message.text:
    source = "Лофт"
else:
    return await message.answer("Выберите вариант с кнопок")

await state.update_data(source=source)

    await state.update_data(source=message.text)
    await message.answer("Введите дату события:")
    await Feedback.next()

@dp.message_handler(state=Feedback.date)
async def get_date(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text)
    await message.answer("Напишите ваш отзыв:")
    await Feedback.next()

@dp.message_handler(state=Feedback.review)
async def get_review(message: types.Message, state: FSMContext):
    await state.update_data(review=message.text)
    await message.answer("Ваш контакт (или '-' чтобы пропустить):")
    await Feedback.next()

@dp.message_handler(state=Feedback.contact)
async def get_contact(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text)

    data = await state.get_data()

    save_review(
        user_id=message.from_user.id,
        source=data["source"],
        date=data["date"],
        review=data["review"],
        contact=data["contact"]
    )

    text = f"""
📩 Новый отзыв

Источник: {data['source']}
Дата: {data['date']}
Отзыв: {data['review']}
Контакт: {data['contact']}
"""

    await bot.send_message(ADMIN_ID, text)
    await message.answer("Спасибо! 🙌")

    await state.finish()

if __name__ == "__main__":
    init_db()
    executor.start_polling(dp, skip_updates=True)
