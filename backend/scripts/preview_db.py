import argparse
import asyncio
import shutil

import asyncpg

from leaseclear.core.config import settings
from leaseclear.db.connection import close_pool, get_pool, use_database

MAX_ROWS = 4
MAX_CELL_WIDTH = 48
MAX_COMPACT_CELL_WIDTH = 8
MIN_FLEXIBLE_CELL_WIDTH = 12
SEPARATOR = " | "
DIVIDER_SEP = "-+-"


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
    compact_types = (
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
        "boolean",
        "bool",
        "vector",
        "tsvector",
    )
    return any(token in dtype_lower for token in compact_types)


def terminal_width() -> int:
    return max(40, shutil.get_terminal_size((100, 24)).columns)


def format_cell(value: object, *, max_width: int) -> str:
    if value is None:
        return "NULL"

    text = str(value).replace("\n", "\\n")
    if max_width <= 0:
        return ""
    if len(text) > max_width:
        if max_width <= 3:
            return text[:max_width]
        return f"{text[: max_width - 3]}..."
    return text


def truncate(text: str, max_width: int) -> str:
    if len(text) <= max_width:
        return text
    if max_width <= 3:
        return text[:max_width]
    return f"{text[: max_width - 3]}..."


def table_header(table: str, total_rows: int) -> str:
    return f"\n=== {table} ({total_rows} rows) ==="


def natural_widths(
    headers: list[str],
    rendered_rows: list[list[str]],
    max_widths: list[int],
) -> list[int]:
    return [
        min(
            max(
                len(header),
                *(len(row[index]) for row in rendered_rows) if rendered_rows else [0],
            ),
            max_widths[index],
        )
        for index, header in enumerate(headers)
    ]


def allocate_widths(
    natural: list[int],
    compact: list[bool],
    available: int,
) -> list[int] | None:
    """Shrink column widths to fit `available` chars, or return None if unreadable."""
    n = len(natural)
    if n == 0:
        return []

    total = sum(natural)
    if total <= available:
        return natural

    widths = list(natural)
    flexible = [i for i, is_compact in enumerate(compact) if not is_compact]
    if not flexible:
        flexible = list(range(n))

    while sum(widths) > available and flexible:
        shrinkable = [i for i in flexible if widths[i] > MIN_FLEXIBLE_CELL_WIDTH]
        if not shrinkable:
            break
        overflow = sum(widths) - available
        per_col = max(1, overflow // len(shrinkable))
        for index in shrinkable:
            widths[index] = max(MIN_FLEXIBLE_CELL_WIDTH, widths[index] - per_col)

    # Prefer a vertical layout over crushing columns below a readable width.
    if sum(widths) > available:
        return None
    return widths


def print_horizontal(
    headers: list[str],
    rendered_rows: list[list[str]],
    widths: list[int],
) -> None:
    clipped_headers = [
        truncate(header, widths[index]).ljust(widths[index])
        for index, header in enumerate(headers)
    ]
    print(SEPARATOR.join(clipped_headers))
    print(DIVIDER_SEP.join("-" * width for width in widths))
    for rendered_row in rendered_rows:
        print(
            SEPARATOR.join(
                truncate(cell, widths[index]).ljust(widths[index])
                for index, cell in enumerate(rendered_row)
            )
        )


def print_vertical(
    headers: list[str],
    column_names: list[str],
    rows: list[asyncpg.Record],
    compact: list[bool],
) -> None:
    width = terminal_width()
    label_width = min(max(len(header) for header in headers), max(12, width // 3))
    value_width = max(8, width - label_width - 2)

    for row_index, row in enumerate(rows, start=1):
        print(f"\n--- row {row_index} ---")
        for index, (header, column_name) in enumerate(
            zip(headers, column_names, strict=True)
        ):
            max_width = (
                MAX_COMPACT_CELL_WIDTH
                if compact[index]
                else min(MAX_CELL_WIDTH, value_width)
            )
            value = format_cell(row[column_name], max_width=max_width)
            label = truncate(header, label_width).ljust(label_width)
            print(f"{label}: {value}")


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

    print(table_header(table, total_rows))

    if not rows:
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
    natural = natural_widths(headers, rendered_rows, max_widths)
    sep_overhead = len(SEPARATOR) * (len(headers) - 1) if headers else 0
    available = terminal_width() - sep_overhead
    widths = allocate_widths(natural, compact, available)

    if widths is None:
        print_vertical(headers, column_names, rows, compact)
        return

    print_horizontal(headers, rendered_rows, widths)


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

    async with use_database(database_url):
        pool = await get_pool()
        try:
            async with pool.acquire() as conn:
                tables = await list_tables(conn)
                if not tables:
                    print("No tables in public schema.")
                    return

                for table in tables:
                    columns = await list_columns(conn, table)
                    total_rows = await conn.fetchval(f'SELECT COUNT(*) FROM "{table}"')
                    rows = await conn.fetch(f'SELECT * FROM "{table}" LIMIT {MAX_ROWS}')
                    print_table(table, columns, rows, total_rows)
        finally:
            await close_pool()


if __name__ == "__main__":
    asyncio.run(main())
