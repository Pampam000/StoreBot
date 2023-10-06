CREATE TABLE IF NOT EXISTS bot_types (
    type VARCHAR(50) PRIMARY KEY
    );

CREATE TABLE IF NOT EXISTS bot_bots (
    token VARCHAR(100) PRIMARY KEY,
    type VARCHAR(50) NOT NULL,

    FOREIGN KEY (type) REFERENCES bot_types(type)
    );

CREATE TABLE IF NOT EXISTS bot_state_groups (
    name VARCHAR(50) PRIMARY KEY
    );

CREATE TABLE IF NOT EXISTS bot_states (
    name VARCHAR(50) PRIMARY KEY,
    bot_token VARCHAR(100) NOT NULL,
    state_group_name VARCHAR(50) NOT NULL,
    message TEXT,
    priority SMALLINT,

    FOREIGN KEY (state_group_name) REFERENCES bot_state_groups(name),
    FOREIGN KEY (bot_token) REFERENCES bot_bots(token)
    );

CREATE TABLE IF NOT EXISTS bot_buttons (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL
    );

CREATE TABLE IF NOT EXISTS bot_bots_states_buttons (
    id BIGSERIAL PRIMARY KEY,
    state_name VARCHAR(50) NOT NULL,
    button_id BIGINT NOT NULL,
    bot_token VARCHAR(100) NOT NULL,

    FOREIGN KEY (state_name) REFERENCES bot_states(name),
    FOREIGN KEY (button_id) REFERENCES bot_buttons(id),
    FOREIGN KEY (bot_token) REFERENCES bot_bots(token)
);
