import sqlite3
from contextlib import contextmanager

class DBOperations:
    def __init__(self, db_name="weather_data.db"):
        self.db_name = db_name

    @contextmanager
    def get_db_connection(self):
        """Context manager to manage database connections."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        finally:
            conn.close()

    def initialize_db(self):
        """Initialize the database with the required schema."""
        with self.get_db_connection() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS weather (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sample_date TEXT NOT NULL,
                    location TEXT NOT NULL,
                    min_temp REAL,
                    max_temp REAL,
                    avg_temp REAL,
                    UNIQUE(sample_date, location)
                )
            ''')

    def save_data(self, weather_data, location):
        """Save new weather data into the database."""
        with self.get_db_connection() as cursor:
            for date, temps in weather_data.items():
                cursor.execute('''
                    INSERT OR IGNORE INTO weather (sample_date, location, min_temp, max_temp, avg_temp)
                    VALUES (?, ?, ?, ?, ?)
                ''', (date, location, temps['Min'], temps['Max'], temps['Mean']))

    def fetch_data(self, location):
        """Fetch weather data for plotting."""
        with self.get_db_connection() as cursor:
            cursor.execute('''
                SELECT sample_date, min_temp, max_temp, avg_temp
                FROM weather WHERE location = ?
                ORDER BY sample_date
            ''', (location,))
            return cursor.fetchall()

    def purge_data(self):
        """Purge all the data from the database."""
        try:
            with self.get_db_connection() as cursor:
                cursor.execute('DELETE FROM weather')
                print("Data purged successfully.")
        except Exception as e:
            print(f"Error while purging data: {e}")
