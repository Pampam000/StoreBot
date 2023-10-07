from contextlib import asynccontextmanager

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.types import Update
from fastapi import FastAPI

from app import crud
from app.bot import create_webhook_bot, bots, close_bots
from app.api.bot_types.routes import router as bot_types_api_router
from app.api.bots.routes import router as bots_api_router
from app.handlers import router

dp = Dispatcher()
dp.include_router(router)


async def on_startup():
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
app.include_router(bot_types_api_router)
app.include_router(bots_api_router)


@app.post('/webhook/{token}', include_in_schema=False)
async def bot_webhook(update: dict, token: str):
    update = Update(**update)
    _bot: Bot = bots.get(token)
    await dp.feed_update(bot=_bot, update=update)
