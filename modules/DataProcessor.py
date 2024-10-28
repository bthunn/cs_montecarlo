import json
from datetime import date
from datetime import datetime
import pandas as pd
import matplotlib as plt
import numpy as np


class DataProcessor:
    def __init__(self, raw_data):
        self.item_data = ItemData(raw_data)
        self.processed_item_data = self.item_data.prices_clean

    def get_processed_item_data(self):
        return self.processed_item_data


class ItemData:
    def __init__(self, raw_data):
        self.raw_data = raw_data
        self.data_handler = DataHandler(self.raw_data)
        self.prices_all = self.data_handler.prices
        self.dates = self.data_handler.dates
        self.data_cleaner = dataCleaner(prices=self.prices_all, dates=self.dates)
        self.df = self.data_cleaner.df
        self.prices_clean = self.df['Filtered_Price_Interp'].tolist()

    def plot_cleaned_data(self, start_date=date(1900,1,1), end_date=date(1900,1,1)):
        dataCleaner.plot_cleaned_data(self.data_cleaner, start_date, end_date)


class DataHandler:
    def __init__(self, raw_data):
        self.data = raw_data
        self.dates = self._convert_dates()
        self.prices = self._extract_prices()
    
    def _convert_dates(self):
        dates_str = [sublist[0] for sublist in self.data]
        dates_split = [date.split() for date in dates_str] # split string into ['mmm', 'dd, 'yyyy', ...]
        dates_str_simple = [f"{date[0]} {date[1]} {date[2]}" for date in dates_split]
        converted_dates = [datetime.strptime(date, "%b %d %Y").date() for date in dates_str_simple]
        return converted_dates
    
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