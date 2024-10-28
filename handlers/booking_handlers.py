from aiogram import types
import logging
from database import (
    SessionLocal,
    get_user,
    get_available_lessons,
    create_booking,
    Lesson,
    Booking
)
from datetime import datetime

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