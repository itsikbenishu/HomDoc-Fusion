import psycopg
from .DBConfig import db_settings

def get_db():
    conn = psycopg.connect(
        host=db_settings.POSTGRES_HOST,
        port=db_settings.POSTGRES_PORT,
        user=db_settings.POSTGRES_USER,
        password=db_settings.POSTGRES_PASSWORD,
        dbname=db_settings.POSTGRES_DB
    )
    return conn

def select(query, params=None):
    with get_db() as conn:
        with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            cur.execute(query, params or ())
            results = cur.fetchall()
            return results

def update(query, params=None):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
        conn.commit()

def update_row_by_id(table_name, data: dict, row_id: int):
    set_clause = ", ".join(f"{key} = %s" for key in data.keys())
    values = list(data.values())
    values.append(row_id)  

    query = f"UPDATE {table_name} SET {set_clause} WHERE id = %s"

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(query, values)
        conn.commit()
