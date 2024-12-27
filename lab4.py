import logging
import requests
from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import *

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger("bot-logger")

# Переменные
TOKEN = '7947566711:AAHAXk-W3S2ZPUVAqHvbrKIzXIxso0zVKiM'
API_BASE_URL = 'https://cnichols1734.pythonanywhere.com'
USER_SETTINGS = {}

get_random_fact_btn = KeyboardButton('/random')
get_categories_btn = KeyboardButton('/get_categories')
set_categories_btn = KeyboardButton("/set_category")
get_random_fact_by_category_btn = KeyboardButton('/random_by_category')
kbm = ReplyKeyboardMarkup([[
    get_random_fact_btn, set_categories_btn, get_categories_btn, get_random_fact_by_category_btn
]], resize_keyboard=True)

async def start(update, context) -> None:
    """Ответы на команду /start."""
    await update.message.reply_text(
        'Привет! Я ваш бот, предоставляющий случайные факты. Попробуйте /random, /get_categories, /random_by_category или /set_category.',
        reply_markup=kbm
    )


async def get_random_fact(update, context) -> None:
    """Получение случайного факта."""
    try:
        response = requests.get(f'{API_BASE_URL}/facts/random')
        response.raise_for_status()
        fact = response.json().get('fact', 'Не удалось получить факт.')
        await update.message.reply_text(fact, reply_markup=kbm)
    except requests.exceptions.RequestException as e:
        logger.error(f'Ошибка получения факта: {e}')
        await update.message.reply_text('Произошла ошибка при получении факта. Попробуйте позже.')


def get_categories_list() -> list:
    """Получение списка категорий."""
    try:
        response = requests.get(f'{API_BASE_URL}/categories')
        response.raise_for_status()
        return response.json().get('categories', [])
    except requests.exceptions.RequestException as e:
        logger.error(f'Ошибка получения категорий: {e}')
        return []


async def get_categories(update, context) -> None:
    """Получение списка категорий /get_categories."""
    await update.message.reply_text(f"Доступные категории: {", ".join(get_categories_list())}")


async def get_random_fact_by_category(update, context) -> None:
    """Получение случайного факта по указанной категории или по сохранённой пользовательской настройке."""
    category = ' '.join(context.args).title()
    if not category:
        user_id = update.message.from_user.id
        category = USER_SETTINGS.get(user_id, 'Science')

    try:
        response = requests.get(f'{API_BASE_URL}/facts/random/{category}')
        response.raise_for_status()
        fact = response.json().get('fact', f'Факты для категории "{category}" не найдены.')
        await update.message.reply_text(fact)
    except requests.exceptions.RequestException as e:
        logger.error(f'Ошибка получения факта по категории: {e}')
        await update.message.reply_text('Произошла ошибка при получении факта по категории. Попробуйте позже.')


async def set_category(update, context) -> None:
    """Выбор и сохранение предпочтительной категории для пользователя через инлайн-кнопки."""
    categories = get_categories_list()
    if categories:
        keyboard = [[InlineKeyboardButton(cat, callback_data=f'set_category_{cat}')] for cat in categories]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Выберите категорию:', reply_markup=reply_markup)
    else:
        await update.message.reply_text('Категории недоступны. Попробуйте позже.')


async def button(update, context) -> None:
    """Обработка нажатий на инлайн-кнопки."""
    query = update.callback_query
    query.answer()

    # Извлекатель категории из данных кнопки
    category = query.data.split('_', 2)[2]
    user_id = query.from_user.id

    USER_SETTINGS[user_id] = category
    await query.edit_message_text(text=f'Категория "{category}" успешно сохранена.')


def main() -> None:
    """Запуск бота."""


    application = Application.builder().token(TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("random", get_random_fact))
    application.add_handler(CommandHandler("get_categories", get_categories))
    application.add_handler(CommandHandler("random_by_category", get_random_fact_by_category))
    application.add_handler(CommandHandler("set_category", set_category))

    # Обработчик для инлайн-кнопок
    application.add_handler(CallbackQueryHandler(button))

    # Запуск
    application.run_polling(1.0)


if __name__ == '__main__':
    main()
