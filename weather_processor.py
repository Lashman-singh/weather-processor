"""
Weather Processor Module.

This module handles the main operations for scraping weather data,
saving it to a database, and generating plots.
"""

import tkinter as tk
from tkinter import messagebox
import logging
from datetime import datetime, timedelta
from scrape_weather import WeatherScraper
from db_operations import DBOperations
from plot_operations import PlotOperations

class WeatherProcessorGUI(tk.Tk):
    """
    WeatherProcessorGUI class to manage the weather data scraping,
    database storage, and data visualization via a graphical user interface.
    """

    def __init__(self):
        """
        Initialize the GUI window and set up WeatherScraper, DBOperations,
        and PlotOperations instances.
        """
        super().__init__()
        self.title("Weather Processing App")
        self.geometry("400x400")

        # Initialize backend components
        self.scraper = WeatherScraper()
        self.db = DBOperations()
        self.plotter = PlotOperations()
        self.db.initialize_db()

        # Set up GUI elements
        self.create_widgets()

    def create_widgets(self):
        """
        Create all widgets (buttons, labels, etc.) for the GUI.
        """
        self.download_button = tk.Button(self, text="Download full set of weather data", command=self.download_full_data)
        self.download_button.pack(pady=10)

        self.update_button = tk.Button(self, text="Update weather data", command=self.update_data)
        self.update_button.pack(pady=10)

        self.box_plot_button = tk.Button(self, text="Generate box plot", command=self.generate_box_plot)
        self.box_plot_button.pack(pady=10)

        self.line_plot_button = tk.Button(self, text="Generate line plot", command=self.generate_line_plot)
        self.line_plot_button.pack(pady=10)

        # Input fields for box plot
        self.start_year_label = tk.Label(self, text="Start Year:")
        self.start_year_label.pack()
        self.start_year_entry = tk.Entry(self)
        self.start_year_entry.pack(pady=5)

        self.end_year_label = tk.Label(self, text="End Year:")
        self.end_year_label.pack()
        self.end_year_entry = tk.Entry(self)
        self.end_year_entry.pack(pady=5)

        # Input fields for line plot
        self.month_label = tk.Label(self, text="Month (1-12):")
        self.month_label.pack()
        self.month_entry = tk.Entry(self)
        self.month_entry.pack(pady=5)

        self.year_label = tk.Label(self, text="Year:")
        self.year_label.pack()
        self.year_entry = tk.Entry(self)
        self.year_entry.pack(pady=5)

        self.exit_button = tk.Button(self, text="Exit", command=self.quit)
        self.exit_button.pack(pady=10)

    def download_full_data(self):
        """
        Trigger downloading and storing of full weather data.
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

            messagebox.showinfo("Success", "Full weather data download completed.")

        except Exception as e:
            logging.error("Error while downloading full data: %s", e)
            messagebox.showerror("Error", f"Error while downloading full set of data: {e}")

    def update_data(self):
        """
        Trigger updating of weather data in the database.
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

                messagebox.showinfo("Success", "Weather data updated successfully.")
            else:
                messagebox.showwarning("No Data", "No existing data found. Please download full data first.")

        except Exception as e:
            logging.error("Error while updating data: %s", e)
            messagebox.showerror("Error", f"Error while updating data: {e}")

    def generate_box_plot(self):
        """
        Trigger the generation of a box plot.
        """
        try:
            start_year = int(self.start_year_entry.get())
            end_year = int(self.end_year_entry.get())
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
                messagebox.showinfo("Success", "Box plot generated.")
            else:
                messagebox.showwarning("No Data", "No data available for the selected year range.")
        except ValueError:
            logging.error("Invalid input for year range.")
            messagebox.showerror("Error", "Please enter valid numeric input for the years.")
        except Exception as e:
            logging.error("Error generating box plot: %s", e)
            messagebox.showerror("Error", f"Error generating box plot: {e}")

    def generate_line_plot(self):
        """
        Trigger the generation of a line plot.
        """
        try:
            month = int(self.month_entry.get())
            year = int(self.year_entry.get())
            data = self.db.fetch_data(location="Winnipeg")

            if not data:
                print("No data found in the database.")
                return

            daily_data = [
                record[3] for record in data if record[0].startswith(f"{year}-{month:02d}")
            ]

            if daily_data:
                self.plotter.plot_lineplot(daily_data, month, year)
                messagebox.showinfo("Success", "Line plot generated.")
            else:
                messagebox.showwarning("No Data", "No data available for the selected month and year.")
        except ValueError:
            logging.error("Invalid input for month or year.")
            messagebox.showerror("Error", "Please enter valid numeric input for month and year.")
        except Exception as e:
            logging.error("Error generating line plot: %s", e)
            messagebox.showerror("Error", f"Error generating line plot: {e}")


# Run the application
if __name__ == "__main__":
    app = WeatherProcessorGUI()
    app.mainloop()
