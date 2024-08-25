import config
import psycopg2


class Mk3Catalog:
    def __init__(self):
        self.psql_host = config.psql_host
        self.psql_port = config.psql_port
        self.psql_dbname = config.psql_dbname
        self.psql_user = config.psql_user
        self.psql_password = config.psql_password

    def add_wanted_release(self, rgid: str):
        self.conn = psycopg2.connect(
            host=self.psql_host,
            port=self.psql_port,
            dbname=self.psql_dbname,
            user=self.psql_user,
            password=self.psql_password
            )
        cur = self.conn.cursor()
        insert_query = """
            INSERT INTO wanted_releases (rgid)
            VALUES (%s)
            ON CONFLICT (rgid) DO NOTHING
        """
        try:
            cur.execute(insert_query, (rgid,))
            self.conn.commit()
            if cur.rowcount > 0:
                return 1
            else:
                return 0
        except Exception as e:
            self.conn.rollback()
            return "Error!"
        finally:
            cur.close()
            self.conn.close()

    def grab_data(self, table:str) -> list:
        self.conn = psycopg2.connect(
            host=self.psql_host,
            port=self.psql_port,
            dbname=self.psql_dbname,
            user=self.psql_user,
            password=self.psql_password
        )
        cur = self.conn.cursor()
        select_query = f"SELECT * FROM {table};"
        try:
            cur.execute(select_query)
            rows = cur.fetchall()
            self.conn.commit()
            return rows
        except Exception as e:
            self.conn.rollback()
            print(f"Error: {e}")
            return "Error!"
        finally:
            cur.close()
            self.conn.close()
