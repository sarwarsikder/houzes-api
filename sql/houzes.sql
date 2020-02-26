INSERT INTO plans (id, plan_name, plan_cost, plan_coin, created_at, updated_at, created_by_id, updated_by_id, description, image) VALUES
(3,	'Free',	0.00,	0.00,	'2020-02-05 05:40:50.338374+00',	'2020-02-05 05:40:50.338374+00',	1,	NULL,	'["Our most serious, fastest-growing clients start here", "Unlimited use of our app.\nAdd Unlimited HouZes\nDrive Unlimited miles\nUpload lists from desktop\n$.10 Sherlock Owner info\n$.69 accurate Skip Tracing\n$1.69 Direct Mail post cards (no minimums)"]',	NULL),
(2,	'Team',	97.00,	97.00,	'2020-02-05 05:40:13.060587+00',	'2020-02-05 05:40:13.060587+00',	1,	NULL,	'["Our most serious, fastest-growing clients start here","Unlimited use of our app.\nAdd Unlimited HouZes\nDrive Unlimited miles\nFree ownership info\nUpload lists from desktop\n$.69 accurate Skip Tracing\n$1.69 Direct Mail post cards (no minimums)"]',	NULL),
(1,	'Solo',	47.00,	47.00,	'2020-02-05 05:39:41.020828+00',	'2020-02-05 05:39:41.020828+00',	1,	NULL,	'["Our beginner clients looking to kickstart their business start here", "Unlimited use of our app.\nAdd Unlimited HouZes\nDrive Unlimited miles\nFree ownership info\nUpload lists from desktop\n$.69 accurate Skip Tracing\n$1.69 Direct Mail post cards (no minimums)" ]',	NULL);

insert into payment_plans(payment_plan_name, payment_plan_coin, plan_id, created_at, updated_at) values
('power-trace','0.69',3,now(),now()),
('power-trace','0.20',2,now(),now()),
('power-trace','0.20',1,now(),now()),

('fetch-ownership-info','0.10',3,now(),now()),
('fetch-ownership-info','0.00',2,now(),now()),
('fetch-ownership-info','0.00',1,now(),now()),

('mailer-wizard','1.50',3,now(),now()),
('mailer-wizard','0.97',2,now(),now()),
('mailer-wizard','0.97',1,now(),now());

insert into property_tags(name, color, color_code, created_at, updated_at, user_id)values 
('Confirmed vacant', 'RED', '#FF0000', now(), now(), null),
('Visibly distressed', 'BLUE', '#0066FF', now(), now(), null),
('Overgrown yard', 'INDIGO', '#66B3FF', now(), now(), null),
('Referred by area expert', 'Green', '#00CC00', now(), now(), null),
('Spoke to neighbor', 'ORANGE', '#FF6600', now(), now(), null);

INSERT INTO "mail_wizard_subs_types" ("type_name", "days_interval", "created_at", "updated_at") VALUES
('Every Week', 7, now(), now()),
('Every Month', 30, now(), now()),
('Every Quarter', 180, now(), now());
