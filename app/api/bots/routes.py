from fastapi import APIRouter, HTTPException

from app.bot import create_webhook_bot, bots, close_bot
from . import crud
from .schemas import BotSchema

router = APIRouter(prefix='/bot',
                   tags=['bot'])


@router.get('/')
async def get_bots():
    return await crud.get_bots()


@router.post('/')
async def add_bot(bot: BotSchema):
    # check bot existence
    if bot.token in bots:
        raise HTTPException(status_code=400,
                            detail=f"Key (token)=({bot.token}) already exists."
                            )

    # validate token and start webhook
    if detail := await create_webhook_bot(bot.token):
        raise HTTPException(status_code=400, detail=detail)

    # check foreign key violation and add bot to db or close webhook
    if detail := await crud.add_bot(bot=bot):
        await close_bot(token=bot.token)
        raise HTTPException(status_code=400, detail=detail)

    return bot
