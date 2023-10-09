CREATE TABLE IF NOT EXISTS bot_migrations (
    name VARCHAR(255) PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS bot_types (
    type VARCHAR(50) PRIMARY KEY
    );

CREATE TABLE IF NOT EXISTS bot_bots (
    token VARCHAR(100) PRIMARY KEY,
    type VARCHAR(50) NOT NULL,

    FOREIGN KEY (type) REFERENCES bot_types(type)
    );


CREATE TABLE IF NOT EXISTS bot_states(
    name VARCHAR(50) PRIMARY KEY,
    priority SMALLINT DEFAULT 1 NOT NULL
    );

------------------------------------------------------
CREATE TABLE IF NOT EXISTS bot_message_groups(
    id SERIAL PRIMARY KEY,
    state_name VARCHAR(50) UNIQUE NOT NULL,

    FOREIGN KEY (state_name) REFERENCES bot_states(name)
    );

CREATE TABLE IF NOT EXISTS bot_messages(
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    priority SMALLINT NOT NULL,
    message_group_id INT NOT NULL,

    UNIQUE (priority, message_group_id),
    FOREIGN KEY (message_group_id) REFERENCES bot_message_groups(id)
    );

CREATE TABLE IF NOT EXISTS bot_keyboard_types(
    type VARCHAR(10) PRIMARY KEY
    );

CREATE TABLE IF NOT EXISTS bot_keyboards(
    id SERIAL PRIMARY KEY,
    type VARCHAR(10) NOT NULL,
    message_id INT,
    state_name VARCHAR(50),

    FOREIGN KEY (type) REFERENCES bot_keyboard_types(type),
    FOREIGN KEY (message_id) REFERENCES bot_messages(id),
    FOREIGN KEY (state_name) REFERENCES bot_states(name)
    );


CREATE TABLE IF NOT EXISTS bot_buttons (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    text VARCHAR(50) NOT NULL,
    keyboard_id INT NOT NULL,

    FOREIGN KEY (keyboard_id) REFERENCES bot_keyboards(id)
    );
