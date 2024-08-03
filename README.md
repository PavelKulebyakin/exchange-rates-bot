# Currency Bot

## Описание

Currency Bot - это телеграм-бот для получения информации о курсах валют. Бот позволяет пользователям получать текущие курсы обмена между различными валютами, а также просматривать список поддерживаемых валют.

## Функционал

- **/start** - Показать приветственное сообщение.
- **/help** - Показать список доступных команд и примеры использования.
- **/list** - Получить список всех поддерживаемых валют.
- **/rate** - Получить текущий курс обмена между двумя валютами.

## Установка и Запуск

### Требования

- Python 3.8+
- Docker (для использования с Docker)
- Токен Telegram Bot и ключ API Exchange Rate API

### Локальный запуск

1. Клонируйте репозиторий:

    ```sh
    git clone https://github.com/yourusername/currency_bot.git
    cd currency_bot
    ```

2. Установите зависимости:

    ```sh
    pip install -r requirements.txt
    ```

3. Создайте файл `.env` в корневой директории и добавьте следующие строки, заменив `your_telegram_token_here` и `your_exchange_rate_api_key_here` на ваши реальные значения:

    ```env
    TELEGRAM_TOKEN=your_telegram_token_here
    EXCHANGE_RATE_API_KEY=your_exchange_rate_api_key_here
    ```

4. Запустите бота:

    ```sh
    python main/bot.py
    ```

### Запуск с использованием Docker

1. Клонируйте репозиторий:

    ```sh
    git clone https://github.com/yourusername/currency_bot.git
    cd currency_bot
    ```

2. Создайте файл `.env` в корневой директории и добавьте следующие строки, заменив `your_telegram_token_here` и `your_exchange_rate_api_key_here` на ваши реальные значения:

    ```env
    TELEGRAM_TOKEN=your_telegram_token_here
    EXCHANGE_RATE_API_KEY=your_exchange_rate_api_key_here
    ```

3. Постройте и запустите контейнер Docker:

    ```sh
    docker-compose up --build
    ```

## Примеры использования

### Получение курса обмена

Чтобы узнать текущий курс обмена между двумя валютами, используйте команду `/rate`:

```plaintext
/rate USD RUB
```

Чтобы узнать курс обмена для определенной суммы, используйте команду /rate с тремя аргументами:

```plaintext
/rate USD RUB 100
```

Чтобы получить список всех поддерживаемых валют, используйте команду /list:

```plaintext
/list
```