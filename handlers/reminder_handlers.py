from aiogram import types
import logging
import data

async def set_reminder_command(message: types.Message):
    try:
        _, lesson_id, reminder_time = message.text.split()
        data.set_reminder(lesson_id, reminder_time)
        await message.answer(f"Нагадування про урок {lesson_id} встановлено на {reminder_time}.")
        logging.info(f"Нагадування про урок {lesson_id} встановлено на {reminder_time}")
    except ValueError:
        await message.answer("Будь ласка, вкажіть ID уроку та час нагадування у форматі: /setreminder <id> <час>")
        logging.warning("Помилка формату команди /setreminder")
