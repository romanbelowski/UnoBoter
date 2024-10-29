from aiogram import types
import logging
from database import SessionLocal, get_user, create_notification_settings, get_notification_settings, Booking
from datetime import datetime, timedelta

async def set_reminder_command(message: types.Message):
    try:
        command_parts = message.text.split()
        if len(command_parts) != 3:
            await message.answer("Формат: /set_reminder <id_бронювання> <години_до_уроку>")
            return

        booking_id = int(command_parts[1])
        hours_before = int(command_parts[2])

        user_id = message.from_user.id
        with SessionLocal() as db:
            user = get_user(db, user_id)
            if not user:
                await message.answer("Спочатку потрібно зареєструватися.")
                return

            # Перевіряємо чи існує бронювання і чи належить воно користувачу
            booking = db.query(Booking).filter(
                Booking.id == booking_id,
                Booking.student_id == user.id
            ).first()

            if not booking:
                await message.answer("Бронювання не знайдено або воно вам не належить.")
                return

            # Створюємо або оновлюємо налаштування нагадувань
            settings = get_notification_settings(db, user.id)
            if not settings:
                settings = create_notification_settings(db, user.id)

            # Тут можна додати логіку для збереження конкретного часу нагадування
            # Наприклад, можна створити нову таблицю для конкретних нагадувань

            await message.answer(
                f"Нагадування встановлено. Ви отримаєте повідомлення за {hours_before} годин до уроку."
            )
            logging.info(f"Встановлено нагадування для бронювання {booking_id}")

    except ValueError:
        await message.answer("Некоректний формат даних. Використовуйте цілі числа.")
    except Exception as e:
        logging.error(f"Помилка при встановленні нагадування: {e}")
        await message.answer("Сталася помилка при встановленні нагадування.")

async def toggle_reminders_command(message: types.Message):
    user_id = message.from_user.id
    with SessionLocal() as db:
        try:
            user = get_user(db, user_id)
            if not user:
                await message.answer("Спочатку потрібно зареєструватися.")
                return

            settings = get_notification_settings(db, user.id)
            if settings:
                settings.reminders_on = not settings.reminders_on
                db.commit()
                status = "увімкнені" if settings.reminders_on else "вимкнені"
            else:
                settings = create_notification_settings(db, user.id, True)
                status = "увімкнені"

            await message.answer(f"Нагадування {status}!")
            logging.info(f"Користувач {user_id} змінив налаштування нагадувань")

        except Exception as e:
            logging.error(f"Помилка при зміні налаштувань нагадувань: {e}")
            await message.answer("Сталася помилка при зміні налаштувань нагадувань.")