from asyncpg import Connection, Record

from app.db import with_connection


@with_connection
async def get_tokens(conn: Connection) -> list[str]:
    tokens: list[Record] = await conn.fetch("""SELECT token FROM bot_bots""")
    return [token['token'] for token in tokens]
