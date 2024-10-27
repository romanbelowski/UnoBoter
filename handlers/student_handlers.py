from aiogram import types
from aiogram.filters import Command
import logging
from database import SessionLocal, get_user, get_user_bookings, get_available_lessons
from aiogram.enums import ParseMode


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
    with SessionLocal() as db:
        try:
            user = get_user(db, message.from_user.id)
            if not user:
                await message.answer("Спочатку потрібно зареєструватися. Використовуйте /start")
                return

            available_lessons = get_available_lessons(db)
            if available_lessons:
                response = "Доступні уроки:\n"
                for lesson in available_lessons:
                    teacher = lesson.teacher
                    response += (
                        f"ID: {lesson.id} | "
                        f"Дата: {lesson.date_time.strftime('%Y-%m-%d %H:%M')} | "
                        f"Викладач: {teacher.full_name}\n"
                    )
            else:
                response = "На даний момент немає доступних уроків."

            await message.answer(response)
            logging.info("Виконана команда /schedule")
        except Exception as e:
            logging.error(f"Помилка при отриманні розкладу: {e}")
            await message.answer("Сталася помилка при отриманні розкладу.")


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