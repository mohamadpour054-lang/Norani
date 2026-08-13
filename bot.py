# -*- coding: utf-8 -*-
"""
اجرای ربات تلگرامی الدوریا به‌صورت Webhook — مخصوص دیپلوی روی Render (پلن رایگان Web Service).

برای اجرای محلی روی سیستم خودت به‌جای این فایل از bot_local.py استفاده کن.

متغیرهای محیطی لازم روی Render:
    BOT_TOKEN            توکنی که از @BotFather گرفتی (اجباری)
    WEBHOOK_SECRET        یه رشته‌ی دلخواه و رندوم برای امنیت وبهوک (اختیاری ولی توصیه‌شده)

Render خودش این‌ها رو خودکار تنظیم می‌کنه، نیازی به دست‌زدن نیست:
    RENDER_EXTERNAL_URL   آدرس عمومی سرویس (مثل https://eldoria-bot.onrender.com)
    PORT                  پورتی که باید سرویس روش گوش بده
"""
import logging
import os

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

import database as db
from handlers import router

logging.basicConfig(level=logging.INFO)

WEBHOOK_PATH = "/webhook"
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "eldoria-secret-change-me")


def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise SystemExit("❌ متغیر محیطی BOT_TOKEN تنظیم نشده. اونو توی Render > Environment اضافه کن.")

    base_url = os.environ.get("RENDER_EXTERNAL_URL") or os.environ.get("WEBHOOK_URL")
    if not base_url:
        raise SystemExit(
            "❌ آدرس عمومی سرویس پیدا نشد.\n"
            "اگه روی Render هستی این خودکار تنظیم میشه (RENDER_EXTERNAL_URL).\n"
            "اگه جای دیگه اجرا می‌کنی، متغیر WEBHOOK_URL رو با آدرس عمومی سرویس ست کن."
        )

    port = int(os.environ.get("PORT", 10000))

    db.init_db()

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    async def on_startup(app: web.Application):
        webhook_url = f"{base_url}{WEBHOOK_PATH}"
        await bot.set_webhook(
            webhook_url,
            secret_token=WEBHOOK_SECRET,
            drop_pending_updates=True,
        )
        logging.info("✅ وبهوک تنظیم شد: %s", webhook_url)

    async def on_shutdown(app: web.Application):
        await bot.delete_webhook()

    async def health(request: web.Request):
        # صفحه‌ی سلامتی ساده، تا Render بفهمه سرویس زندست
        return web.Response(text="🎮 Eldoria bot is running.")

    app = web.Application()
    app.router.add_get("/", health)

    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    ).register(app, path=WEBHOOK_PATH)

    setup_application(app, dp, bot=bot)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    print("🎮 ربات الدوریا (حالت وب‌هوک) در حال اجراست...")
    web.run_app(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
