import argparse
import asyncio

from leaseclear.core.config import settings
from leaseclear.db.seed import DEMO_EMAIL, seed_database


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
    user_id, pdf_count, chunk_count = await seed_database(database_url)
    print(f"Seeded {database_url}")
    print(f"  demo user: {DEMO_EMAIL} ({user_id})")
    print(f"  documents: {pdf_count}")
    print(f"  chunks: {chunk_count}")


if __name__ == "__main__":
    asyncio.run(main())
