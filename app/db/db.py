import os
from contextlib import asynccontextmanager

import asyncpg
from asyncpg import UniqueViolationError, UndefinedTableError

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


@with_connection
async def make_migrations(conn: asyncpg.Connection):
    migration_files = sorted(os.listdir(cf.MIGRATIONS_DIR))

    for migration_file in migration_files:
        name = migration_file.split('.')[0]

        try:
            await conn.execute("INSERT INTO bot_migrations (name) VALUES ($1)",
                               name)
        except UniqueViolationError:
            continue

        except UndefinedTableError:
            pass

        with open(cf.MIGRATIONS_DIR / migration_file, "r") as f:
            migration_sql = f.read()

        await conn.execute(migration_sql)

        print(f"Выполнена миграция из файла {migration_file}")
