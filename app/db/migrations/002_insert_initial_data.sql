INSERT INTO bot_types (type)
VALUES ('general'), ('individual'), ('list'), ('distributor'),
('autoresponder'), ('service');

INSERT INTO bot_states (name) VALUES
('Register:start'),

('Register:enter_password:incorrect_3_times'),
('Register:enter_password:incorrect'),
('Register:enter_password:correct'),

('Register:choose_option:referral_code'),

('Register:enter_referral_code:incorrect'),

('Register:enter_referral_code:used'),

('Register:enter_referral_code:correct');


INSERT INTO bot_keyboard_types (type)
VALUES ('reply'), ('inline');

INSERT INTO bot_message_groups (state_name) VALUES
('Register:start'),

('Register:enter_password:incorrect_3_times'),
('Register:enter_password:incorrect'),
('Register:enter_password:correct'),

('Register:choose_option:referral_code'),

('Register:enter_referral_code:incorrect'),

('Register:enter_referral_code:used'),

('Register:enter_referral_code:correct');



INSERT INTO bot_messages (text, priority, message_group_id) VALUES
('Здравствуйте!', 1, 1),
('Введите ваш пароль:',2, 1),
--2
('Вы ввели неверный пароль',1, 2),
('После 3 попытки вы будете заблокированы на 5 минут', 2, 2),
('Попробуйте ещё раз', 3, 2),
--5
('Вы ввели неверно пароль 3 раза',1, 3),
('Вы заблокированы на 5 минут', 2, 3),
--7
('Вы ввели верный пароль',1, 4),
('Чтобы указать локацию нажмите сюда', 2, 4),
('Чтобы указать реф.код нажмите сюда', 3, 4),
--10
('Введите ваш реферальный код', 1, 5),
--11
('Введённый вами реферальный код не верный.', 1, 6),
('Введите код ещё раз', 2, 6),
--13
('Введённый вами реферальный код уже использовался.', 1, 7),
('Введите другой код', 2, 7),
--15
('Реферальный код успешно активирован!', 1, 8);
--16
INSERT INTO bot_keyboards (type, message_id, state_name) VALUES
('inline', 9, null),
('inline', 10, null),
('inline', 16, null);


INSERT INTO bot_buttons (name, text, keyboard_id) VALUES
('locality', 'locality', 1),
--('choose later', 'choose later', 1),
('referral code', 'referral code', 2),
('to catalog', 'to catalog', 3);