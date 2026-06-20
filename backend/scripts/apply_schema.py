import asyncio

from leaseclear.db.connection import apply_schema, close_pool, get_pool


async def main() -> None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        await apply_schema(conn)
    await close_pool()
    print("Schema applied.")


if __name__ == "__main__":
    asyncio.run(main())
