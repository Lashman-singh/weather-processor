from scrape_weather import scrape_all_data
from db_operations import DBOperations

def main():
    # Step 1: Scrape data
    weather_data = scrape_all_data()

    # Step 2: Initialize the database and save data
    db_operations = DBOperations()
    db_operations.initialize_db()

    # Save the weather data into the database (using a fixed location)
    db_operations.save_data(weather_data, location="MyLocation")

    # Step 3: Fetch data from the database for plotting (if needed)
    data = db_operations.fetch_data(location="MyLocation")
    print(data)

if __name__ == "__main__":
    main()
