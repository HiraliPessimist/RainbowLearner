import os

from datetime import datetime

import psycopg2


class Logs:

    @staticmethod
    def create(origin: str, phonetics: str, ip: str) -> None:
        now = datetime.now()
        id = hash(now)

        dsn = os.environ.get('DATABASE_URL')
        conn = psycopg2.connect(dsn)
        cur = conn.cursor()

        cur.execute(f"INSERT INTO language_helper_logs VALUES({id},{now},'{origin}','{phonetics}','{ip}')")

    @staticmethod
    def read_id(id: int):
        dsn = os.environ.get('DATABASE_URL')
        conn = psycopg2.connect(dsn)
        cur = conn.cursor()

        cur.execute(f"SELECT * FROM language_helper_logs WHERE id = {id}")
