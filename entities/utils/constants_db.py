import psycopg
from psycopg import sql
from db_config import db_settings

ALLOWED_TABLES = {"rentcast_stats"}

def _get_db():
    try:
        conn = psycopg.connect(
            host=db_settings.POSTGRES_HOST,
            port=db_settings.POSTGRES_PORT,
            user=db_settings.POSTGRES_USER,
            password=db_settings.POSTGRES_PASSWORD,
            dbname=db_settings.POSTGRES_DB
        )
        return conn    
    except psycopg.Error as e:
        print(f"Failed to connect: {e}")
        raise


def select(query, params=None):
    try:
        with _get_db() as conn:
            with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
                cur.execute(query, params or ())
                return cur.fetchall()
    except psycopg.Error as e:
        print(f"Select query failed: {e}")
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
        print(f"Failed to update row in {table_name}: {e}")
        raise
