import os
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
EXCHANGE_RATE_API_KEY = os.getenv('EXCHANGE_RATE_API_KEY')