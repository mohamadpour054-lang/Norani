# -*- coding: utf-8 -*-
"""
اجرای ربات تلگرامی الدوریا (Eldoria)
قبل از اجرا، توکن ربات رو در متغیر محیطی BOT_TOKEN قرار بده:
    export BOT_TOKEN="123456:ABC-your-token-here"
    python3 bot.py
"""
import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

import database as db
from handlers import router

logging.basicConfig(level=logging.INFO)


async def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise SystemExit(
            "❌ متغیر محیطی BOT_TOKEN تنظیم نشده.\n"
            "توکن رو از @BotFather بگیر و اینطوری اجرا کن:\n"
            '   export BOT_TOKEN="توکن_تو"\n'
            "   python3 bot.py"
        )

    db.init_db()

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    print("🎮 ربات الدوریا در حال اجراست...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
