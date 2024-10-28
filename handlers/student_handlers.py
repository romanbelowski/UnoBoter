import logging
import re
from datetime import datetime, timedelta

from aiogram import types
from aiogram.enums import ParseMode

from database import SessionLocal, get_user, get_user_bookings, get_user_schedule, User, Lesson


async def start_command(message: types.Message):
    user_id = message.from_user.id
    with SessionLocal() as db:
        try:
            user = get_user(db, user_id)
            if user and not user.is_teacher:
                await message.answer(
                    "Ви вже зареєстровані як учень! Використовуйте /help для отримання списку команд.",
                    parse_mode=ParseMode.HTML
                )
            else:
                await message.answer(
                    "Привіт! Я ваш репетитор-бот. Використовуйте /help для отримання списку команд.",
                    parse_mode=ParseMode.HTML
                )
        except Exception as e:
            logging.error(f"Помилка в команді /start для учня: {e}")
            await message.answer("Сталася помилка при старті бота.")


async def help_command(message: types.Message):
    help_text = (
        "/start - Початок роботи з ботом\n"
        "/help - Список доступних команд\n"
        "/profile - Переглянути профіль\n"
        "/schedule - Показати доступні уроки\n"
        "/book <id_уроку> - Записатися на урок\n"
        "/mycourses - Показати мої заброньовані уроки\n"
        "/cancel <id_бронювання> - Скасувати урок\n"
        "/reschedule <id_бронювання> <новий_id_уроку> - Перенести урок\n"
        "/setreminder <id_бронювання> <час> - Встановити нагадування"
    )
    await message.answer(help_text)
    logging.info("Виконана команда /help")


async def schedule_command(message: types.Message):
    command_parts = message.text.split()

    if len(command_parts) != 2 or not command_parts[1].startswith('@'):
        await message.answer("Невірний формат команди. Використовуйте: /schedule @username")
        return

    username = command_parts[1][1:]  # Видаляємо '@'

    with SessionLocal() as db:
        try:
            # Шукаємо викладача за username
            user = db.query(User).filter(User.username == username, User.is_teacher == True).first()

            if not user:
                await message.answer(f"Викладача з username @{username} не знайдено або він не є викладачем.")
                return

            # Отримуємо розклад викладача
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=7)  # На наступний тиждень
            lessons = get_user_schedule(db, user.id, start_date, end_date)

            if not lessons:
                await message.answer(f"У викладача @{username} немає уроків на найближчий тиждень.")
                return

            # Формуємо таблицю уроків
            response = f"Розклад викладача @{username}:\n\n"
            response += "ID Уроку | Дата та Час | Статус\n"
            response += "-" * 40 + "\n"

            for lesson in lessons:
                status = "Заброньований" if lesson.is_booked else "Вільний"
                response += f"{lesson.id:<9} | {lesson.date_time.strftime('%Y-%m-%d %H:%M'):<14} | {status}\n"

            await message.answer(response)

        except Exception as e:
            logging.error(f"Помилка в команді /schedule: {e}")
            await message.answer("Сталася помилка при обробці запиту.")

async def mycourses_command(message: types.Message):
    with SessionLocal() as db:
        try:
            user = get_user(db, message.from_user.id)
            if not user:
                await message.answer("Спочатку потрібно зареєструватися. Використовуйте /start")
                return

            bookings = get_user_bookings(db, user.id)
            if bookings:
                response = "Ваші заброньовані уроки:\n"
                for booking in bookings:
                    lesson = booking.lesson
                    teacher = lesson.teacher
                    response += (
                        f"ID бронювання: {booking.id} | "
                        f"Дата: {lesson.date_time.strftime('%Y-%m-%d %H:%M')} | "
                        f"Викладач: {teacher.full_name} | "
                        f"Статус: {booking.status}\n"
                    )
            else:
                response = "У вас поки немає заброньованих уроків."

            await message.answer(response)
            logging.info("Виконана команда /mycourses")
        except Exception as e:
            logging.error(f"Помилка при отриманні списку уроків: {e}")
            await message.answer("Сталася помилка при отриманні списку уроків.")