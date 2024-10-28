from aiogram import types
import logging
from database import SessionLocal, get_user, create_user
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode  

async def profile_command(message: types.Message):
    user_id = message.from_user.id
    
    with SessionLocal() as db:
        try:
            user = get_user(db, user_id)
            if user:
                profile_info = (f"Ім'я: {user.full_name}\n"
                                f"Юзернейм: @{user.username}\n"
                                f"Роль: {'Репетитор' if user.is_teacher else 'Учень'}")
                await message.answer(f"Ваш профіль:\n{profile_info}", parse_mode=ParseMode.HTML)
            else:
                await message.answer("Ви не зареєстровані. Використовуйте команду /start для реєстрації.", parse_mode=ParseMode.HTML)
        except Exception as e:
            logging.error(f"Помилка в команді /profile: {e}")
            await message.answer("Сталася помилка при отриманні вашого профілю.")

async def set_teacher_status(message: types.Message):
    """
    Команда для встановлення ролі користувача як репетитора
    """
    user_id = message.from_user.id
    
    with SessionLocal() as db:
        try:
            user = get_user(db, user_id)
            if user:
                user.is_teacher = True
                db.commit()
                await message.answer("Вітаю, ви наш новий репетитор!")
            else:
                await message.answer("Ви не зареєстровані. Використовуйте команду /start для реєстрації.")
        except Exception as e:
            logging.error(f"Помилка в команді /set_teacher: {e}")
            await message.answer("Сталася помилка при оновленні вашої ролі.")

async def set_student_status(message: types.Message):
    """
    Команда для встановлення ролі користувача як учня
    """
    user_id = message.from_user.id
    
    with SessionLocal() as db:
        try:
            user = get_user(db, user_id)
            if user:
                user.is_teacher = False
                db.commit()
                await message.answer("Вітаю, ви наш новий учень!")
            else:
                await message.answer("Ви не зареєстровані. Використовуйте команду /start для реєстрації.")
        except Exception as e:
            logging.error(f"Помилка в команді /set_student_status: {e}")
            await message.answer("Сталася помилка при оновленні вашої ролі.")
