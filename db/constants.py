import logging
import psycopg
from db.session import engine
from typing import Optional, Any

logger = logging.getLogger(__name__)

ALLOWED_TABLES = {"rentcast_stats"}

def _get_db():
    try:
        return engine.raw_connection()
    except Exception as e:
        logger.error(f"Failed to connect: {e}")
        raise


def select(query: str, params: Optional[list | tuple] = None) -> dict[str, Any]:
    try:
        with _get_db() as conn:
            with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
                cur.execute(query, params or ())
                return cur.fetchone()
    except psycopg.Error as e:
        logger.error(f"Select query failed: {e}")
        raise


def update_row_by_id(table_name: str, data: dict, row_id: int):
    if table_name not in ALLOWED_TABLES:
        raise ValueError(f"Invalid table name: {table_name}")

    if not data:
        raise ValueError("No data provided for update")

    set_clause = ", ".join(f"{key} = %s" for key in data.keys())
    values = list(data.values())
    values.append(row_id)

    query = f"UPDATE {table_name} SET {set_clause} WHERE id = %s"

    try:
        with _get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(query, values)
            conn.commit()
    except psycopg.Error as e:
        logger.error(f"Failed to update row in {table_name}: {e}")
        raise
