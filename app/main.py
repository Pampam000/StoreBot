from contextlib import asynccontextmanager

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.types import Update
from fastapi import FastAPI

from app.api.bots.routes import router as bots_api_router
from app.api.messages.routes import router as messages_api_router, buttons_router
from app.bot import crud
from app.bot.bot import create_webhook_bot, bots, close_bots
# from app.bot.handlers import router
from app.bot.register.handlers import router
from app.db.db import make_migrations

dp = Dispatcher()
dp.include_router(router)


async def on_startup():
    await make_migrations()

    tokens: list[str] = await crud.get_tokens()
    for token in tokens:
        await create_webhook_bot(token=token)


async def on_shutdown():
    await close_bots()


@asynccontextmanager
async def lifespan(_):
    await on_startup()
    yield
    await on_shutdown()


app = FastAPI(lifespan=lifespan)

app.include_router(bots_api_router)
app.include_router(messages_api_router)
app.include_router(buttons_router)

@app.post('/webhook/{token}', include_in_schema=False)
async def bot_webhook(update: dict, token: str):
    update = Update(**update)
    _bot: Bot = bots.get(token)
    await dp.feed_update(bot=_bot, update=update)
