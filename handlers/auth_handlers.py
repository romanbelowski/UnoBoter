from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging
from database import SessionLocal, get_user, create_user
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    choosing_role = State()

def get_role_keyboard():
    """Створення клавіатури для вибору ролі"""
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Я репетитор",
        callback_data="role_teacher"
    ))
    builder.add(types.InlineKeyboardButton(
        text="Я учень",
        callback_data="role_student"
    ))
    builder.adjust(1)
    return builder.as_markup()

async def start_command(message: types.Message, state: FSMContext):
    """Обробник команди /start"""
    user_id = message.from_user.id

    with SessionLocal() as db:
        try:
            user = get_user(db, user_id)
            if user:
                role = "репетитора" if user.is_teacher else "учня"
                await message.answer(
                    f"Ви вже зареєстровані як {role}!\n"
                    "Використовуйте команду /help для перегляду доступних команд.",
                    parse_mode=ParseMode.HTML
                )
            else:
                await state.set_state(RegistrationStates.choosing_role)
                await message.answer(
                    "Вітаємо! Будь ласка, оберіть вашу роль:",
                    reply_markup=get_role_keyboard(),
                    parse_mode=ParseMode.HTML
                )
        except Exception as e:
            logging.error(f"Помилка при обробці команди /start: {e}")
            await message.answer("Сталася помилка при реєстрації. Спробуйте пізніше.")

async def role_callback(callback: types.CallbackQuery, state: FSMContext):
    """Обробник вибору ролі через кнопки"""
    user_id = callback.from_user.id
    is_teacher = callback.data == "role_teacher"

    with SessionLocal() as db:
        try:
            user = get_user(db, user_id)
            if user:
                await callback.message.edit_text("Ви вже зареєстровані!")
            else:
                user = create_user(
                    db,
                    user_id,
                    callback.from_user.username,
                    callback.from_user.full_name,
                    is_teacher=is_teacher
                )

                role_text = "репетитора" if is_teacher else "учня"
                commands_text = get_teacher_commands() if is_teacher else get_student_commands()

                await callback.message.edit_text(
                    f"Реєстрація пройшла успішно! Ви зареєстровані як {role_text}.\n\n"
                    f"Доступні команди:\n{commands_text}"
                )

            await callback.answer()
            await state.clear()

        except Exception as e:
            logging.error(f"Помилка при обробці вибору ролі: {e}")
            await callback.message.edit_text(
                "Сталася помилка при реєстрації. Спробуйте ще раз через /start"
            )

def get_teacher_commands():
    return (
        "/help - Список доступних команд\n"
        "/profile - Переглянути профіль\n"
        "/setschedule - Додати новий урок\n"
        "/viewbookings - Переглянути заброньовані уроки\n"
        "/t_cancel - Скасувати урок\n"
        "/reschedule - Перенести урок\n"
        "/showmyschedule - Мій розклад\n"
    )

def get_student_commands():
    """Повертає список команд для учня"""
    return (
        "/help - Список доступних команд\n"
        "/profile - Переглянути профіль\n"
        "/schedule - Показати доступні уроки\n"
        "/book - Записатися на урок\n"
        "/mycourses - Мої заброньовані уроки\n"
        "/cancel - Скасувати урок\n"
        "/reschedule - Перенести урок\n"
        "/setreminder - Встановити нагадування"
    )

async def help_command(message: types.Message):
    """Обробник команди /help"""
    user_id = message.from_user.id

    with SessionLocal() as db:
        try:
            user = get_user(db, user_id)
            if not user:
                await message.answer(
                    "Спочатку потрібно зареєструватися. Використовуйте команду /start",
                    parse_mode=ParseMode.HTML
                )
                return

            commands = get_teacher_commands() if user.is_teacher else get_student_commands()
            await message.answer(f"Доступні команди:\n{commands}")
            logging.info("Команда /help виконана")

        except Exception as e:
            logging.error(f"Помилка при виконанні команди /help: {e}")
            await message.answer("Сталася помилка при отриманні списку команд.")