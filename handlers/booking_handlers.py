from aiogram import types
import logging
import data

async def schedule_command(message: types.Message):
    schedule = data.get_schedule()
    await message.answer(f"Доступні слоти:\n{schedule}")
    logging.info("Команда /schedule виконана")

async def book_command(message: types.Message):
    try:
        _, date, time = message.text.split()
        data.book_lesson(date, time)
        await message.answer(f"Урок заброньовано на {date} о {time}.")
        logging.info(f"Урок заброньовано на {date} {time}")
    except ValueError:
        await message.answer("Будь ласка, вкажіть дату та час у форматі: /book <дата> <час>")
        logging.warning("Помилка формату команди /book")

async def cancel_command(message: types.Message):
    try:
        _, date, time = message.text.split()
        result = data.cancel_lesson(date, time)
        if result:
            await message.answer(result)
        else:
            await message.answer(f"Урок на {date} о {time} скасовано.")
            logging.info(f"Урок скасовано на {date} {time}")
    except ValueError:
        await message.answer("Будь ласка, вкажіть дату та час у форматі: /cancel <дата> <час>")
        logging.warning("Помилка формату команди /cancel")

async def reschedule_command(message: types.Message):
    try:
        _, lesson_id, new_date, new_time = message.text.split()
        result = data.reschedule_lesson(lesson_id, new_date, new_time)
        await message.answer(result)
        logging.info(f"Урок {lesson_id} перенесено на {new_date} о {new_time}")
    except ValueError:
        await message.answer("Будь ласка, вкажіть ID уроку, нову дату та час у форматі: /reschedule <id> <нова_дата> <новий_час>")
        logging.warning("Помилка формату команди /reschedule")
