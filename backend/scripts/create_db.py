import argparse
import asyncio

from leaseclear.core.config import settings
from leaseclear.db.admin import create_database


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--eval",
        action="store_true",
        help="use EVAL_DATABASE_URL instead of DATABASE_URL",
    )
    return parser.parse_args()


async def main() -> None:
    args = _parse_args()
    database_url = settings.eval_database_url if args.eval else settings.database_url
    await create_database(database_url)
    print(f"Database ready at {database_url}")


if __name__ == "__main__":
    asyncio.run(main())
