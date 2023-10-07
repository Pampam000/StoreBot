from asyncpg import Connection, Record, UniqueViolationError

from app.api.bot_types.schemas import TypeSchema
from app.db import with_connection


@with_connection
async def get_types(conn: Connection) -> list[Record]:
    return await conn.fetch("SELECT type FROM bot_types")


@with_connection
async def add_type(conn: Connection, _type: TypeSchema) -> str:
    try:
        await conn.execute("INSERT INTO bot_types (type) values($1)",
                           _type.type)
    except UniqueViolationError as e:
        return e.detail
