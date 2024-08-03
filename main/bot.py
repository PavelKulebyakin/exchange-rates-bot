import logging
import requests

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import CommandHandler, Application, ContextTypes, CallbackQueryHandler
from cachetools import TTLCache, cached
from config import TELEGRAM_TOKEN, EXCHANGE_RATE_API_KEY

# Конфигурация
ITEMS_PER_PAGE = 20
BASE_CACHE_TTL = 3600
LONG_CACHE_TTL = 3600 * 24

# Настройка кэша
base_cache = TTLCache(maxsize=100, ttl=BASE_CACHE_TTL)
long_cache = TTLCache(maxsize=1, ttl=LONG_CACHE_TTL)

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    start_message = (
        "👋 Привет! Я бот для получения курса валют.\n\n"
        "Вот список полезных команд:\n\n"
        "💱 /rate - Получить текущий курс обмена между двумя валютами.\n"
        "📋 /list - Получить список поддерживаемых валют.\n"
        "❓ /help - Показать дополнительную информацию.\n\n"
    )
    await update.message.reply_text(start_message)


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_message = (
        "👋 Добро пожаловать! Я ваш бот для получения информации о курсах валют.\n\n"
        "Вот список доступных команд:\n\n"
        "💱 /rate  - Получить текущий курс обмена между двумя валютами.\n"
        "📋 /list  - Получить список всех поддерживаемых валют.\n"
        "❓ /help  - Показать дополнительную информацию.\n"
        "💡 /start - Начать работу с ботом и получить приветственное сообщение.\n\n"
        "Примеры использования команды /rate:\n\n"
        "🔹 Если вы хотите узнать курс обмена из долларов США (USD) в российские рубли (RUB), введите: /rate USD RUB\n"
        "🔹 Если вы хотите узнать перевести 100 евро (EUR) в японские иены (JPY), введите: /rate EUR JPY 100\n\n"
    )
    await update.message.reply_text(help_message)


@cached(long_cache)
async def fetch_supported_currencies():
    url = f'https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/codes'
    with requests.get(url) as response:
        return response


async def supported_currencies_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0) -> None:

    api_response = await fetch_supported_currencies

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


async def fetch_pair_amount_conversion(base_currency: str, target_currency: str, amount: str):
    url = f'https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/pair/{base_currency}/{target_currency}/{amount}'
    with requests.get(url) as response:
        return response


@cached(base_cache)
async def fetch_pair_conversion(base_currency: str, target_currency: str):
    url = f'https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/pair/{base_currency}/{target_currency}'
    with requests.get(url) as response:
        return response


async def pair_conversion_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    args = context.args

    if not args or len(args) < 2:
        await update.message.reply_text('Пожалуйста, укажите базовую и целевую валюты. Пример: /rate RUB USD')
        return

    if len(args) > 3:
        await update.message.reply_text('Слишком много аргументов. Пример: /rate RUB USD или /rate RUB USD 100')
        return

    base_currency, target_currency = args[:2]

    if not (is_valid_currency_code(base_currency) and is_valid_currency_code(target_currency)):
        await update.message.reply_text('Код валюты должен состоять из трех латинских букв. Пример: RUB')
        return

    if len(args) == 2:
        amount = 1
        api_response = await fetch_pair_conversion(base_currency, target_currency)
    elif len(args) == 3 and args[2].isdigit():
        amount = args[2]
        api_response = await fetch_pair_amount_conversion(base_currency, target_currency, amount)
    else:
        message_text = 'Количество валюты должно быть записано в виде цифры.\nПример: /rate RUB USD 100.'
        await update.message.reply_text(message_text)
        return

    if api_response.status_code == 404:
        error_message = 'Пожалуйста, проверьте название валюты.'
        await update.message.reply_text(error_message)
        return

    if not api_response.ok:
        error_message = 'Ошибка при получении данных.\nПожалуйста, попробуйте позже.'
        await update.message.reply_text(error_message)
        return

    data = api_response.json()
    conversion_result = data['conversion_result']

    reply_message = f"Курс обмена : {amount} {base_currency} = {conversion_result} {target_currency}"

    await update.message.reply_text(reply_message)


def is_valid_currency_code(currency_code: str) -> bool:
    return len(currency_code) == 3 and currency_code.isalpha()


async def post_init(application: Application) -> None:
    bot_commands = [
        BotCommand("rate", "Получить курс валют"),
        BotCommand("list", "Список поддерживаемых валют"),
        BotCommand("help", "Помощь")
    ]
    await application.bot.set_my_commands(bot_commands)


def start() -> None:

    application = Application.builder().token(TELEGRAM_TOKEN).post_init(post_init).build()

    handlers = [
        CommandHandler("start", start_handler),
        CommandHandler("help", help_handler),
        CommandHandler("list", supported_currencies_handler),
        CommandHandler("rate", pair_conversion_handler),
        CallbackQueryHandler(button_handler)
    ]

    application.add_handlers(handlers)

    application.run_polling(allowed_updates=Update.ALL_TYPES)



