import asyncio

from leaseclear.db.connection import apply_schema, close_pool, db_session


async def main() -> None:
    async with db_session():
        await apply_schema()
    await close_pool()
    print("Schema applied.")


if __name__ == "__main__":
    asyncio.run(main())
