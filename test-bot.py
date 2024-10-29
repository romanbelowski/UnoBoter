import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

from handlers.auth_handlers import start_command, help_command, role_callback
from handlers.profile_handlers import profile_command, set_teacher_status, set_student_status
from handlers.student_handlers import (
    book_command,
    cancel_command
)
from handlers.teacher_handlers import (
    setschedule_command,
    viewbookings_command, check_and_show_schedule, slot_cancel_command, book_cancel_command
)
from handlers.student_handlers import mycourses_command, schedule_command
from handlers.reminder_handlers import (
    set_reminder_command,
    toggle_reminders_command
)

from database import init_db

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ініціалізація бота і диспетчера
bot = Bot(token="7443278914:AAGunpsq3Ep5Ysq7-fKYRpF6dFgHKcrGYy0")
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

def register_handlers():
    # Аутентифікація
    dp.message.register(start_command, Command("start"))
    dp.message.register(help_command, Command("help"))
    dp.callback_query.register(role_callback, F.data.startswith("role_"))

    # Профіль
    dp.message.register(profile_command, Command("profile"))
    dp.message.register(set_teacher_status, Command("setteacher"))
    dp.message.register(set_student_status, Command("setstudent"))

    # Бронювання
    dp.message.register(book_command, Command("book"))
    dp.message.register(cancel_command, Command("cancel"))

    # Команди учня
    dp.message.register(mycourses_command, Command("my_courses"))
    dp.message.register(schedule_command, Command("schedule"))

    # Нагадування
    dp.message.register(set_reminder_command, Command("set_reminder"))
    dp.message.register(toggle_reminders_command, Command("toggle_reminders"))

    # Команди викладача
    dp.message.register(setschedule_command, Command("set_schedule_slot"))
    dp.message.register(viewbookings_command, Command("view_bookings"))
    dp.message.register(check_and_show_schedule, Command("show_my_schedule"))
    dp.message.register(slot_cancel_command, Command("slot_cancel"))
    dp.message.register(book_cancel_command, Command("book_cancel"))

async def main():
    logger.info("Запуск бота...")
    try:
        # Ініціалізація бази даних
        init_db()
        logger.info("База даних ініціалізована")

        # Реєстрація хендлерів
        register_handlers()
        logger.info("Хендлери зареєстровані")

        # Запуск бота
        logger.info("Бот запущений")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Помилка при запуску бота: {e}")
    finally:
        await bot.session.close()
        logger.info("Бот зупинений")

if __name__ == '__main__':
    try:
        import asyncio

        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот зупинений через переривання")
    except Exception as e:
        logger.error(f"Критична помилка: {e}")