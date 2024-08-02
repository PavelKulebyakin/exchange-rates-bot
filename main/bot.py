import logging
import requests

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, Application, ContextTypes, CallbackQueryHandler
from config import TELEGRAM_TOKEN, EXCHANGE_RATE_API_KEY

ITEMS_PER_PAGE = 20

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
# logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Привет! Я бот для получения курса валют. Введите /rate <валюта>, чтобы узнать курс.')


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Help!")


async def fetch_supported_currencies():
    url = f'https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/codes'
    with requests.get(url) as response:
        return response


async def supported_currencies_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0) -> None:

    api_response = await fetch_supported_currencies()

    if not api_response.ok:
        await update.message.reply_text('Ошибка при получении данных. Пожалуйста, попробуйте позже.')
        return

    data = api_response.json()

    if data['result'] == 'error':
        await update.message.reply_text(f'Ошибка: {data["error-type"]}')
        return

    supported_currencies = data['supported_codes']
    total_pages = (len(supported_currencies) - 1) // ITEMS_PER_PAGE

    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    paginated_supported_currencies = supported_currencies[start:end]

    rate_message = f'Поддерживаемые валюты (стр. {page + 1}/{total_pages + 1}) :\n\n'
    for currency in paginated_supported_currencies:
        rate_message += f'{currency[0]} - {currency[1]}\n'

    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton("⬅️ Назад ", callback_data=f'{page - 1}'))
    if page < total_pages:
        buttons.append(InlineKeyboardButton("Вперед ➡️", callback_data=f'{page + 1}'))

    reply_markup = InlineKeyboardMarkup([buttons])

    if update.callback_query:
        await update.callback_query.edit_message_text(rate_message, reply_markup=reply_markup)
    else:
        await update.message.reply_text(rate_message, reply_markup=reply_markup)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    query = update.callback_query
    await query.answer()

    page = query.data
    page = int(page)
    await supported_currencies_handler(update, context, page)


def main() -> None:

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("supported", supported_currencies_handler))
    application.add_handler(CallbackQueryHandler(button_handler))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
