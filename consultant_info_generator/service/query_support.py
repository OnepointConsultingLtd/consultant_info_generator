import asyncio
import sys
from typing import Any, Awaitable, Coroutine

from psycopg import AsyncConnection, AsyncCursor

from consultant_info_generator.config import db_cfg
from consultant_info_generator.logger import logger

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def create_connection(conninfo: str = db_cfg.db_conn_str) -> AsyncConnection:
    return await AsyncConnection.connect(conninfo)


async def create_cursor(func: Awaitable, commit=False, conn_info: str = None) -> Any:
    try:
        conn = (
            (await create_connection())
            if conn_info is None
            else (await create_connection(conn_info))
        )
        # async with asynch_pool.connection() as conn:
        async with conn.cursor() as cur:
            return await func(cur)
    except Exception as e:
        logger.error(str(e))
        logger.exception("Could not create cursor.")
        return None
    finally:
        if "conn" in locals() and conn is not None:
            if commit:
                await conn.commit()
            await conn.close()


async def use_connection(func: Coroutine, commit=True) -> any:
    try:
        conn = await create_connection()
        return await func(conn)
    except Exception as e:
        logger.exception(f"Could not create database connection: {e}")
    finally:
        if conn is not None:
            if commit:
                await conn.commit()
            await conn.close()


async def handle_select_func(query: str, query_params: dict):
    async def func(cur: AsyncCursor):
        await cur.execute(
            query,
            query_params,
        )
        return list(await cur.fetchall())

    return func


async def select_from(query: str, parameter_map: dict, conn_info: str = None) -> list:
    handle_select = await handle_select_func(query, parameter_map)
    return await create_cursor(handle_select, False, conn_info)
