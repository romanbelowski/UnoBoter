from aiogram import types
import logging
from database import SessionLocal, get_user, create_lesson, get_user_bookings
from datetime import datetime


async def setschedule_command(message: types.Message):
    try:
        command_parts = message.text.split()
        if len(command_parts) != 3:
            await message.answer("Формат: /setschedule <дата> <час>")
            return

        date_str = command_parts[1]
        time_str = command_parts[2]
        date_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")

        user_id = message.from_user.id
        with SessionLocal() as db:
            user = get_user(db, user_id)
            if not user or not user.is_teacher:
                await message.answer("Ця команда доступна тільки для викладачів.")
                return

            new_lesson = create_lesson(db, user.id, date_time)
            await message.answer(f"Додано новий урок на {date_time.strftime('%Y-%m-%d %H:%M')}")
            logging.info(f"Викладач {user_id} додав новий урок")

    except ValueError:
        await message.answer("Некоректний формат дати/часу. Використовуйте формат: YYYY-MM-DD HH:MM")
    except Exception as e:
        logging.error(f"Помилка при створенні уроку: {e}")
        await message.answer("Сталася помилка при створенні уроку.")


async def viewbookings_command(message: types.Message):
    user_id = message.from_user.id

    with SessionLocal() as db:
        try:
            user = get_user(db, user_id)
            if not user or not user.is_teacher:
                await message.answer("Ця команда доступна тільки для викладачів.")
                return

            bookings = get_user_bookings(db, user.id, is_teacher=True)
            if bookings:
                response = "Ваші заброньовані уроки:\n"
                for booking in bookings:
                    student = booking.student
                    lesson = booking.lesson
                    response += f"ID: {booking.id} | Дата: {lesson.date_time.strftime('%Y-%m-%d %H:%M')} | "
                    response += f"Учень: {student.full_name} | Статус: {booking.status}\n"
            else:
                response = "У вас поки немає заброньованих уроків."

            await message.answer(response)
            logging.info(f"Викладач {user_id} переглянув свої бронювання")

        except Exception as e:
            logging.error(f"Помилка при отриманні бронювань: {e}")
            await message.answer("Сталася помилка при отриманні списку бронювань.")