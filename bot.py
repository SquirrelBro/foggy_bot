import sys
import time
import re
import traceback
import unicodedata
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from codecs import encode, decode
from datetime import datetime
from ast import literal_eval
from adv import *
from for_sheets import *

# Функция для обработки команды 'squirrel_roll'
async def squirrel_roll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = parse_and_roll(' '.join(context.args)) 
    if result:
        await update.message.reply_text(result, parse_mode='HTML')

# Функция для обработки команды 'sheeting'
async def sheeting(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = parse_and_sheet(' '.join(context.args), update.message.from_user.username)  
    await update.message.reply_text(result, parse_mode='HTML') 

# Функция для обработки команды 'roll_stats'
async def roll_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = generate_characteristics()
    await update.message.reply_text(result, parse_mode='HTML')

# Получение токена из аргументов командной строки
TOKEN = sys.argv[1]

# Настройка вывода логов
formatter = logging.Formatter('====> %(asctime)s | %(name)s | %(levelname)s | %(message)s')
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)
file_handler = logging.FileHandler('roll.log')
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(formatter)

logger = logging.basicConfig(
    handlers=[stream_handler, file_handler],
    level=logging.DEBUG,
)

# Основная функция для запуска приложения и добавление хендлеров
def main() -> None:
    app = ApplicationBuilder().token(TOKEN).build() 
    app.add_handler(CommandHandler('froll', squirrel_roll))
    app.add_handler(CommandHandler('s', roll_stats))
    app.add_handler(CommandHandler('help', help)) 
    app.add_handler(CommandHandler(['common', 'c'], sheeting))
    app.run_polling()

if __name__ == "__main__":
    main()