import matplotlib.pyplot as plt

class PlotOperations:
    def plot_boxplot(self, data, start_year, end_year):
        """Plot a boxplot for temperatures over a year range."""
        years = list(set(year for year, temp in data))
        years.sort()
        temperatures_by_year = {year: [] for year in years}
        
        for year, temp in data:
            temperatures_by_year[year].append(float(temp))
        
        temperatures_data = [temperatures_by_year[year] for year in years]
        
        plt.figure(figsize=(10, 6))
        plt.boxplot(temperatures_data, labels=years)
        plt.title(f'Boxplot of Mean Temperatures from {start_year} to {end_year}')
        plt.xlabel('Year')
        plt.ylabel('Mean Temperature (°C)')
        plt.show()

    def plot_lineplot(self, daily_data, month, year):
        """Plot a line plot for temperatures over a specific month and year."""
        days = list(range(1, len(daily_data) + 1))
        temperatures = [float(temp) for temp in daily_data]
        
        plt.figure(figsize=(10, 6))
        plt.plot(days, temperatures, marker='o')
        plt.title(f'Temperature Line Plot for {year}-{month:02d}')
        plt.xlabel('Day of the Month')
        plt.ylabel('Mean Temperature (°C)')
        plt.grid(True)
        plt.show()