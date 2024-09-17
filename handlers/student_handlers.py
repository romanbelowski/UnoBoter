from aiogram import types
from aiogram.filters import Command
import data
import logging

async def start_command(message: types.Message):
    await message.answer("Привіт! Я ваш репетитор-бот. Використовуйте /help для отримання списку команд.")
    logging.info("Виконана команда /start")

async def help_command(message: types.Message):
    help_text = (
        "/start - Початок роботи з ботом\n"
        "/help - Список доступних команд\n"
        "/schedule - Показати доступні слоти\n"
        "/book <дата> <час> - Записатися на урок\n"
        "/mycourses - Показати заброньовані уроки\n"
        "/cancel <дата> <час> - Скасувати урок"
    )
    await message.answer(help_text)
    logging.info("Виконана команда /help")

async def schedule_command(message: types.Message):
    schedule = data.get_schedule()
    await message.answer(f"Доступні слоти:\n{schedule}")
    logging.info("Виконана команда /schedule")

async def book_command(message: types.Message):
    try:
        _, date, time = message.text.split()
        data.book_lesson(date, time)
        await message.answer(f"Урок заброньовано на {date} о {time}.")
        logging.info(f"Урок забронирован на {date} {time}")
    except ValueError:
        await message.answer("Будь ласка, вкажіть дату та час у форматі: /book <дата> <час>")
        logging.warning("Помилка команди /book")

async def mycourses_command(message: types.Message):
    bookings = data.get_bookings()
    await message.answer(f"Ваші заброньовані уроки:\n{bookings}")
    logging.info("Виконана команда /mycourses")

async def cancel_command(message: types.Message):
    try:
        _, date, time = message.text.split()
        result = data.cancel_lesson(date, time)
        if result:
            await message.answer(result)
        else:
            await message.answer(f"Урок на {date} о {time} скасовано.")
            logging.info(f"Урок скасовано {date} {time}")
    except ValueError:
        await message.answer("Будь ласка, вкажіть дату та час у форматі: /cancel <дата> <час>")
        logging.warning("Помилка команди /cancel")
