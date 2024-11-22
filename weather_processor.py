"""
Weather Processor Module.

This module handles the main operations for scraping weather data,
saving it to a database, and generating plots.
"""

import logging
from datetime import datetime, timedelta
from scrape_weather import WeatherScraper
from db_operations import DBOperations
from plot_operations import PlotOperations

class WeatherProcessor:
    """
    WeatherProcessor class to manage weather data scraping,
    database storage, and data visualization.
    """

    def __init__(self):
        """
        Initialize WeatherProcessor with instances of WeatherScraper,
        DBOperations, and PlotOperations. Also initializes the database.
        """
        self.scraper = WeatherScraper()
        self.db = DBOperations()
        self.plotter = PlotOperations()
        self.db.initialize_db()

    def start(self):
        """
        Main menu for the Weather Processing application.
        Handles user choices for downloading, updating data,
        and generating plots.
        """
        while True:
            print("\nWeather Processing App")
            print("1. Download full set of weather data")
            print("2. Update weather data")
            print("3. Generate a box plot")
            print("4. Generate a line plot")
            print("5. Exit")
            choice = input("Enter your choice: ")

            try:
                if choice == '1':
                    self.download_full_data()
                elif choice == '2':
                    self.update_data()
                elif choice == '3':
                    self.generate_box_plot()
                elif choice == '4':
                    self.generate_line_plot()
                elif choice == '5':
                    print("Exiting the application.")
                    break
                else:
                    print("Invalid choice. Please enter a number between 1 and 5.")
            except Exception as e:
                logging.error("Error in main menu: %s", e)
                print(f"An error occurred: {e}")

    def download_full_data(self):
        """
        Download and store a full set of weather data for Winnipeg from
        2020 to the current year.
        """
        location = "Winnipeg"
        start_year = 2020
        current_year = datetime.now().year
        current_month = datetime.now().month

        try:
            for year in range(start_year, current_year + 1):
                for month in range(1, 13):
                    if year == current_year and month > current_month:
                        break

                    print(f"Scraping data for {location} in {year}-{month:02d}...")
                    url = f"http://climate.weather.gc.ca/climate_data/daily_data_e.html?StationID=27174&timeframe=2&Year={year}&Month={month}"
                    weather_data = self.scraper.start_scraping(url)

                    if weather_data:
                        self.db.save_data(weather_data, location)
                        print(f"Data for {location} in {year}-{month:02d} saved successfully.")
                    else:
                        print(f"Failed to scrape data for {location} in {year}-{month:02d}")

        except Exception as e:
            logging.error("Error while downloading full data: %s", e)
            print(f"Error while downloading full set of data for {location}: {e}")

    def update_data(self):
        """
        Update weather data in the database from the last date to today.
        """
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            with self.db.get_db_connection() as cursor:
                cursor.execute("SELECT MAX(sample_date) FROM weather")
                last_date = cursor.fetchone()[0]

            if last_date:
                last_date_obj = datetime.strptime(last_date, "%Y-%m-%d")
                current_date = last_date_obj + timedelta(days=1)
                while current_date.strftime("%Y-%m-%d") <= today:
                    year, month, day = current_date.strftime("%Y-%m-%d").split('-')
                    print(f"Updating data for {current_date.strftime('%Y-%m-%d')}...")
                    url = f"http://climate.weather.gc.ca/climate_data/daily_data_e.html?StationID=27174&timeframe=2&Year={year}&Month={month}"
                    weather_data = self.scraper.start_scraping(url)

                    if weather_data:
                        self.db.save_data(weather_data, location="Winnipeg")
                        print(f"Data for {current_date.strftime('%Y-%m-%d')} updated successfully.")
                    current_date += timedelta(days=1)
            else:
                print("No existing data found in the database. Please download full data first.")
        except Exception as e:
            logging.error("Error while updating data: %s", e)
            print(f"Error while updating data: {e}")

    def generate_box_plot(self):
        """
        Generate a box plot for mean temperatures over a year range.
        """
        try:
            start_year = int(input("Enter start year: "))
            end_year = int(input("Enter end year: "))
            data = self.db.fetch_data(location="Winnipeg")

            if not data:
                print("No data found in the database.")
                return

            filtered_data = [
                (int(record[0][:4]), record[3]) for record in data
                if start_year <= int(record[0][:4]) <= end_year
            ]

            if filtered_data:
                self.plotter.plot_boxplot(filtered_data, start_year, end_year)
            else:
                print("No data available for the selected year range.")
        except ValueError:
            logging.error("Invalid input for year range.")
            print("Please enter valid numeric input for the years.")
        except Exception as e:
            logging.error("Error generating box plot: %s", e)
            print(f"Error generating box plot: {e}")

    def generate_line_plot(self):
        """
        Generate a line plot for a specific month and year.
        """
        try:
            month = int(input("Enter month (1-12): "))
            year = int(input("Enter year: "))
            data = self.db.fetch_data(location="Winnipeg")

            if not data:
                print("No data found in the database.")
                return

            daily_data = [
                record[3] for record in data if record[0].startswith(f"{year}-{month:02d}")
            ]

            if daily_data:
                self.plotter.plot_lineplot(daily_data, month, year)
            else:
                print("No data available for the selected month and year.")
        except ValueError:
            logging.error("Invalid input for month or year.")
            print("Please enter valid numeric input for month and year.")
        except Exception as e:
            logging.error("Error generating line plot: %s", e)
            print(f"Error generating line plot: {e}")

# Run the application
if __name__ == "__main__":
    processor = WeatherProcessor()
    processor.start()
