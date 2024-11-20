import sqlite3

class DBCM:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type is None:
            self.conn.commit()
        self.cursor.close()
        self.conn.close()
