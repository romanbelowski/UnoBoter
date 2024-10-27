from dotenv import load_dotenv
import os

load_dotenv()  # Завантажує змінні з .env файлу

TOKEN = os.getenv("TELEGRAM_TOKEN")
print(TOKEN)  # Для перевірки, чи правильно завантажено токен
