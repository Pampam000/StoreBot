from asyncpg import Connection, Record, ForeignKeyViolationError

from app.db.db import with_connection
from .schemas import UpdateOrder, AddMessageSchema


@with_connection
async def get_states(conn: Connection) -> list[Record]:
    return await conn.fetch('SELECT * FROM bot_states')


@with_connection
async def add_message(conn: Connection,
                      message: AddMessageSchema,
                      message_group_id: int):
    updates = await conn.fetch(
        """
        UPDATE bot_messages SET priority = priority + 100
        WHERE priority >= $1 AND message_group_id = $2
        RETURNING id
        """,
        message.priority, message_group_id)

    await conn.execute(
        """
        INSERT INTO bot_messages (text, priority, message_group_id)
        VALUES ($1, $2, $3) 
        """,
        message.text, message.priority, message_group_id)

    if updates:
        await conn.execute(
            """
            UPDATE bot_messages SET priority = priority - 99
            WHERE priority > 100
            """
        )


@with_connection
async def update_message_text(conn: Connection,
                              message_id: int,
                              text: str) -> Record:
    return await conn.fetchrow(
        """
        UPDATE bot_messages SET text = $1 WHERE id = $2 RETURNING *
        """,
        text, message_id)


@with_connection
async def update_order(conn: Connection,
                       order: UpdateOrder,
                       message_group_id: int):
    result = await conn.fetch(
        """
        SELECT * FROM bot_messages 
        WHERE message_group_id = $1
        """,
        message_group_id
    )

    await conn.execute(
        """
        UPDATE bot_messages SET priority = priority + 100
        WHERE message_group_id = $1
        """,
        message_group_id
    )

    for num, message in enumerate(order.order):
        minus = 100 - message.priority + 1 + (result[num]['priority'] - 1)
        await conn.execute(
            """
            UPDATE bot_messages SET priority = priority - $1
            WHERE message_group_id = $2 AND id = $3
            """,
            minus,
            message_group_id,
            message.message_id
        )


@with_connection
async def delete_message(conn: Connection, message_id: int):
    try:
        result: Record = await conn.fetchrow(
            """
            DELETE FROM bot_messages WHERE id = $1
            RETURNING priority, message_group_id
            """,
            message_id)
    except ForeignKeyViolationError:
        return 'Could not delete message with inline keyboard'

    await conn.execute(
        """
        UPDATE bot_messages SET priority = priority - 1 
        WHERE priority > $1 AND message_group_id = $2
        """,
        result['priority'], result['message_group_id']
    )


@with_connection
async def get_message_buttons(conn: Connection,
                              message_id: int) -> list[Record]:
    return await conn.fetch(
        """
        SELECT bb.* FROM bot_buttons bb
        JOIN bot_keyboards bk ON bb.keyboard_id = bk.id
        WHERE bk.message_id = $1
        """,
        message_id
    )


@with_connection
async def update_button(conn: Connection,
                        button_id: int,
                        text: str) -> Record:
    return await conn.fetchrow(
        "UPDATE bot_buttons SET text = $1 WHERE id = $2 RETURNING *",
        text, button_id)
