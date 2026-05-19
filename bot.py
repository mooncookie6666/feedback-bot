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


# --- START ---
@dp.message_handler(commands="start", state="*")
async def start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Откуда вы?", reply_markup=start_kb)
    await Feedback.source.set()


# --- CANCEL ---
@dp.message_handler(commands="cancel", state="*")
async def cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Диалог сброшен. Напишите /start")


# --- SOURCE ---
@dp.message_handler(state=Feedback.source)
async def get_source(message: types.Message, state: FSMContext):

    if "Гостиница" in message.text:
        source = "Гостиница"
    elif "Лофт" in message.text:
        source = "Лофт"
    else:
        return await message.answer("Выберите вариант с кнопок")

    await state.update_data(source=source)
    await message.answer("Введите дату события (например: 12.05.2026):", reply_markup=types.ReplyKeyboardRemove())
    await Feedback.next()


# --- DATE ---
@dp.message_handler(state=Feedback.date)
async def get_date(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text)
    await message.answer("Напишите ваш отзыв:")
    await Feedback.next()


# --- REVIEW ---
@dp.message_handler(state=Feedback.review)
async def get_review(message: types.Message, state: FSMContext):
    await state.update_data(review=message.text)

    from keyboards import contact_kb

    await message.answer(
        "Оставьте контакт для связи или пропустите:",
        reply_markup=contact_kb
    )

    await Feedback.next()

# --- CONTACT ---
# --- CONTACT ---
@dp.message_handler(state=Feedback.contact, content_types=types.ContentTypes.ANY)
async def get_contact(message: types.Message, state: FSMContext):

    if message.contact:
        contact = message.contact.phone_number
    elif message.text == "❌ Пропустить":
        contact = "-"
    else:
        contact = message.text

    await state.update_data(contact=contact)

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
    await message.answer("Спасибо! 🙌", reply_markup=types.ReplyKeyboardRemove())

    await state.finish()

# --- RUN ---
if __name__ == "__main__":
    init_db()
    executor.start_polling(dp, skip_updates=True)
