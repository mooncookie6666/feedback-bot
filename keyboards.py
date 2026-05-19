from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_kb = ReplyKeyboardMarkup(resize_keyboard=True)
start_kb.add(
    KeyboardButton("Гостиница"),
    KeyboardButton("Лофт")
)

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

contact_kb = ReplyKeyboardMarkup(resize_keyboard=True)
contact_kb.add(
    KeyboardButton("📱 Отправить контакт", request_contact=True),
    KeyboardButton("❌ Пропустить")
)
