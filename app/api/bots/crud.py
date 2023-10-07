from asyncpg import Connection, Record, ForeignKeyViolationError

from app.db.db import with_connection
from .schemas import BotSchema


@with_connection
async def get_bots(conn: Connection) -> list[Record]:
    bots: list[Record] = \
        await conn.fetch("SELECT token, type FROM bot_bots")
    return bots


@with_connection
async def add_bot(conn: Connection, bot: BotSchema) -> str:
    try:
        await conn.execute(
            "INSERT INTO bot_bots (token, type) values($1, $2)",
            bot.token, bot.type)
    except ForeignKeyViolationError as e:
        return e.detail
