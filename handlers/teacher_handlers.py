from aiogram import types
from aiogram.filters import Command
import data
import logging

async def setschedule_command(message: types.Message):
    new_schedule = message.text.replace('/setschedule ', '')
    data.schedule = new_schedule
    await message.answer("Розклад оновлено.")
    logging.info("Розклад оновлено")

async def viewbookings_command(message: types.Message):
    bookings = data.get_bookings()
    await message.answer(f"Всі заброньовані уроки:\n{bookings}")
    logging.info("Виконана команда /viewbookings")
