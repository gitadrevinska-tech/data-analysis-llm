"""
db_utils.py — MySQL savienojums un shēmas izgūšana.
DB konfigurācija tiek nolasīta no config.py (kas lasa no env mainīgajiem).
"""
import os
import mysql.connector
import pandas as pd
from config import DB_CONFIG
 
 
def get_connection(database: str = None):
    """Izveido savienojumu, apvienojot DB_CONFIG ar env mainīgajiem."""
    cfg = {
        "host":     os.environ.get("DB_HOST",     DB_CONFIG["host"]),
        "port":     int(os.environ.get("DB_PORT", DB_CONFIG["port"])),
        "user":     os.environ.get("DB_USER",     DB_CONFIG["user"]),
        "password": os.environ.get("DB_PASSWORD", DB_CONFIG["password"]),
    }
    if database:
        cfg["database"] = database
    elif DB_CONFIG.get("database"):
        cfg["database"] = DB_CONFIG["database"]
    return mysql.connector.connect(**cfg)
 
 
def list_databases() -> list[str]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SHOW DATABASES")
    dbs = [row[0] for row in cur.fetchall()]
    conn.close()
    skip = {"information_schema", "mysql", "performance_schema", "sys"}
    return [d for d in dbs if d not in skip]
 
 
def get_schema(database: str) -> str:
    """Atgriež datubāzes shēmu kā tekstu LLM kontekstam."""
    conn = get_connection(database)
    cur = conn.cursor()
    cur.execute("SHOW TABLES")
    tables = [row[0] for row in cur.fetchall()]
 
    lines = [f"Database: {database}\n"]
    for table in tables:
        cur.execute(f"DESCRIBE `{table}`")
        cols = cur.fetchall()
        cur.execute(f"SELECT COUNT(*) FROM `{table}`")
        count = cur.fetchone()[0]
        lines.append(f"\nTable: {table} ({count} rows)")
        lines.append("Columns:")
        for col in cols:
            nullable = "" if col[2] == "YES" else " NOT NULL"
            pk       = " PK" if col[3] == "PRI" else ""
            lines.append(f"  - {col[0]} ({col[1]}){nullable}{pk}")
 
        # Foreign keys
        try:
            cur.execute(f"""
                SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                FROM information_schema.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                  AND REFERENCED_TABLE_NAME IS NOT NULL
            """, (database, table))
            fks = cur.fetchall()
            if fks:
                lines.append("Foreign keys:")
                for fk in fks:
                    lines.append(f"  - {fk[0]} -> {fk[1]}.{fk[2]}")
        except Exception:
            pass
 
        # Sample rows
        try:
            cur.execute(f"SELECT * FROM `{table}` LIMIT 3")
            rows = cur.fetchall()
            col_names = [c[0] for c in cols]
            if rows:
                lines.append("Sample rows:")
                for row in rows:
                    sample = {col_names[i]: str(v) for i, v in enumerate(row)}
                    lines.append(f"  {sample}")
        except Exception:
            pass
 
    conn.close()
    return "\n".join(lines)
 
 
def run_query(database: str, sql: str) -> pd.DataFrame:
    """Izpilda SQL un atgriež DataFrame."""
    conn = get_connection(database)
    try:
        df = pd.read_sql(sql, conn)
    finally:
        conn.close()
    return df
 
 
def validate_sql(database: str, sql: str) -> tuple[bool, str]:
    """Validē SQL — atgriež (True, '') vai (False, kļūdas ziņojums)."""
    conn = get_connection(database)
    cur = conn.cursor()
    try:
        cur.execute(f"EXPLAIN {sql}")
        cur.fetchall()
        conn.close()
        return True, ""
    except mysql.connector.Error as e:
        conn.close()
        return False, str(e)