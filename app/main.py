from contextlib import asynccontextmanager

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types import Update
from fastapi import FastAPI

from app import config as cf, crud
from app.handlers import router

bots = {}

dp = Dispatcher()
dp.include_router(router)


def create_bot(token: str) -> Bot:
    return Bot(token=token, session=AiohttpSession(timeout=5))


async def on_startup():
    tokens: list[str] = await crud.get_tokens()

    for token in tokens:
        bot: Bot = create_bot(token=token)
        token_path = f"/{token}"
        webhook_url = cf.WEBHOOK_HOST + cf.WEBHOOK_PATH + token_path
        webhook_info = await bot.get_webhook_info()

        if webhook_info.url != webhook_url:
            await bot.set_webhook(url=webhook_url, drop_pending_updates=True)

        bots[token] = bot


async def on_shutdown():
    for token in bots:
        bot: Bot = bots[token]
        await bot.delete_webhook()
        await bot.session.close()


@asynccontextmanager
async def lifespan(_):
    await on_startup()
    yield
    await on_shutdown()


app = FastAPI(lifespan=lifespan)


@app.post('/webhook/{token}', include_in_schema=False)
async def bot_webhook(update: dict, token: str):
    update = Update(**update)
    bot: Bot = bots.get(token)
    await dp.feed_update(bot=bot, update=update)
