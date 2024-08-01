import logging
import requests

from telegram import Update
from telegram.ext import CommandHandler, Application, ContextTypes
from config import TELEGRAM_TOKEN, EXCHANGE_RATE_API_KEY

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Привет! Я бот для получения курса валют. Введите /rate <валюта>, чтобы узнать курс.')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Help!")


async def get_rate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text('Пожалуйста, укажите валюту. Пример: /rate USD')
        return

    currency = context.args[0].upper()
    response = requests.get(f'https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/latest/{currency}')

    if response.status_code != 200:
        await update.message.reply_text('Ошибка при получении данных. Пожалуйста, попробуйте позже.')
        return

    data = response.json()

    if data['result'] == 'error':
        await update.message.reply_text(f'Ошибка: {data["error-type"]}')
        return

    rates = data['conversion_rates']
    rate_message = f'Курсы валют для {currency}:\n'
    for key, value in rates.items():
        rate_message += f'{key}: {value}\n'

    await update.message.reply_text(rate_message)


def main() -> None:
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("rate", get_rate))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
