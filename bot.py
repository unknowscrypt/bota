import asyncio
import logging
import os
import random

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo,
)

from tarot_data import FULL_DECK

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ["BOT_TOKEN"]          # токен из BotFather
WEBAPP_URL = os.environ["WEBAPP_URL"]        # https-адрес задеплоенного webapp (см. README)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✨ Открыть приложение", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton(text="🃏 Карта дня", callback_data="daily_card")],
    ])


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Привет! Я — бот таро и матрицы судьбы.\n\n"
        "Открой приложение для полного интерфейса с раскладами и расчётом "
        "матрицы, или просто вытяни карту дня прямо здесь.",
        reply_markup=main_menu(),
    )


@dp.message(Command("card"))
@dp.callback_query(F.data == "daily_card")
async def daily_card(event):
    card = random.choice(FULL_DECK)
    reversed_ = random.random() < 0.35
    text = (
        f"{card['emoji']} <b>{card['name']}</b>"
        f"{' (перевёрнутая)' if reversed_ else ''}\n\n"
        f"{card['reversed'] if reversed_ else card['upright']}"
    )
    if isinstance(event, Message):
        await event.answer(text, parse_mode="HTML", reply_markup=main_menu())
    else:
        await event.message.answer(text, parse_mode="HTML", reply_markup=main_menu())
        await event.answer()


@dp.message(Command("matrix"))
async def matrix_hint(message: Message):
    await message.answer(
        "Расчёт матрицы судьбы удобнее делать в приложении — там есть ввод "
        "даты и наглядная схема.",
        reply_markup=main_menu(),
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
