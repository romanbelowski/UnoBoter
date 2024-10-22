import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
import config
from handlers.profile_handlers import profile_command, set_teacher_status, set_student_status
import handlers.auth_handlers as auth_handlers
import handlers.booking_handlers as booking_handlers
import handlers.reminder_handlers as reminder_handlers
import asyncio

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN)
dp = Dispatcher()

# Регистрация обработчиков команд
dp.message.register(auth_handlers.start_command, Command("start"))
dp.message.register(auth_handlers.help_command, Command("help"))
dp.message.register(profile_command, Command("profile"))
dp.message.register(set_teacher_status, Command("set_teacher"))
dp.message.register(set_student_status, Command("set_student"))

dp.message.register(booking_handlers.schedule_command, Command("schedule"))
dp.message.register(booking_handlers.book_command, Command("book"))
dp.message.register(booking_handlers.cancel_command, Command("cancel"))
dp.message.register(booking_handlers.reschedule_command, Command("reschedule"))

dp.message.register(reminder_handlers.set_reminder_command, Command("setreminder"))

async def main():
    logging.info("Бот запускається...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Помилка при запуску бота: {e}")

if __name__ == '__main__':
    asyncio.run(main())
