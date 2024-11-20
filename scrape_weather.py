from html.parser import HTMLParser
import urllib.request
from datetime import datetime

class WeatherScraper(HTMLParser):
    """Class that scrapes weather data using HTMLParser"""

    def __init__(self):
        super().__init__()
        self.reset_state()

    def reset_state(self):
        """Resets the parsing state variables."""
        self.tbody = False
        self.title = False
        self.tr = False
        self.td = False
        self.count = 0
        self.maxTemp = 0
        self.minTemp = 0
        self.avg = 0
        self.date = ""
        self.weather = {}

    def start_scraping(self, url: str):
        """Scrapes the data from the given URL."""
        try:
            with urllib.request.urlopen(url) as response:
                html = response.read().decode('utf-8')
            self.feed(html)
            return self.weather
        except Exception as e:
            print(f"Error in scraping data: {e}")
            return {}

    def handle_starttag(self, tag, attrs):
        """Handles HTML start tags."""
        if tag == "tbody":
            self.tbody = True
        elif tag == "abbr" and self.tbody:
            # Extract date from the 'title' attribute
            for attr in attrs:
                if attr[0] == "title":
                    try:
                        self.date = datetime.strptime(attr[1], "%B %d, %Y").strftime("%Y-%m-%d")
                    except ValueError:
                        self.date = ""
                    break
        elif self.tbody and tag == "tr":
            self.tr = True
        elif self.tbody and self.tr and tag == "td" and self.count < 3:
            self.td = True

    def handle_endtag(self, tag):
        """Handles HTML end tags."""
        if tag == "td":
            self.td = False
            self.count += 1
        elif tag == "tr":
            self.tr = False
            self.count = 0

    def handle_data(self, data):
        """Handles data between HTML tags."""
        if self.td and self.date:
            try:
                value = float(data)
                if self.count == 0:
                    self.maxTemp = value
                elif self.count == 1:
                    self.minTemp = value
                elif self.count == 2:
                    self.avg = value
                    # Store the collected temperatures for the date
                    self.weather[self.date] = {
                        "Max": self.maxTemp,
                        "Min": self.minTemp,
                        "Mean": self.avg
                    }
                    # Reset date after storing the data
                    self.date = ""
            except ValueError:
                pass

def scrape_all_data():
    """Scrapes data from 2010 to the current year dynamically."""
    base_url = "http://climate.weather.gc.ca/climate_data/daily_data_e.html?StationID=27174&timeframe=2&Year={year}&Month={month}"
    weather_data = {}
    scraper = WeatherScraper()
    
    current_year = datetime.now().year
    current_month = datetime.now().month

    # Loop through years from 2010 to the current year
    for year in range(2010, current_year + 1):
        month = 1  # Start from January
        while month <= 12:  # Loop through all months
            if year == current_year and month > current_month:
                break  # Stop if we reach the current year and month
            url = base_url.format(year=year, month=month)
            data = scraper.start_scraping(url)
            if not data:
                print(f"No data found for {year}-{month:02d}")
                break  # Stop if no more data is available
            weather_data.update(data)

            # Increment month for next iteration
            month += 1

            # Reset parser state for the next page
            scraper.reset_state()

    return weather_data



if __name__ == "__main__":
    weather = scrape_all_data()

    # Wrap the weather data in a top-level dictionary
    wrapped_weather = {"weather": weather}
    
    # Display the data in the wrapped dictionary format
    print(wrapped_weather)