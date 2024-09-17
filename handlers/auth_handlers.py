from aiogram import types
import logging
from database import SessionLocal, create_user, get_user, User
from aiogram.enums import ParseMode  
from aiogram.fsm.context import FSMContext

async def start_command(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    db = SessionLocal()
    
    try:
        user = get_user(db, user_id)
        
        if user:
            await message.answer("Ви вже зареєстровані!\nВикористовуйте команду /help - cписок доступних команд.", parse_mode=ParseMode.HTML)
        else:
            await message.answer("Вітаємо! Будь ласка, зареєструйтесь.", parse_mode=ParseMode.HTML)
            create_user(db, user_id, message.from_user.username, message.from_user.full_name, is_teacher=False)
            await message.answer("Реєстрація пройшла успішно!\nВикористовуйте команду /help - cписок доступних команд.")
    except Exception as e:
        logging.error(f"Помилка при обробці команди /start: {e}")
    finally:
        db.close()
    logging.info("Команда /start виконана")

async def help_command(message: types.Message):
    help_text = (
        "/start - Початок роботи з ботом\n"
        "/help - Список доступних команд\n"
        "/profile - Переглянути профіль\n"
        "/schedule - Показати доступні слоти\n"
        "/book - Записатися на урок\n"
        "/cancel - Скасувати урок\n"
        "/reschedule - Перенести урок\n"
        "/setreminder - Налаштувати нагадування\n"
        "/mycourses - Показати заброньовані уроки\n"
        "/set_teacher - Налаштувати як репетитора\n"
        "/set_student - Налаштувати як учня\n"
    )
    await message.answer(help_text, parse_mode=ParseMode.MARKDOWN)
    logging.info("Команда /help виконана")
