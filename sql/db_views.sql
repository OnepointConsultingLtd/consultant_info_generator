DROP VIEW VW_CONSULTANT_CATEGORY_ITEM;

CREATE VIEW VW_CONSULTANT_CATEGORY_ITEM AS
SELECT
	CA.NAME CATEGORY_NAME,
	ITEM CATEGORY_ITEM,
	C.ID CONSULTANT_ID,
	GIVEN_NAME,
	SURNAME,
	LINKEDIN_PROFILE_URL
FROM
	TB_CONSULTANT C
	INNER JOIN TB_CONSULTANT_CATEGORY_ITEM_ASSIGNMENT A ON C.ID = A.CONSULTANT_ID
	INNER JOIN TB_CATEGORY_ITEM I ON I.ID = A.CATEGORY_ITEM_ID
	INNER JOIN TB_CATEGORY CA ON CA.ID = I.CATEGORY_ID
ORDER BYNAME,
	ITEM;