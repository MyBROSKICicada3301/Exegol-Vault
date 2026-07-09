import os

import psycopg
from dotenv import load_dotenv

from paths import app_dir

load_dotenv(app_dir() / ".env")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS master_config (
    id            INTEGER PRIMARY KEY CHECK (id = 1),
    password_hash BYTEA NOT NULL,
    kdf_salt      BYTEA NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS holocrons (
    id           SERIAL PRIMARY KEY,
    title        TEXT NOT NULL,
    username     TEXT NOT NULL DEFAULT '',
    password_enc TEXT NOT NULL,
    url          TEXT NOT NULL DEFAULT '',
    notes        TEXT NOT NULL DEFAULT '',
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""


class VaultDatabaseError(Exception):
    pass


class Database:
    def __init__(self):
        self._conn = None

    def connect(self):
        port_raw = os.getenv("DB_PORT", "5432")
        try:
            port = int(port_raw)
        except ValueError:
            raise VaultDatabaseError(
                f"DB_PORT in .env is not a number: {port_raw!r} (usually 5432)"
            ) from None
        try:
            self._conn = psycopg.connect(
                host=os.getenv("DB_HOST", "localhost"),
                port=port,
                dbname=os.getenv("DB_NAME", "Exegol-Vault"),
                user=os.getenv("DB_APP_USER", "Exegol-Vault"),
                password=os.getenv("DB_APP_PASSWORD", ""),
                autocommit=True,
            )
        except psycopg.OperationalError as exc:
            raise VaultDatabaseError(str(exc)) from exc
        with self._conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)

    def close(self):
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def _cursor(self):
        if self._conn is None or self._conn.closed:
            self.connect()
        return self._conn.cursor()

    def get_master(self):
        with self._cursor() as cur:
            cur.execute("SELECT password_hash, kdf_salt FROM master_config WHERE id = 1")
            row = cur.fetchone()
        return (bytes(row[0]), bytes(row[1])) if row else None

    def set_master(self, password_hash: bytes, kdf_salt: bytes):
        with self._cursor() as cur:
            cur.execute(
                """
                INSERT INTO master_config (id, password_hash, kdf_salt)
                VALUES (1, %s, %s)
                ON CONFLICT (id) DO UPDATE
                SET password_hash = EXCLUDED.password_hash,
                    kdf_salt = EXCLUDED.kdf_salt
                """,
                (password_hash, kdf_salt),
            )

    def list_holocrons(self, search: str = ""):
        query = """
            SELECT id, title, username, password_enc, url, notes
            FROM holocrons
        """
        params = ()
        if search:
            query += " WHERE title ILIKE %s OR username ILIKE %s OR url ILIKE %s"
            like = f"%{search}%"
            params = (like, like, like)
        query += " ORDER BY lower(title), id"
        with self._cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
        return [
            {
                "id": r[0],
                "title": r[1],
                "username": r[2],
                "password_enc": r[3],
                "url": r[4],
                "notes": r[5],
            }
            for r in rows
        ]

    def add_holocron(self, title, username, password_enc, url, notes):
        with self._cursor() as cur:
            cur.execute(
                """
                INSERT INTO holocrons (title, username, password_enc, url, notes)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (title, username, password_enc, url, notes),
            )
            return cur.fetchone()[0]

    def update_holocron(self, entry_id, title, username, password_enc, url, notes):
        with self._cursor() as cur:
            cur.execute(
                """
                UPDATE holocrons
                SET title = %s, username = %s, password_enc = %s,
                    url = %s, notes = %s, updated_at = now()
                WHERE id = %s
                """,
                (title, username, password_enc, url, notes, entry_id),
            )

    def delete_holocron(self, entry_id):
        with self._cursor() as cur:
            cur.execute("DELETE FROM holocrons WHERE id = %s", (entry_id,))
