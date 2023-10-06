from contextlib import asynccontextmanager

import asyncpg

from app import config as cf


async def get_conn():
    conn: asyncpg.Connection = await asyncpg.connect(
        user=cf.POSTGRES_USER,
        password=cf.POSTGRES_PASSWORD,
        host=cf.POSTGRES_HOST,
        database=cf.POSTGRES_DB,
        port=cf.POSTGRES_PORT)

    return conn


@asynccontextmanager
async def get_connection():
    conn = await get_conn()
    try:
        yield conn
    finally:
        await conn.close()


def with_connection(func):
    async def wrapper(*args, **kwargs):
        async with get_connection() as conn:
            return await func(conn=conn, *args, **kwargs)

    return wrapper

