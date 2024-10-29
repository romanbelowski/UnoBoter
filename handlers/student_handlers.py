import logging
import re
from datetime import datetime, timedelta

from aiogram import types
from aiogram.enums import ParseMode

from database import SessionLocal, get_user, get_user_bookings, get_user_schedule, User, Lesson, create_booking, Booking

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
        "/schedule - Показати доступні слоти викладача\n"
        "/book <id_уроку> - Записатися на урок\n"
        "/mycourses - Показати мої заброньовані уроки\n"
        "/cancel <id_бронювання> - Скасувати урок\n"
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
                    teacher = lesson.teacher if lesson else None

                    lesson_info = (
                        f"ID бронювання: {booking.id} | "
                        f"Дата: {lesson.date_time.strftime('%Y-%m-%d %H:%M') if lesson else 'Невідомо'} | "
                        f"Викладач: {teacher.full_name if teacher else 'Невідомо'} | "
                        f"Статус: {booking.status}\n"
                    )
                    response += lesson_info
            else:
                response = "У вас поки немає заброньованих уроків."

            await message.answer(response)
            logging.info("Виконана команда /mycourses")

        except Exception as e:
            logging.error(f"Помилка при отриманні списку уроків: {e}")
            await message.answer("Сталася помилка при отриманні списку уроків.")

async def book_command(message: types.Message):
    try:
        command_parts = message.text.split()
        if len(command_parts) != 2:
            await message.answer("Будь ласка, вкажіть ID уроку у форматі: /book <id_уроку>")
            return

        lesson_id = int(command_parts[1])
        user_id = message.from_user.id

        with SessionLocal() as db:
            user = get_user(db, user_id)
            if not user:
                await message.answer("Спочатку потрібно зареєструватися. Використовуйте /start")
                return

            if user.is_teacher:
                await message.answer("Викладачі не можуть бронювати уроки.")
                return

            lesson = db.query(Lesson).filter(Lesson.id == lesson_id, Lesson.is_booked == False).first()
            if not lesson:
                await message.answer("Урок не знайдено або вже заброньовано.")
                return

            booking = create_booking(db, lesson_id, user.id)
            await message.answer(f"Урок успішно заброньовано на {lesson.date_time.strftime('%Y-%m-%d %H:%M')}")
            logging.info(f"Користувач {user_id} заброньував урок {lesson_id}")

    except ValueError:
        await message.answer("Некоректний формат ID уроку.")
        logging.warning("Помилка формату команди /book")
    except Exception as e:
        logging.error(f"Помилка при бронюванні уроку: {e}")
        await message.answer("Сталася помилка при бронюванні уроку.")

async def cancel_command(message: types.Message):
    try:
        command_parts = message.text.split()
        if len(command_parts) != 2:
            await message.answer("Будь ласка, вкажіть ID бронювання у форматі: /cancel <id_бронювання>")
            return

        booking_id = int(command_parts[1])
        user_id = message.from_user.id

        with SessionLocal() as db:
            user = get_user(db, user_id)
            if not user:
                await message.answer("Спочатку потрібно зареєструватися.")
                return

            booking = db.query(Booking).filter(Booking.id == booking_id).first()
            if not booking or (not user.is_teacher and booking.student_id != user.id):
                await message.answer("Бронювання не знайдено або у вас немає прав для його скасування.")
                return

            booking.status = "cancelled"
            booking.lesson.is_booked = False
            db.commit()

            await message.answer(f"Бронювання #{booking_id} скасовано.")
            logging.info(f"Користувач {user_id} скасував бронювання {booking_id}")

    except ValueError:
        await message.answer("Некоректний формат ID бронювання.")
        logging.warning("Помилка формату команди /cancel")
    except Exception as e:
        logging.error(f"Помилка при скасуванні бронювання: {e}")
        await message.answer("Сталася помилка при скасуванні бронювання.")

'''
НА ВІДЛАДЦІ (поки що звідусіль видалив посилання на хендлер)
async def reschedule_command(message: types.Message):
    try:
        command_parts = message.text.split()
        if len(command_parts) != 3:
            await message.answer("Формат: /reschedule <id_бронювання> <новий_id_уроку>")
            return

        booking_id = int(command_parts[1])
        new_lesson_id = int(command_parts[2])
        user_id = message.from_user.id

        with SessionLocal() as db:
            user = get_user(db, user_id)
            if not user:
                await message.answer("Спочатку потрібно зареєструватися.")
                return

            booking = db.query(Booking).filter(Booking.id == booking_id).first()
            if not booking or (not user.is_teacher and booking.student_id != user.id):
                await message.answer("Бронювання не знайдено або у вас немає прав для його перенесення.")
                return

            new_lesson = db.query(Lesson).filter(
                Lesson.id == new_lesson_id,
                Lesson.is_booked == False
            ).first()

            if not new_lesson:
                await message.answer("Новий слот недоступний.")
                return

            # Оновлення старого уроку
            booking.lesson.is_booked = False

            # Оновлення бронювання
            booking.lesson_id = new_lesson_id
            booking.status = "rescheduled"
            new_lesson.is_booked = True

            db.commit()

            await message.answer(f"Урок перенесено на {new_lesson.date_time.strftime('%Y-%m-%d %H:%M')}")
            logging.info(f"Користувач {user_id} переніс бронювання {booking_id} на урок {new_lesson_id}")

    except ValueError:
        await message.answer("Некоректний формат ID.")
        logging.warning("Помилка формату команди /reschedule")
    except Exception as e:
        logging.error(f"Помилка при перенесенні уроку: {e}")
        await message.answer("Сталася помилка при перенесенні уроку.")
'''