from asyncpg import Connection, Record

from app.db.db import with_connection


@with_connection
async def get_tokens(conn: Connection) -> list[str]:
    tokens: list[Record] = await conn.fetch("""SELECT token FROM bot_bots""")
    return [token['token'] for token in tokens]


@with_connection
async def get_state_messages(
        conn: Connection,
        state_name: str = None,
        with_inline_kb: bool = False,
        with_reply_kb: bool = False) -> (list, dict, list):
    query = """
        SELECT {} FROM bot_message_groups bmg
        JOIN bot_messages bm ON bmg.id = bm.message_group_id
        """

    select_string = 'bm.*, bmg.state_name'
    if with_inline_kb:
        query += ' LEFT JOIN bot_keyboards bk ON bm.id = bk.message_id'
        select_string += ', bk.id as keyboard_id'

    query = query.format(select_string)

    if state_name:
        query += " WHERE bmg.state_name LIKE $1"

    query += " ORDER BY bm.message_group_id, bm.priority"
    messages: list[Record] = await conn.fetch(query, f"%{state_name}%")

    all_inline_buttons = {}
    if with_inline_kb:
        for message in messages:
            if not message['keyboard_id']:
                continue

            inline_buttons: list[Record] = await conn.fetch(
                """
                SELECT * FROM bot_buttons
                WHERE keyboard_id = $1
                """,
                message['keyboard_id']
            )
            all_inline_buttons[message['id']] = inline_buttons

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

    return messages, all_inline_buttons, reply_buttons
