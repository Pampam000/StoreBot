INSERT INTO bot_types (type)
VALUES ('general'), ('individual'), ('list'), ('distributor'),
('autoresponder'), ('service');

INSERT INTO bot_states (name)
VALUES ('Register:start'),('Register:enter_password');

INSERT INTO bot_keyboard_types (type)
VALUES ('reply'), ('inline');

INSERT INTO bot_message_groups (state_name) VALUES
('Register:start'), ('Register:enter_password');


INSERT INTO bot_messages (name, text, message_group_id) VALUES
('enter_password', 'Здравствуйте, введите ваш пароль:', 1),
('incorrect_password_3_times', 'Вы ввели неверно пароль 3 раза', 2),
('incorrect_paasword', 'Вы ввели неверный пароль', 2),
('correct_password', 'Вы ввели верный пароль', 2);

INSERT INTO bot_keyboards (type, state_name) VALUES
('reply', 'Register:start'),('reply','Register:enter_password');




