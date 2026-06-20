import asyncio

import asyncpg

from leaseclear.db.connection import close_pool, get_pool

MAX_ROWS = 4
MAX_CELL_WIDTH = 48


async def list_tables(conn) -> list[str]:
    rows = await conn.fetch(
        """
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY tablename
        """
    )
    return [row["tablename"] for row in rows]


async def list_columns(conn, table: str) -> list[tuple[str, str]]:
    rows = await conn.fetch(
        """
        SELECT
            a.attname AS column_name,
            pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type
        FROM pg_catalog.pg_attribute a
        JOIN pg_catalog.pg_class c ON a.attrelid = c.oid
        JOIN pg_catalog.pg_namespace n ON c.relnamespace = n.oid
        WHERE n.nspname = 'public'
          AND c.relname = $1
          AND a.attnum > 0
          AND NOT a.attisdropped
        ORDER BY a.attnum
        """,
        table,
    )
    return [(row["column_name"], row["data_type"]) for row in rows]


def format_cell(value: object) -> str:
    if value is None:
        return "NULL"

    text = str(value).replace("\n", "\\n")
    if len(text) > MAX_CELL_WIDTH:
        return f"{text[: MAX_CELL_WIDTH - 3]}..."
    return text


def print_table(
    table: str, columns: list[tuple[str, str]], rows: list[asyncpg.Record]
) -> None:
    headers = [f"{name} ({dtype})" for name, dtype in columns]
    column_names = [name for name, _ in columns]

    if not rows:
        print(f"\n=== {table} (0 rows) ===")
        for header in headers:
            print(f"  {header}")
        print("  (no rows)")
        return

    rendered_rows = [
        [format_cell(row[column_name]) for column_name in column_names] for row in rows
    ]
    widths = [
        max(len(header), *(len(row[index]) for row in rendered_rows))
        for index, header in enumerate(headers)
    ]

    print(f"\n=== {table} (showing {len(rows)} row(s)) ===")

    header_line = " | ".join(
        header.ljust(widths[index]) for index, header in enumerate(headers)
    )
    divider = "-+-".join("-" * width for width in widths)
    print(header_line)
    print(divider)
    for rendered_row in rendered_rows:
        print(
            " | ".join(
                cell.ljust(widths[index]) for index, cell in enumerate(rendered_row)
            )
        )


async def main() -> None:
    pool = await get_pool()
    try:
        async with pool.acquire() as conn:
            tables = await list_tables(conn)
            if not tables:
                print("No tables in public schema.")
                return

            for table in tables:
                columns = await list_columns(conn, table)
                rows = await conn.fetch(f'SELECT * FROM "{table}" LIMIT {MAX_ROWS}')
                print_table(table, columns, rows)
    finally:
        await close_pool()


if __name__ == "__main__":
    asyncio.run(main())
