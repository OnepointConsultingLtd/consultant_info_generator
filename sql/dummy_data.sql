delete from tb_session where session_id = '1234';

insert into tb_session(session_id, user_email) values('1234', 'anon@test.com');

insert into TB_SESSION_QUESTION(SESSION_ID, CATEGORY_QUESTION_ID)
values((select id from TB_SESSION where SESSION_ID='1234'), 
(select id from TB_CATEGORY_QUESTION order by order_index limit 1));

insert into TB_SESSION_QUESTION(SESSION_ID, CATEGORY_QUESTION_ID)
values((select id from TB_SESSION where SESSION_ID='1234'), 
(select id from TB_CATEGORY_QUESTION order by order_index offset 1 limit 1));

insert into TB_SESSION_QUESTION_RESPONSES(SESSION_QUESTION_ID, CATEGORY_ITEM_ID)
values((select sq.id from TB_SESSION_QUESTION sq
where SESSION_ID = ((select id from TB_SESSION where SESSION_ID='1234')) 
and CATEGORY_QUESTION_ID = (select id from TB_CATEGORY_QUESTION order by order_index limit 1)), 
(select id from TB_CATEGORY_ITEM where category_id = (select C.id from TB_CATEGORY C 
INNER JOIN TB_CATEGORY_QUESTION q on C.id = q.CATEGORY_ID
WHERE q.id = (select id from TB_CATEGORY_QUESTION order by order_index limit 1)) limit 1));

insert into TB_SESSION_QUESTION_RESPONSES(SESSION_QUESTION_ID, CATEGORY_ITEM_ID)
values((select sq.id from TB_SESSION_QUESTION sq
where SESSION_ID = ((select id from TB_SESSION where SESSION_ID='1234')) 
and CATEGORY_QUESTION_ID = (select id from TB_CATEGORY_QUESTION order by order_index offset 1 limit 1)), 
(select id from TB_CATEGORY_ITEM where category_id = (select C.id from TB_CATEGORY C 
INNER JOIN TB_CATEGORY_QUESTION q on C.id = q.CATEGORY_ID
WHERE q.id = (select id from TB_CATEGORY_QUESTION order by order_index offset 1 limit 1)) limit 1));

insert into TB_SESSION_QUESTION_RESPONSES(SESSION_QUESTION_ID, CATEGORY_ITEM_ID)
values((select sq.id from TB_SESSION_QUESTION sq
where SESSION_ID = ((select id from TB_SESSION where SESSION_ID='1234')) 
and CATEGORY_QUESTION_ID = (select id from TB_CATEGORY_QUESTION order by order_index offset 1 limit 1)), 
(select id from TB_CATEGORY_ITEM where category_id = (select C.id from TB_CATEGORY C 
INNER JOIN TB_CATEGORY_QUESTION q on C.id = q.CATEGORY_ID
WHERE q.id = (select id from TB_CATEGORY_QUESTION order by order_index offset 1 limit 1)) offset 1 limit 1));

insert into TB_SESSION_QUESTION_RESPONSES(SESSION_QUESTION_ID, CATEGORY_ITEM_ID)
values((select sq.id from TB_SESSION_QUESTION sq
where SESSION_ID = ((select id from TB_SESSION where SESSION_ID='1234')) 
and CATEGORY_QUESTION_ID = (select id from TB_CATEGORY_QUESTION order by order_index offset 1 limit 1)), 
(select id from TB_CATEGORY_ITEM where category_id = (select C.id from TB_CATEGORY C 
INNER JOIN TB_CATEGORY_QUESTION q on C.id = q.CATEGORY_ID
WHERE q.id = (select id from TB_CATEGORY_QUESTION order by order_index offset 1 limit 1)) offset 2 limit 1));
