import urllib.request
from html.parser import HTMLParser
import datetime
import logging

# Set up logging
logging.basicConfig(filename='weather_app.log', level=logging.ERROR, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

class WeatherScraper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.data = {}
        self.in_data = False
        self.current_date = None
        self.daily_temps = {}

    def handle_starttag(self, tag, attrs):
        # Detect relevant data using HTML tag information
        if tag == 'tr' and ('data-row', 'date') in attrs:
            # Capture date, temperature data
            self.in_data = True
            for attr in attrs:
                if attr[0] == 'data-date':
                    self.current_date = attr[1]

    def handle_endtag(self, tag):
        if tag == 'tr' and self.in_data:
            self.in_data = False
            if self.current_date and self.daily_temps:
                self.data[self.current_date] = self.daily_temps
                self.daily_temps = {}

    def handle_data(self, data):
      if self.in_data:
          try:
              temp_data = data.strip().split()
              if len(temp_data) == 2 and temp_data[0] == "Max":
                  max_temp = float(temp_data[1])
                  self.daily_temps['max_temp'] = max_temp
                  print(f"Max Temp Found: {max_temp}")  # <-- Add this line to check max temperature
              elif len(temp_data) == 2 and temp_data[0] == "Min":
                  min_temp = float(temp_data[1])
                  self.daily_temps['min_temp'] = min_temp
                  print(f"Min Temp Found: {min_temp}")  # <-- Add this line to check min temperature
          except ValueError:
              logging.error(f"Failed to parse temperature data: {data}")


    def scrape_data(self, start_url):
        try:
            response = urllib.request.urlopen(start_url)
            html = response.read().decode('utf-8')
            self.feed(html)
            return self.data
        except Exception as e:
            logging.error(f"Error scraping data: {e}")
            return {}

# Test code for the scraper
if __name__ == "__main__":
    scraper = WeatherScraper()
    today = datetime.datetime.now()
    start_url = f"https://climate.weather.gc.ca/climate_data/daily_data_e.html?StationID=27174&timeframe=2&StartYear=1840&EndYear=2018&Day=1&Year=2018&Month=5"
    # "http://climate.weather.gc.ca/climate_data/daily_data_e.html?StationID=27174&timeframe=2&StartYear={today.year}&EndYear={today.year}&Day={today.day}&Year={today.year}&Month={today.month}#"
    weather_data = scraper.scrape_data(start_url)
    print(weather_data)
