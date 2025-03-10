import logging

from consultant_info_generator.model.model import (
    Company,
    Consultant,
    Experience,
    Skill,
)
from consultant_info_generator.model.category import Category
from consultant_info_generator.model.questions import CategoryQuestion
from consultant_info_generator.model.category_assignments import (
    ProfileCategoryAssignment,
)
from psycopg import AsyncCursor

from consultant_info_generator.service.query_support import create_cursor, select_from

logger = logging.getLogger(__name__)

async def __process_simple_operation(sql: str, skill: str) -> int:
    async def process(cur: AsyncCursor):
        await cur.execute(sql, {"skill": skill})
        return cur.rowcount

    return await create_cursor(process, True)


async def upsert_skill(skill: str) -> int:
    sql = """
INSERT INTO TB_SKILL (SKILL_NAME) VALUES (%(skill)s) ON CONFLICT (SKILL_NAME) DO NOTHING;
"""
    return await __process_simple_operation(sql, skill)


async def delete_skill(skill: str) -> int:
    sql = """
DELETE FROM TB_SKILL WHERE SKILL_NAME = %(skill)s
"""
    return await __process_simple_operation(sql, skill)


async def save_consultant(consultant: Consultant) -> int | None:
    async def process(cur: AsyncCursor):
        sql = """
INSERT INTO TB_CONSULTANT(GIVEN_NAME, SURNAME, EMAIL, CV, INDUSTRY_NAME, GEO_LOCATION, LINKEDIN_PROFILE_URL)
VALUES(%(given_name)s, %(surname)s, %(email)s, %(cv)s, %(industry_name)s, %(location)s, %(linkedin_profile_url)s)
ON CONFLICT (EMAIL) DO UPDATE SET GIVEN_NAME=%(given_name)s, SURNAME=%(surname)s, EMAIL=%(email)s, CV=%(cv)s, INDUSTRY_NAME=%(industry_name)s, 
GEO_LOCATION=%(location)s, LINKEDIN_PROFILE_URL=%(linkedin_profile_url)s, UPDATED_AT=CURRENT_TIMESTAMP RETURNING ID;
"""
        await cur.execute(
            sql,
            {
                "given_name": consultant.given_name,
                "surname": consultant.surname,
                "email": consultant.email,
                "cv": consultant.cv,
                "industry_name": consultant.industry_name,
                "location": consultant.geo_location,
                "linkedin_profile_url": consultant.linkedin_profile_url,
            },
        )
        rows = await cur.fetchone()
        if rows is None or len(rows) == 0:
            return None
        consultant_id = rows[0]

        sql = """DELETE FROM TB_CONSULTANT_SKILL WHERE CONSULTANT_ID = %(consultant_id)s"""
        await cur.execute(sql, {"consultant_id": consultant_id})

        sql = """
INSERT INTO TB_SKILL(SKILL_NAME) VALUES(%(skill)s)
ON CONFLICT (SKILL_NAME) DO NOTHING
"""
        for skill in consultant.skills:
            await cur.execute(sql, {"skill": skill.name})

        sql = """
INSERT INTO TB_CONSULTANT_SKILL(CONSULTANT_ID, SKILL_ID) VALUES(%(consultant_id)s, (SELECT ID from TB_SKILL WHERE SKILL_NAME = %(skill_name)s))
ON CONFLICT (CONSULTANT_ID, SKILL_ID) DO NOTHING
"""
        for skill in consultant.skills:
            await cur.execute(
                sql, {"consultant_id": consultant_id, "skill_name": skill.name}
            )

        company_sql = """
INSERT INTO TB_COMPANY(COMPANY_NAME) VALUES(%(company_name)s)
ON CONFLICT (COMPANY_NAME) DO NOTHING
"""
        experience_sql = """
INSERT INTO TB_CONSULTANT_EXPERIENCE(CONSULTANT_ID, TITLE, LOCATION, START_DATE, END_DATE, COMPANY_ID)
VALUES(%(consultant_id)s, %(title)s, %(location)s, %(start_date)s, %(end_date)s, (SELECT ID FROM TB_COMPANY WHERE COMPANY_NAME = %(company_name)s))
"""
        for experience in consultant.experiences:
            if experience.company:
                company_name = experience.company.name
                await cur.execute(company_sql, {"company_name": company_name})
                await cur.execute(
                    experience_sql,
                    {
                        "consultant_id": consultant_id,
                        "title": experience.title,
                        "location": experience.location,
                        "start_date": experience.start,
                        "end_date": experience.end,
                        "company_name": experience.company.name,
                    },
                )

    return await create_cursor(process, True)


async def delete_consultant(consultant: Consultant) -> int:
    async def process(cur: AsyncCursor):
        sql = """
DELETE FROM TB_CONSULTANT WHERE EMAIL=%(email)s
"""
        await cur.execute(sql, {"email": consultant.email})
        return cur.rowcount

    return await create_cursor(process, True)


async def delete_consultant_by_profile_id(profile_id: str) -> int:
    async def process(cur: AsyncCursor):
        sql = """
DELETE FROM TB_CONSULTANT WHERE LINKEDIN_PROFILE_URL=%(profile_id)s
"""
        await cur.execute(
            sql, {"profile_id": f"https://www.linkedin.com/in/{profile_id}"}
        )
        return cur.rowcount

    return await create_cursor(process, True)


async def read_consultants(offset: int = None, limit: int = None) -> list[Consultant]:
    splitter = "@@"
    offset_expression = f"OFFSET {offset}" if offset else ""
    limit_expression = f"LIMIT {limit}" if limit else ""
    consultant_sql = f"""
select C.ID, C.GIVEN_NAME, C.SURNAME, C.EMAIL, C.CV, C.INDUSTRY_NAME, C.GEO_LOCATION, C.LINKEDIN_PROFILE_URL,
string_agg(S.SKILL_NAME, '{splitter}') skills from TB_CONSULTANT C 
INNER JOIN TB_CONSULTANT_SKILL CS ON C.ID = CS.CONSULTANT_ID
INNER JOIN TB_SKILL S ON S.ID = CS.SKILL_ID
GROUP BY C.ID, C.GIVEN_NAME, C.SURNAME, C.EMAIL, C.CV, C.INDUSTRY_NAME, C.GEO_LOCATION, C.LINKEDIN_PROFILE_URL
{offset_expression} {limit_expression}
"""
    experience_sql = """
SELECT TITLE, LOCATION, START_DATE, END_DATE, CO.COMPANY_NAME FROM TB_CONSULTANT_EXPERIENCE E
INNER JOIN TB_CONSULTANT C ON C.ID = E.CONSULTANT_ID
INNER JOIN TB_COMPANY CO ON CO.ID = E.COMPANY_ID
WHERE C.ID = %(consultant_id)s
"""
    rows = await select_from(consultant_sql, {})
    consultant_id = 0
    consultant_given_name = 1
    consultant_surname = 2
    consultant_email = 3
    consultant_cv = 4
    consultant_industry_name = 5
    consultant_geo_location = 6
    consultant_linkedin_profile_url = 7
    consultant_skills = 8
    consultants = []

    experience_title = 0
    experience_location = 1
    experience_start_date = 2
    experience_end_date = 3
    experience_company = 4
    for r in rows:
        id = r[consultant_id]
        skills_str = r[consultant_skills]
        skills = [Skill(name=s) for s in skills_str.split(splitter)]
        experience_rows = await select_from(experience_sql, {"consultant_id": id})
        experiences = [
            Experience(
                title=e[experience_title],
                location=e[experience_location],
                start=e[experience_start_date],
                end=e[experience_end_date],
                company=Company(name=e[experience_company]),
            )
            for e in experience_rows
        ]
        consultants.append(
            Consultant(
                given_name=r[consultant_given_name],
                surname=r[consultant_surname],
                email=r[consultant_email],
                cv=r[consultant_cv],
                industry_name=r[consultant_industry_name],
                geo_location=r[consultant_geo_location],
                linkedin_profile_url=r[consultant_linkedin_profile_url],
                experiences=experiences,
                skills=skills,
            )
        )
    return consultants


async def save_category(category: Category) -> int | None:
    async def process(cur: AsyncCursor):
        sql = """
INSERT INTO TB_CATEGORY(NAME, DESCRIPTION) VALUES(%(name)s, %(description)s)
ON CONFLICT (NAME) DO UPDATE SET DESCRIPTION=%(description)s RETURNING ID;
"""
        await cur.execute(
            sql, {"name": category.name, "description": category.description}
        )
        rows = await cur.fetchone()
        if rows is None or len(rows) == 0:
            return None
        category_id = rows[0]

        sql = """
INSERT INTO TB_CATEGORY_ITEM(CATEGORY_ID, ITEM) VALUES(%(category_id)s, %(item)s)
ON CONFLICT (CATEGORY_ID, ITEM) DO NOTHING
"""
        for value in category.list_of_values:
            await cur.execute(sql, {"category_id": category_id, "item": value})
        return category_id

    return await create_cursor(process, True)


async def delete_category(category: Category) -> int:
    async def process(cur: AsyncCursor):
        sql = """
DELETE FROM TB_CATEGORY WHERE NAME=%(name)s"""
        await cur.execute(sql, {"name": category.name})
        return cur.rowcount

    return await create_cursor(process, True)


async def read_categories() -> list[Category]:
    sql = """
SELECT NAME, DESCRIPTION, ITEM FROM TB_CATEGORY C INNER JOIN TB_CATEGORY_ITEM CI ON C.ID = CI.CATEGORY_ID
ORDER BY C.NAME
"""
    rows = await select_from(sql, {})
    categories = []
    current_category = None
    category_name = 0
    category_description = 1
    category_item = 2
    for r in rows:
        if current_category is None or current_category.name != r[category_name]:
            current_category = Category(
                name=r[category_name],
                description=r[category_description],
                list_of_values=[],
            )
            categories.append(current_category)
            current_category.list_of_values.append(r[category_item])
        else:
            current_category.list_of_values.append(r[category_item])
    return categories


async def save_category_question(question: CategoryQuestion) -> int | None:
    async def process(cur: AsyncCursor):
        await save_category(question)
        sql = """
INSERT INTO TB_CATEGORY_QUESTION(CATEGORY_ID, QUESTION) VALUES((SELECT ID FROM TB_CATEGORY WHERE NAME = %(category_name)s), %(question)s)
RETURNING ID;
"""
        await cur.execute(
            sql, {"category_name": question.name, "question": question.question}
        )
        rows = await cur.fetchone()
        return None if rows is None or len(rows) == 0 else rows[0]

    return await create_cursor(process, True)


async def delete_category_question(question: CategoryQuestion) -> int:
    async def process(cur: AsyncCursor):
        sql = """
DELETE FROM TB_CATEGORY_QUESTION WHERE CATEGORY_ID = (SELECT ID FROM TB_CATEGORY WHERE NAME = %(category_name)s) AND QUESTION = %(question)s
"""
        await cur.execute(
            sql, {"category_name": question.name, "question": question.question}
        )
        deleted_questions = cur.rowcount
        deleted_category = await delete_category(question)
        return deleted_questions + deleted_category

    return await create_cursor(process, True)


async def save_profile_category_assignment(
    assignment: ProfileCategoryAssignment,
) -> int | None:
    async def process(cur: AsyncCursor):
        item_sql = """
SELECT ID FROM TB_CATEGORY_ITEM WHERE CATEGORY_ID = (SELECT ID FROM TB_CATEGORY WHERE LOWER(NAME) = LOWER(%(category_name)s)) AND LOWER(ITEM) = LOWER(%(category_element)s)
"""
        rows = await select_from(item_sql, {"category_name": assignment.category_name, "category_element": assignment.category_element})
        if rows is None or len(rows) == 0:
            logger.error(f"Category item not found: {assignment.category_name} {assignment.category_element}")
            simplefied_item_sql = """
SELECT ID FROM TB_CATEGORY_ITEM WHERE LOWER(ITEM) = LOWER(%(category_element)s)
"""
            rows = await select_from(simplefied_item_sql, {"category_element": assignment.category_element})
            if rows is None or len(rows) != 1:
                logger.error(f"Category item not found again: for {assignment.category_element}")
                return None
            category_item_id = rows[0][0]
        else:
            category_item_id = rows[0][0]
        sql = """
INSERT INTO TB_CONSULTANT_CATEGORY_ITEM_ASSIGNMENT(CONSULTANT_ID, CATEGORY_ITEM_ID, REASON) 
VALUES(
    (select id from tb_consultant where linkedin_profile_url = %(profile_url)s), 
    %(category_item_id)s,
    %(reason)s
)
ON CONFLICT (CONSULTANT_ID, CATEGORY_ITEM_ID) DO NOTHING RETURNING ID;
"""
        await cur.execute(
            sql,
            {
                "profile_url": (
                    f"https://www.linkedin.com/in/{assignment.profile}"
                    if "linkedin" not in assignment.profile
                    else assignment.profile
                ),
                "category_name": assignment.category_name,
                "category_item_id": category_item_id,
                "reason": assignment.reason,
            },
        )
        rows = await cur.fetchone()
        return None if rows is None or len(rows) == 0 else rows[0]

    return await create_cursor(process, True)


async def delete_profile_category_assignment(
    assignment: ProfileCategoryAssignment,
) -> int | None:
    async def process(cur: AsyncCursor):
        sql = """
DELETE FROM TB_CONSULTANT_CATEGORY_ITEM_ASSIGNMENT 
WHERE CONSULTANT_ID = (SELECT ID FROM TB_CONSULTANT WHERE LINKEDIN_PROFILE_URL = %(profile_url)s) 
AND CATEGORY_ITEM_ID = (SELECT ID FROM TB_CATEGORY_ITEM WHERE CATEGORY_ID = (SELECT ID FROM TB_CATEGORY WHERE LOWER(NAME) = LOWER(%(category_name)s)) AND LOWER(ITEM) = LOWER(%(category_element)s))
"""
        await cur.execute(
            sql,
            {
                "profile_url": (
                    f"https://www.linkedin.com/in/{assignment.profile}"
                    if "linkedin" not in assignment.profile
                    else assignment.profile
                ),
                "category_name": assignment.category_name,
                "category_element": assignment.category_element,
            },
        )

    return await create_cursor(process, True)
