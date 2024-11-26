import tkinter as tk
from tkinter import messagebox, ttk
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
        self.title("Weather Processing Application")
        self.geometry("500x600")

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
        # App Title
        title_label = tk.Label(self, text="Weather Processing App", font=("Helvetica", 18, "bold"))
        title_label.pack(pady=15)

        # Status Label
        self.status_label = tk.Label(self, text="Status: Ready", font=("Helvetica", 10, "italic"))
        self.status_label.pack(pady=5)

        # Frame for Download and Update Buttons
        frame_buttons = tk.Frame(self)
        frame_buttons.pack(pady=10)

        self.download_button = tk.Button(frame_buttons, text="Download Full Weather Data", command=self.download_full_data)
        self.download_button.grid(row=0, column=0, padx=10, pady=10)

        self.update_button = tk.Button(frame_buttons, text="Update Weather Data", command=self.update_data)
        self.update_button.grid(row=0, column=1, padx=10, pady=10)

        # Separator
        ttk.Separator(self, orient='horizontal').pack(fill='x', pady=10)

        # Frame for Box Plot
        frame_box_plot = tk.LabelFrame(self, text="Box Plot Generation", padx=10, pady=10)
        frame_box_plot.pack(pady=10, fill="x", padx=20)

        self.start_year_label = tk.Label(frame_box_plot, text="Start Year:")
        self.start_year_label.grid(row=0, column=0, padx=5, pady=5)
        self.start_year_entry = tk.Entry(frame_box_plot)
        self.start_year_entry.grid(row=0, column=1, padx=5, pady=5)

        self.end_year_label = tk.Label(frame_box_plot, text="End Year:")
        self.end_year_label.grid(row=1, column=0, padx=5, pady=5)
        self.end_year_entry = tk.Entry(frame_box_plot)
        self.end_year_entry.grid(row=1, column=1, padx=5, pady=5)

        self.box_plot_button = tk.Button(frame_box_plot, text="Generate Box Plot", command=self.generate_box_plot)
        self.box_plot_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Separator
        ttk.Separator(self, orient='horizontal').pack(fill='x', pady=10)

        # Frame for Line Plot
        frame_line_plot = tk.LabelFrame(self, text="Line Plot Generation", padx=10, pady=10)
        frame_line_plot.pack(pady=10, fill="x", padx=20)

        self.month_label = tk.Label(frame_line_plot, text="Month (1-12):")
        self.month_label.grid(row=0, column=0, padx=5, pady=5)
        self.month_entry = tk.Entry(frame_line_plot)
        self.month_entry.grid(row=0, column=1, padx=5, pady=5)

        self.year_label = tk.Label(frame_line_plot, text="Year:")
        self.year_label.grid(row=1, column=0, padx=5, pady=5)
        self.year_entry = tk.Entry(frame_line_plot)
        self.year_entry.grid(row=1, column=1, padx=5, pady=5)

        self.line_plot_button = tk.Button(frame_line_plot, text="Generate Line Plot", command=self.generate_line_plot)
        self.line_plot_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Exit Button
        self.exit_button = tk.Button(self, text="Exit", command=self.quit, bg="#ff4d4d", fg="white")
        self.exit_button.pack(pady=20)

    def update_status(self, message):
        """
        Update the status label with a given message.
        """
        self.status_label.config(text=f"Status: {message}")
        self.update_idletasks()

    def download_full_data(self):
        """
        Trigger downloading and storing of full weather data.
        """
        location = "Winnipeg"
        start_year = 2020
        current_year = datetime.now().year
        current_month = datetime.now().month

        try:
            self.update_status("Downloading full weather data...")
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
            self.update_status("Download completed.")

        except Exception as e:
            logging.error("Error while downloading full data: %s", e)
            messagebox.showerror("Error", f"Error while downloading full set of data: {e}")
            self.update_status("Error occurred.")

    def update_data(self):
        """
        Trigger updating of weather data in the database.
        """
        try:
            self.update_status("Updating weather data...")
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
                self.update_status("Update completed.")
            else:
                messagebox.showwarning("No Data", "No existing data found. Please download full data first.")
                self.update_status("No data to update.")

        except Exception as e:
            logging.error("Error while updating data: %s", e)
            messagebox.showerror("Error", f"Error while updating data: {e}")
            self.update_status("Error occurred.")

    def generate_box_plot(self):
        """
        Trigger the generation of a box plot.
        """
        try:
            self.update_status("Generating box plot...")
            start_year = int(self.start_year_entry.get())
            end_year = int(self.end_year_entry.get())
            data = self.db.fetch_data(location="Winnipeg")

            if not data:
                print("No data found in the database.")
                self.update_status("No data available.")
                return

            filtered_data = [
                (int(record[0][:4]), record[3]) for record in data
                if start_year <= int(record[0][:4]) <= end_year
            ]

            if filtered_data:
                self.plotter.plot_boxplot(filtered_data, start_year, end_year)
                self.update_status("Box plot generated.")
            else:
                messagebox.showwarning("No Data", "No data found for the specified year range.")
                self.update_status("No data for selected range.")

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid start and end years.")
            self.update_status("Invalid input for years.")
        except Exception as e:
            logging.error("Error while generating box plot: %s", e)
            messagebox.showerror("Error", f"Error while generating box plot: {e}")
            self.update_status("Error occurred.")

    def generate_line_plot(self):
        """
        Trigger the generation of a line plot.
        """
        try:
            # Validate month and year inputs
            month = self.month_entry.get()
            year = self.year_entry.get()

            if not month.isdigit() or not year.isdigit():
                raise ValueError("Month and year must be numeric values.")
            
            month = int(month)
            year = int(year)
            
            if month < 1 or month > 12:
                raise ValueError("Month must be between 1 and 12.")

            # Fetch data from the database for the specified location
            data = self.db.fetch_data(location="Winnipeg")
            
            if not data:
                messagebox.showwarning("No Data", "No data found in the database.")
                return

            # Filter data based on the selected year and month
            daily_data = [
                float(record[3]) for record in data if record[0].startswith(f"{year}-{month:02d}")
            ]

            # Plot if data exists
            if daily_data:
                self.plotter.plot_lineplot(daily_data, month, year)
            else:
                messagebox.showwarning("No Data", "No data available for the selected month and year.")
        
        except ValueError as ve:
            logging.error("Invalid input for month or year: %s", ve)
            messagebox.showerror("Error", str(ve))
        except Exception as e:
            logging.error("Error generating line plot: %s", e)
            messagebox.showerror("Error", f"An unexpected error occurred while generating the line plot: {e}")

if __name__ == "__main__":
    app = WeatherProcessorGUI()
    app.mainloop()
