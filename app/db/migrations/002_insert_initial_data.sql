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

('Location:start:inline'),
('Location:start'),

('Location:country:inline'),
('Location:country'),
('Location:country:not_found'),

('Location:federal_region:inline'),
('Location:federal_region'),
('Location:federal_region:not_found'),

('Location:region:inline'),
('Location:region'),
('Location:region:not_found'),

('Location:city:inline'),
('Location:city'),
('Location:city:not_found'),

('Location:district'),
('Location:district:not_found'),

('Location:micro_district'),
('Location:micro_district:not_found'),
('Location:micro_district:success');


INSERT INTO bot_keyboard_types (type)
VALUES ('reply'), ('inline');

INSERT INTO bot_message_groups (state_name) VALUES
('Register:start'),

('Register:password:incorrect_3_times'),
('Register:password:incorrect'),
('Register:password:correct'),
--4
('Register:choose_option:referral_code'),

('Register:referral_code:incorrect'),
('Register:referral_code:used'),
('Register:referral_code:correct'),
--8
('Location:start:inline'),
('Location:start'),
--10
('Location:country:not_found'),
('Location:country:inline'),
('Location:country'),
--13
('Location:federal_region:not_found'),
('Location:federal_region:inline'),
('Location:federal_region'),
--16
('Location:region:not_found'),
('Location:region:inline'),
('Location:region'),
--19

('Location:city:not_found'),
('Location:city:inline'),
('Location:city'),
--22

('Location:district'),
('Location:district:not_found'),
--24
('Location:micro_district'),
('Location:micro_district:not_found'),
('Location:micro_district:success');
--27
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
('Или введите вручную:', 1, 10),
('Такой страны нет', 1, 11),
--19
('Укажите федеральный регион', 1, 12),
('Или введите вручную:', 1, 13),
('Такого региона нет', 1, 14),
--22
('укажите область', 1, 15),
('Или введите вручную:', 1, 16),
('Такой области нет', 1, 17),
--25
('Укажите город', 1, 18),
('Или введите вручную:', 1, 19),
('Такого города нет', 1, 20),
--28
('Укажите район', 1, 21),
--('Или введите вручную:', 2, 13),
('Такого района нет', 1, 22),
--30
('Укажите микрорайон', 1, 23),
--('Или введите вручную:', 2, 14),
('Такого микрорайона нет', 1, 24),
--32
('Вы успешно установили локацию', 1, 27);
--33

INSERT INTO bot_keyboards (type, message_id, state_name) VALUES
('inline', 9, null),
('inline', 10, null),
('inline', 16, null),
('reply', null, 'Location:start'),
('inline', 33, null);



INSERT INTO bot_buttons (name, text, keyboard_id) VALUES
('location', 'location', 1),
('referral code', 'referral code', 2),
('to catalog', 'to catalog', 3),
('save', 'save', 4),
('forward', 'forward', 4),
('backward', 'backward', 4),
('to catalog', 'to catalog', 5);

