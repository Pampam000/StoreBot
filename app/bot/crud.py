from asyncpg import Connection, Record

from app.db.db import with_connection


@with_connection
async def get_tokens(conn: Connection) -> list[str]:
    tokens: list[Record] = await conn.fetch("""SELECT token FROM bot_bots""")
    return [token['token'] for token in tokens]

@with_connection
async def get_state_messages(conn: Connection,
                             state_name: str,
                             with_inline_kb: bool,
                             with_reply_kb: bool) -> (list, list, list):
    messages: list[Record] = await conn.fetch(
        """
        SELECT bm.* FROM bot_message_groups bmg
        JOIN bot_messages bm ON bmg.id = bm.message_group_id
        WHERE bmg.state_name = $1
        """,
        state_name
    )

    inline_buttons = []
    if with_inline_kb:
        inline_buttons: list[Record] = await conn.fetch(
            """
            SELECT bb.* FROM bot_keyboards bk
            JOIN bot_buttons bb ON bk.id = bb.keyboard_id
            WHERE bk.message_id = $1
            """,
            messages[0]['id']
        )

    reply_buttons = []
    if with_reply_kb:
        reply_buttons: list[Record] = await conn.fetch(
            """
            SELECT bb.* FROM bot_keyboards bk
            JOIN bot_buttons bb ON bk.id = bb.keyboard_id
            WHERE state_name = $1
            """,
            state_name
        )

    return messages, inline_buttons, reply_buttons