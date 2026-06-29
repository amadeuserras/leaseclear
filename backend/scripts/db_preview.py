import asyncio

import asyncpg

from leaseclear.db.connection import close_pool, get_pool

MAX_ROWS = 4
MAX_CELL_WIDTH = 48
MAX_COMPACT_CELL_WIDTH = 8


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


def is_compact_column(name: str, dtype: str) -> bool:
    if name == "id" or name.endswith("_id") or name.endswith("_ids"):
        return True
    dtype_lower = dtype.lower()
    numeric_types = (
        "int",
        "bigint",
        "smallint",
        "serial",
        "numeric",
        "decimal",
        "double",
        "real",
        "float",
        "uuid",
    )
    return any(token in dtype_lower for token in numeric_types)


def format_cell(value: object, *, max_width: int = MAX_CELL_WIDTH) -> str:
    if value is None:
        return "NULL"

    text = str(value).replace("\n", "\\n")
    if len(text) > max_width:
        return f"{text[: max_width - 3]}..."
    return text


def table_header(table: str, total_rows: int) -> str:
    return f"\n=== {table} ({total_rows} rows) ==="


def print_table(
    table: str,
    columns: list[tuple[str, str]],
    rows: list[asyncpg.Record],
    total_rows: int,
) -> None:
    compact = [is_compact_column(name, dtype) for name, dtype in columns]
    headers = [
        name if is_compact else f"{name} ({dtype})"
        for (name, dtype), is_compact in zip(columns, compact, strict=True)
    ]
    column_names = [name for name, _ in columns]
    max_widths = [
        MAX_COMPACT_CELL_WIDTH if is_compact else MAX_CELL_WIDTH
        for is_compact in compact
    ]

    if not rows:
        print(table_header(table, total_rows))
        for header in headers:
            print(f"  {header}")
        print("  (no rows)")
        return

    rendered_rows = [
        [
            format_cell(row[column_name], max_width=max_widths[index])
            for index, column_name in enumerate(column_names)
        ]
        for row in rows
    ]
    widths = [
        min(
            max(len(header), *(len(row[index]) for row in rendered_rows)),
            max_widths[index],
        )
        for index, header in enumerate(headers)
    ]

    print(table_header(table, total_rows))

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
                total_rows = await conn.fetchval(
                    f'SELECT COUNT(*) FROM "{table}"'
                )
                rows = await conn.fetch(f'SELECT * FROM "{table}" LIMIT {MAX_ROWS}')
                print_table(table, columns, rows, total_rows)
    finally:
        await close_pool()


if __name__ == "__main__":
    asyncio.run(main())
