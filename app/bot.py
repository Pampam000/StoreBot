from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramAPIError
from aiogram.utils.token import TokenValidationError

from app import config as cf

bots = {}


async def create_webhook_bot(token: str) -> str:
    try:
        bot = Bot(token=token, session=AiohttpSession(timeout=5))
        await set_webhook(bot=bot)
        bots[bot.token] = bot
    except (TokenValidationError, TelegramAPIError) as e:
        return str(e)


async def set_webhook(bot: Bot):
    token_path = f"/{bot.token}"
    webhook_url = cf.WEBHOOK_HOST + cf.WEBHOOK_PATH + token_path
    await bot.set_webhook(url=webhook_url, drop_pending_updates=True)


async def close_bot(token: str):
    _bot: Bot = bots[token]
    await _bot.delete_webhook()
    await _bot.session.close()


async def close_bots():
    for token in bots:
        await close_bot(token=token)
