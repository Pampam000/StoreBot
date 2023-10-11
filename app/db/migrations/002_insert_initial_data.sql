INSERT INTO bot_types (type)
VALUES ('general'), ('individual'), ('list'), ('distributor'),
('autoresponder'), ('service');

INSERT INTO bot_states (name) VALUES
('Register:start'),

('Register:password:incorrect_3_times'),
('Register:password:incorrect'),
('Register:password:correct'),

('Register:choose_option:referral_code'),

('Register:referral_code:incorrect'),
('Register:referral_code:used'),
('Register:referral_code:correct'),

('Location:start'),
('Location:country'),
('Location:federal_region'),
('Location:region'),
('Location:city'),
('Location:district'),
('Location:micro_district'),
('Location:micro_district:success');



INSERT INTO bot_keyboard_types (type)
VALUES ('reply'), ('inline');

INSERT INTO bot_message_groups (state_name) VALUES
('Register:start'),

('Register:password:incorrect_3_times'),
('Register:password:incorrect'),
('Register:password:correct'),

('Register:choose_option:referral_code'),

('Register:referral_code:incorrect'),
('Register:referral_code:used'),
('Register:referral_code:correct'),

('Location:start'),
('Location:country'),
('Location:federal_region'),
('Location:region'),
('Location:city'),
('Location:district'),
('Location:micro_district'),
('Location:micro_district:success');

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
('Реферальный код успешно активирован!', 1, 8),
--16
('Укажите страну', 1, 9),
--17
('Укажите федеральный регион', 1, 10),
--18
('укажите область', 1, 11),
--19
('Укажите город', 1, 12),
--20
('Укажите район', 1, 13),
--21
('Укажите микрорайон', 1, 14),
--22
('Вы успешно установили локацию', 1, 15);
--23

INSERT INTO bot_keyboards (type, message_id, state_name) VALUES
('inline', 9, null),
('inline', 10, null),
('inline', 16, null),
('reply', null, 'Location:start');


INSERT INTO bot_buttons (name, text, keyboard_id) VALUES
('location', 'location', 1),
('referral code', 'referral code', 2),
('to catalog', 'to catalog', 3),
('save', 'save', 4),
('forward', 'forward', 4),
('backward', 'backward', 4);
