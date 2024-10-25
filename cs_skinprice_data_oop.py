import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import requests
import json
from datetime import datetime
import pandas as pd

BASE_URL = "https://steamcommunity.com/market/pricehistory/"

def main():

    raw_data = marketData(r"F:\Programs 2\Python\pricedata_awp_redline_minwear.json")

    data = dataHandler(raw_data.data)

    clean_data = dataPrepper(data.dates, data.prices)


    # # endpoint = get_request("gb", "3", "AWP", "Redline", "Minimal%20Wear")
    # # print(endpoint)
    # data = get_data_from_json(r"F:\Programs 2\Python\pricedata_awp_redline_minwear.json")
    # print(type(data))
    # data_list = data['prices']
    # dates = get_convert_dates_from_data(data_list)
    # prices = get_prices_from_data(data_list)
    # display_chart(prices, dates)
    # remove_outliers(dates, prices)


def get_request(country, currency, item_name, skin_name, condition):
    # UK = gb
    # gbp = 3
    endpoint = f'{BASE_URL}?country={country}&currency={currency}&appid=730&market_hash_name={item_name}%20|%20{skin_name}%20({condition})'
    return endpoint

# def get_data(endpoint):
#     response = requests.get(endpoint)
#     data = response.json()
#     return data

# def parse_data(data):
#     prices = data[1]
#     for entry in prices:
#                 date = entry[0]
#                 price = entry[1]
#                 sales_count = entry[2]
#                 print(f"Date: {date}, Price: {price}, Sales Count: {sales_count}")


# def get_convert_dates_from_data(data): # converts dates to datetime type
#     dates = [sublist[0] for sublist in data]
#     padded_dates = [date + '000' for date in dates]
#     converted_dates = [datetime.strptime(date,"%b %d %Y %H: %z") for date in padded_dates]
#     return converted_dates
    
# def get_prices_from_data(data):
#      prices = [sublist[1] for sublist in data]
#      return prices

def display_chart(prices, converted_dates):
    fig, ax = plt.subplots()
    ax.plot(converted_dates, prices)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.grid()
    plt.show()




class marketData:
    def __init__(self, path):
        self.data = self._get_data_from_json(path)

    def _get_data_from_json(self, path):
        with open(path) as file:
            data = json.load(file)
            return data
        

class dataHandler:
    def __init__(self, data):
        self.data_list = data
        self.dates = self._convert_dates()
        self.prices = self._extract_prices()
            
    def _convert_dates(self):
        print(self.data_list)
        dates = [sublist[0] for sublist in self.data_list]
        padded_dates = [date + '000' for date in dates]
        converted_dates = [datetime.strptime(date, "%b %d %Y %H: %z") for date in padded_dates]
        return converted_dates

    def _extract_prices(self):
        return [sublist[1] for sublist in self.data_list]
    
class dataPrepper:
    def __init__(self, dates, prices):
        self.dates = dates
        self.prices = prices
        self.cleaned_data = self._remove_outliers(self.dates, self.prices) # as df

    def _remove_outliers(self):
        dates = self.dates
        prices = self.prices
        df = pd.DataFrame({'Date': dates, 'Price': prices})
        df.set_index('Date', inplace=True)

        window_size = 7

        rolling_q1 = df['Price'].rolling(window=window_size, center=True).quantile(0.25)
        rolling_q3 = df['Price'].rolling(window=window_size, center=True).quantile(0.75)
        rolling_iqr = rolling_q3 - rolling_q1

        # Calculate lower and upper bounds based on the rolling IQR
        lower_bound = rolling_q1 - 0.5 * rolling_iqr
        upper_bound = rolling_q3 + 0.5 * rolling_iqr

        # Filter out the outliers
        df['Filtered_Price'] = df['Price'].where((df['Price'] >= lower_bound) & (df['Price'] <= upper_bound))
        return df['Filtered_Price']
    
    def plot_cleaned_data(self):
        df = self.cleaned_data
        plt.figure(figsize=(10, 6))
        plt.plot(df.index, df['Price'], marker='o', label='Original Prices')
        plt.plot(df.index, df['Filtered_Price'], marker='x', linestyle='--', color='red', label='Filtered Prices')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.title('Local IQR Outlier Removal')
        plt.legend()
        plt.show()

if __name__ == "__main__":
      main()
