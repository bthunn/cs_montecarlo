import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import requests
import json
from datetime import datetime
from datetime import date
import pandas as pd
import os
from PriceGetter import PriceGetter


BASE_URL = "https://steamcommunity.com/market/pricehistory/"

def main():
    temp()

def temp():
    test_inv_raw_data = loadJSON(
    r"F:\programs\python\cs_montecarlo\data\test-inventory-from-steamwebapi-2024-10-28.json" # filepath of list of inv items, from steam web api
        ).data
    
    # browse session cookies. Update as necessary by viewing Network -> search:"domain:steamcommunity.com scheme:https"
    # and find 'cookie:'. These fields will be included, copy them in
    cookies = {
        "sessionid": "1bc5949f3ee1adabe5bc6c2a",
        "steamLoginSecure": "76561198149693785%7C%7CeyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0.eyAiaXNzIjogInI6MTAyOF8yNTQxQ0EzN18zODFFRCIsICJzdWIiOiAiNzY1NjExOTgxNDk2OTM3ODUiLCAiYXVkIjogWyAid2ViOmNvbW11bml0eSIgXSwgImV4cCI6IDE3MzAxODAyNzEsICJuYmYiOiAxNzIxNDUyMTU4LCAiaWF0IjogMTczMDA5MjE1OCwgImp0aSI6ICIxMDIxXzI1NDFDQTM2XzcxQjI0IiwgIm9hdCI6IDE3MzAwOTIxNTgsICJydF9leHAiOiAxNzMyNjcxNjI4LCAicGVyIjogMCwgImlwX3N1YmplY3QiOiAiMTQzLjE1OS4xNzIuMTE0IiwgImlwX2NvbmZpcm1lciI6ICIxNDMuMTU5LjE3Mi4xMTQiIH0.DvBClrpajLmQXgbfRJH5JvhnpEcrpOc0IE-U7up7jefTjfNnTjYeGh0sRTVbAXR2sqMcT3uOJJAWDupwBtKZAQ"
    }

    test_inventory = InventoryData(test_inv_raw_data)
    # price_getter = PriceGetter(item_list=test_inventory.item_list_marketable, cookies=cookies)
    # # format of item_price_list is a list of price data responses, so a list of dictionaries
    # item_price_list = price_getter.get_data_for_item_list() 
    # with open(f'data\\test-inv-price-data-set-{date.today()}.json', 'w', encoding="utf-8") as file:
    #         file.write(json.dumps(item_price_list, ensure_ascii=False))


        

def main_wrapped():
        # get data from JSON
    raw_data = loadJSON(
        r"F:\programs\python\cs_montecarlo\data\pricedata_awp_redline_minwear.json"
            )

    # process data
    test_data = ItemData(raw_data.data)

    #plot data
    start_date = date(2014,1,1)
    #test_data.plot_cleaned_data(start_date)
    
    #generate model
    test_model = GBMModel(test_data)



class InventoryData:
    def __init__(self, raw_json):
        self.raw_json = raw_json
        self.item_list = self._get_list_of_market_hash_names()
        self.item_list_marketable = self._get_list_of_filtered_market_hash_names()


    def _get_list_of_market_hash_names(self):
        item_list = [item['markethashname'] for item in self.raw_json]
        item_list_spaces_replaced = [item.replace(" ", "%20") for item in item_list]
        
        # with open('item_market_hash_name_list.json', 'w', encoding="utf-8") as file:
        #     file.write(json.dumps(item_list_spaces_replaced, ensure_ascii=False))
        
        return item_list_spaces_replaced
    
    def _get_list_of_filtered_market_hash_names(self):
        mask = [item['marketable'] for item in self.raw_json]
        item_list_marketable = []
        for i in range(len(self.item_list)):
            if mask[i] == True:
                item_list_marketable.append(self.item_list[i])
        item_list_spaces_replaced = [item.replace(" ", "%20") for item in item_list_marketable]
        
        return item_list_spaces_replaced
    

class ApiHandler:
    def __init__(self, base_url):
        self.base_url = base_url        

class SteamApiHandler(ApiHandler):
    def __init__(self, base_url):
        super().__init__(base_url)

    def get_item_price_history(self, params:list):
        country, currency, item_name, skin_name, condition = params
        endpoint = f'{BASE_URL}?country={country}&currency={currency}\
                     &appid=730&market_hash_name={item_name}%20|%20{skin_name}%20({condition})'
        return endpoint

class SteamWebApiHandler(ApiHandler):
    def __init__(self, base_url, api_key):
        super().__init__(base_url)
        self.api_key = api_key


def get_request(item_name, skin_name, condition):
    country = 'gb'
    currency = '3'
    endpoint = f'{BASE_URL}?country={country}&currency={currency}\&appid=730&market_hash_name={item_name}%20|%20{skin_name}%20({condition})'
    return endpoint


def display_chart(prices, converted_dates):
    fig, ax = plt.subplots()
    ax.plot(converted_dates, prices)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.grid()
    plt.show()


class ItemData:
    def __init__(self, raw_data):
        self.raw_data = raw_data
        self.data_handler = dataHandler(self.raw_data)
        self.prices_all = self.data_handler.prices
        self.dates = self.data_handler.dates
        self.data_cleaner = dataCleaner(prices=self.prices_all, dates=self.dates)
        self.df = self.data_cleaner.df
        self.prices_clean = self.df['Filtered_Price_Interp'].tolist()

    def plot_cleaned_data(self, start_date=date(1900,1,1), end_date=date(1900,1,1)):
        dataCleaner.plot_cleaned_data(self.data_cleaner, start_date, end_date)

class Model2:
    def __init__(self, data:ItemData):
        self.data = data
        self.latest_date = data.dates[-1]
        self.stock_price = data.prices_all[-1]
        prices = self.data.df['Filtered_Price_Interp']
        returns = prices.pct_change()
        self.mean_returns = returns.mean()
        

class GBMModel:
    def __init__(self, data:ItemData):
        self.data = data
        self.latest_date = data.dates[-1]
        self.stock_price = data.prices_all[-1]
        self.log_returns = self._calculate_log_returns()
        prices = self.data.df['Filtered_Price_Interp']
        returns = prices.pct_change()
        self.mean_returns = returns.mean()
        # self.drift = self._calculate_drift()
        # self.volatility = self
    
    def _calculate_log_returns(self):
        prices = np.array(self.data.prices_clean)
        log_returns = np.log(prices[1:] / prices[:-1])
        return log_returns
    

    def _calculate_drift(self):
        pass

    def _calculate_volatility(self):
        pass


class loadJSON:
    def __init__(self, path):
        self.data = self._get_data_from_json(path)

    def _get_data_from_json(self, path):
        with open(path, 'r', encoding="utf-8") as file:
            data = json.load(file)
            return data
        

class dataHandler:
    def __init__(self, raw_data):
        self.raw_data = raw_data
        self.data = self._extract_data()
        self.dates = self._convert_dates()
        self.prices = self._extract_prices()

    # def _convert_dates_legacy(self): # DO NOT USE
    #     dates = [sublist[0] for sublist in self.data]
    #     padded_dates = [date + '000' for date in dates]
    #     converted_dates = [datetime.strptime(date, "%b %d %Y %H: %z") for date in padded_dates]
    #     return converted_dates
    
    def _convert_dates(self):
        dates_str = [sublist[0] for sublist in self.data]
        dates_split = [date.split() for date in dates_str] # split string into ['mmm', 'dd, 'yyyy', ...]
        dates_str_simple = [f"{date[0]} {date[1]} {date[2]}" for date in dates_split]
        converted_dates = [datetime.strptime(date, "%b %d %Y").date() for date in dates_str_simple]
        return converted_dates

    def _extract_data(self):
        return self.raw_data['prices']
    
    def _extract_prices(self):
        return [sublist[1] for sublist in self.data]
    
    
class dataCleaner:
    def __init__(self, dates, prices):
        self.dates = dates
        self.prices = prices
        df_initial = self._create_dataframe()
        df_outliers_removed = self._remove_outliers(df_initial)
        self.df = self._interpolate_missing_values(df_outliers_removed) # dataframe with cleaned data

    def _create_dataframe(self):
        dates = self.dates
        prices = self.prices
        df = pd.DataFrame({'Date': dates, 'Price': prices})
        df.set_index('Date', inplace=True)
        return df
    
    def _remove_outliers(self, df_initial):
        df = df_initial
        window_size = 7

        rolling_q1 = df['Price'].rolling(window=window_size, center=True).quantile(0.25)
        rolling_q3 = df['Price'].rolling(window=window_size, center=True).quantile(0.75)
        rolling_iqr = rolling_q3 - rolling_q1

        # Calculate lower and upper bounds based on the rolling IQR
        lower_bound = rolling_q1 - 0.5 * rolling_iqr
        upper_bound = rolling_q3 + 0.5 * rolling_iqr

        # Filter out the outliers
        df['Filtered_Price'] = df['Price'].where((df['Price'] >= lower_bound) \
                                                 & (df['Price'] <= upper_bound))
        return df
    
    def _interpolate_missing_values(self, df_outliers_removed):
        df = df_outliers_removed

        dates = df.index.tolist()
        datetimes = pd.to_datetime(dates)
        # print(type(datetimes))
        prices = df['Filtered_Price'].tolist()
        # df = pd.DataFrame({'Datetime': datetimes, 'Filtered_Price': prices})
        # pd.to_datetime(df.index)

        series = pd.Series(data=prices, index=datetimes)
        ser_int = series.interpolate(limit_direction='both', method='time')

        # df['Filtered_Price_Interp']= df['Filtered_Price'].interpolate(limit_direction='both', method='polynomial', order='2') # interpolate NaN values
        df['Filtered_Price_Interp'] = ser_int.tolist()
        print(df)

        # check for remaining NaN values
        NaN_loc = np.isnan(df['Filtered_Price_Interp']).tolist()
        NaN_loc_indecies = []
        i=0
        c=0
        for item in NaN_loc:
            if item == True:
                NaN_loc_indecies.append(i)
                c += 1
            i += 1
        if c != 0:
            print(f"NaN values: {c} at {NaN_loc_indecies}" ) # show message if NaN values still present

        return df
    
    def plot_cleaned_data(self, start_date=date(1900,1,1), end_date=date(1900,1,1)):
        df = self.df # type: pd.DataFrame
        df.index = pd.to_datetime(df.index)

        if start_date == date(1900,1,1): start_date = df.index.min()
        if end_date == date(1900,1,1): end_date = df.index.max()

        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        mask = (df.index >= start_date) & (df.index <= end_date)

        plt.figure(figsize=(10, 6))
        plt.plot(df.index[mask], \
                 df['Price'].loc[mask], \
                    marker='o', label='Original Prices')
        plt.plot(df.index[mask], \
                 df['Filtered_Price_Interp'].loc[mask], \
                    marker='x', linestyle='--', color='red', label='Filtered and Inteerpolated Prices')

        # plt.plot(df.index, df['Price'], marker='o', label='Original Prices')
        # plt.plot(df.index, df['Filtered_Price'], marker='x', linestyle='--', color='red', label='Filtered Prices')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.title('Local IQR Outlier Removal')
        plt.legend()
        plt.show()






if __name__ == "__main__":
      main()
