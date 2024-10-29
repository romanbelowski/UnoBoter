import logging
from database import SessionLocal, get_user, create_lesson, get_user_bookings, get_user_schedule, Lesson, Booking
from aiogram.fsm.context import FSMContext
from aiogram import types  # Використовуємо F для фільтрації тексту
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError

# Артем: Додав шедеврозахист, щоб заднім числом уроки не ставили
async def setschedule_command(message: types.Message):
    try:
        command_parts = message.text.split()
        if len(command_parts) != 3:
            await message.answer("Формат: /set_schedule_slot <дата> <час>")
            return

        # Отримання дати та часу від користувача
        date_str = command_parts[1]
        time_str = command_parts[2]
        date_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")

        # Перевірка, чи дата ще не минула
        current_time = datetime.now()
        if date_time < current_time:
            await message.answer("Не можна створювати урок на минулу дату.")
            return

        # Перевірка, чи користувач є викладачем
        user_id = message.from_user.id
        with SessionLocal() as db:
            user = get_user(db, user_id)
            if not user or not user.is_teacher:
                await message.answer("Ця команда доступна тільки для викладачів.")
                return

            # Створення нового уроку
            new_lesson = create_lesson(db, user.id, date_time)
            await message.answer(f"Додано новий урок на {date_time.strftime('%Y-%m-%d %H:%M')}")
            logging.info(f"Викладач {user_id} додав новий урок на {date_time}")

    except ValueError:
        await message.answer("Некоректний формат дати/часу. Використовуйте формат: YYYY-MM-DD HH:MM")
    except Exception as e:
        logging.error(f"Помилка при створенні уроку: {e}")
        await message.answer("Сталася помилка при створенні уроку.")

# Це мабуть видалити
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
                response = "Ваші заброньовані студентами уроки:\n"
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

# Вивід всіх уроків, айді, та студентів які на уроки підписались
async def check_and_show_schedule(message: types.Message):
    user_id = message.from_user.id

    with SessionLocal() as db:
        try:
            # Перевірка, чи є користувач викладачем
            user = get_user(db, user_id)
            if not user or not user.is_teacher:
                await message.answer("Ця команда доступна тільки для викладачів.")
                return

            # Отримання поточного тижня (понеділок - неділя)
            today = datetime.today()
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)

            # Отримання розкладу викладача на поточний тиждень
            lessons = get_user_schedule(db, user.id, start_of_week, end_of_week)

            if not lessons:
                await message.answer("У вас немає запланованих уроків на цей тиждень.")
                return

            # Формування таблиці розкладу
            header = f"{'ID слота':<10} | {'Дата':<12} | {'Час':<6} | {'Стан':<12} | {'Учень':<20}\n"
            separator = "-" * 65 + "\n"
            rows = []

            for lesson in lessons:
                slot_id = lesson.id
                date = lesson.date_time.strftime('%Y-%m-%d')
                time = lesson.date_time.strftime('%H:%M')
                booking_status = "Забр." if lesson.is_booked else "Вільн."

                # Перевірка наявності бронювання і студента
                if lesson.booking:
                    student_name = lesson.booking.student.full_name
                else:
                    student_name = "-"

                rows.append(f"{slot_id:<10} | {date:<12} | {time:<6} | {booking_status:<12} | {student_name:<20}")

            # Збір повідомлення
            response = "📅 *Ваш розклад на тиждень:*\n\n" + header + separator + "\n".join(rows)

            await message.answer(response, parse_mode="Markdown")
            logging.info(f"Викладач {user_id} переглянув свій розклад на тиждень")

        except SQLAlchemyError as e:
            logging.error(f"Помилка при отриманні розкладу з бази даних: {e}")
            await message.answer("Сталася помилка при отриманні розкладу. Спробуйте пізніше.")
        except Exception as e:
            logging.error(f"Неочікувана помилка: {e}")
            await message.answer("Сталася непередбачувана помилка.")

# Видалення слота для бронювання
async def slot_cancel_command(message: types.Message):
    # Отримуємо текст повідомлення та розбиваємо його на частини
    args = message.text.split()

    # Перевірка, чи є ID слота у повідомленні та чи є він числом
    if len(args) < 2 or not args[1].isdigit():
        await message.answer("Будь ласка, вкажіть коректний ID слота для видалення.")
        return

    lesson_id = int(args[1])  # Отримуємо ID слота

    with SessionLocal() as db:
        try:
            # Перевірка, чи є користувач викладачем
            user = get_user(db, message.from_user.id)
            if not user or not user.is_teacher:
                await message.answer("Ця команда доступна тільки для викладачів.")
                return

            # Отримання уроку за його ID
            lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()

            # Якщо урок не знайдено
            if not lesson:
                await message.answer(f"Урок з ID {lesson_id} не існує.")
                return

            # Перевірка, чи урок належить цьому викладачеві
            if lesson.teacher_id != user.id:
                await message.answer("Цей урок не належить вам.")
                return

            # Перевірка, чи урок вже заброньований
            if lesson.is_booked:
                await message.answer("Цей урок вже заброньовано і не може бути видалений.")
                return

            # Видалення уроку
            db.delete(lesson)
            db.commit()
            await message.answer(f"Урок з ID {lesson_id} успішно видалено.")

        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Помилка при видаленні уроку: {e}")
            await message.answer("Сталася помилка при видаленні уроку. Спробуйте пізніше.")

        except Exception as e:
            logging.error(f"Невідома помилка: {e}")
            await message.answer("Сталася невідома помилка. Спробуйте пізніше.")

async def book_cancel_command(message: types.Message):
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