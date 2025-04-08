import json
from datetime import date
from datetime import datetime
import pandas as pd
import matplotlib as plt
import numpy as np
import os
from modules import functions as fn

# Structure:
# +------------------+
# |  InventoryData   |
# +------------------+
#         |
#         | <<create>> (dependency)
#         |
#         v
# +------------------+
# |  DataProcessor   |
# +------------------+
# | - item_data      |
# +------------------+
#         |
#         |<> (composition)
#         v
# +------------------+
# |    ItemData      |
# +------------------+
# | - data_handler   |
# | - data_cleaner   |
# +------------------+
#     |         |
#     |<>       |<> (composition)
#     v         v
# +------------+  +-------------+
# | DataHandler|  | DataCleaner |
# +------------+  +-------------+



class InventoryData:
    def __init__(self, raw_inv_json, item_data_base_path):
        self.raw_json = raw_inv_json
        self.item_data_base_path = item_data_base_path
    
        self.item_list = self._get_list_of_market_hash_names() # gets list of items in inv from raw_json
        self.item_list_marketable = self._get_list_of_filtered_market_hash_names() # gets items listed on market
        
        if self._check_inv_item_data_present: # raises excpetion if check fails.
            self.price_data_dict = self._load_item_price_data_to_dict() # dict in format {"item" : [prices]}
        self.cleaned_price_data_dict = self._process_price_data() # keys in filename format (incompatable chars replaced)
        self.date_interval = self._find_date_interval()
        self.aligned_dict = self._make_aligned_dict()
        self.inv_data_frame = self._format_to_dataframe() # FINAL 


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
    

    def _check_inv_item_data_present(self):
        counter = 0
        for item in self.item_list_marketable:
            if not os.path.exists(
                f"data\\price-data-{date.today()}\\{fn.replace_invalid_chars_for_filepath(item)}.json"
                ):
                counter += 1
        if counter > 0: 
            raise Exception(
            f"Item price data missing for {counter} items. \
                Import up-to-date price information to continue"
                )
        else:
            return True


    def _load_item_price_data_to_dict(self): # creates dict of items, with each entry contraining respective price history
        # item_price_list = []
        item_price_dict = {}
        for i in range(len(self.item_list_marketable)):
            item = self.item_list_marketable[i]
            item_filename = fn.replace_invalid_chars_for_filepath(item)
            item_filepath = f"{self.item_data_base_path}\\{item_filename}.json"

            if os.path.exists(item_filepath):

                with open(
                    item_filepath, 'r', encoding="utf-8"
                    ) as file:
                    item_data = json.load(file)
                # item_price_list.append(item_data['prices'])
                item_price_dict.update({f"{item_filename}": item_data['prices']})

            else:
                print(f"Faild to load data for {fn.replace_unprintable(item)}, file not found at: \'{item_filepath}\'")

        # if len(item_price_dict.keys()) == len(self.item_list_marketable):
        #     return item_price_dict
        # else: raise Exception("ERROR: incomplete price data")
        return item_price_dict
    

    def _process_price_data(self):
        cleaned_price_data_dict = {}
        for item_name, price_data in self.price_data_dict.items():
            data_processor = DataProcessor(price_data)
            cleaned_price_data_dict.update(
                {f"{item_name}": data_processor.get_processed_item_data()}
                )

        if self.price_data_dict.keys() == cleaned_price_data_dict.keys(): # check keys match
            return cleaned_price_data_dict
        else:
            raise Exception("ERROR dict keys don't match after data processing")


    def _find_date_interval(self):
        start = date(1900,1,1)
        end = date.today()

        for keys, items in self.cleaned_price_data_dict.items():
            # print(f"{items[0][0]} {items[-1][0]}")
            if items[0][0] > start: start = items[0][0]
            if items[-1][0] < end: end = items[-1][0]

        return [start, end] # returns interval
            

    def _make_aligned_dict(self):
        start_date, end_date = self.date_interval
        aligned_dict = {}
        for key, items in self.cleaned_price_data_dict.items():
            start_index = -1
            end_index = -1
            i = 0
            for item in items:
                if item[0] == start_date: start_index = i
                if item[0] == end_date: end_index = i
                i += 1
            
            trimmed_list = items[start_index:(end_index+1)]
            aligned_dict.update({key: trimmed_list})
        
        # print(aligned_dict[fn.replace_invalid_chars_for_filepath(self.item_list_marketable[0])])
        return aligned_dict
    
    def _format_to_dataframe(self):
        # for item in self.aligned_dict:
        #     print(len(item))
        # print(self.aligned_dict[fn.replace_invalid_chars_for_filepath(self.item_list_marketable[0])])

        return pd.DataFrame.from_dict(self.aligned_dict)



class DataProcessor:
    def __init__(self, price_data): # pass in ITEM PRICE DATA
        self.item_data = ItemData(price_data)
       
    def get_processed_item_prices(self): # return list of prices
        return self.item_data.prices_clean
    
    def get_processed_item_data(self): # return 2d list of dates and prices
        return self.item_data.processed_item_data


    def _process_price_data(self):
        cleaned_price_data_dict = {}
        for item_name, price_data in self.price_data_dict.items():
            data_processor = DataProcessor(price_data)
            cleaned_price_data_dict.update(
                {f"{item_name}": data_processor.get_processed_item_data()}
                )

        if self.price_data_dict.keys() == cleaned_price_data_dict.keys(): # check keys match
            return cleaned_price_data_dict
        else:
            raise Exception("ERROR dict keys don't match after data processing")


    def _find_date_interval(self):
        start = date(1900,1,1)
        end = date.today()

        for keys, items in self.cleaned_price_data_dict.items():
            # print(f"{items[0][0]} {items[-1][0]}")
            if items[0][0] > start: start = items[0][0]
            if items[-1][0] < end: end = items[-1][0]

        return [start, end] # returns interval
            

    def _make_aligned_dict(self):
        start_date, end_date = self.date_interval
        aligned_dict = {}
        for key, items in self.cleaned_price_data_dict.items():
            start_index = -1
            end_index = -1
            i = 0
            for item in items:
                if item[0] == start_date: start_index = i
                if item[0] == end_date: end_index = i
                i += 1
            
            trimmed_list = items[start_index:(end_index+1)]
            aligned_dict.update({key: trimmed_list})
        
        # print(aligned_dict[fn.replace_invalid_chars_for_filepath(self.item_list_marketable[0])])
        return aligned_dict
    
    def _format_to_dataframe(self):
        # for item in self.aligned_dict:
        #     print(len(item))
        # print(self.aligned_dict[fn.replace_invalid_chars_for_filepath(self.item_list_marketable[0])])

        return pd.DataFrame.from_dict(self.aligned_dict)



class ItemData:
    def __init__(self, raw_data):
        self.raw_data = raw_data
        self.data_handler = DataHandler(self.raw_data)
        self.prices_all = self.data_handler.prices
        self.dates = self.data_handler.dates
        self.data_cleaner = dataCleaner(prices=self.prices_all, dates=self.dates)
        self.df = self.data_cleaner.df
        self.prices_clean = self.df['Filtered_Price_Interp'].tolist()
        self.processed_item_data = self._generate_2d_processed_data()

    def plot_cleaned_data(self, start_date=date(1900,1,1), end_date=date(1900,1,1)):
        dataCleaner.plot_cleaned_data(self.data_cleaner, start_date, end_date)

    def _generate_2d_processed_data(self):
        data = [0] * len(self.prices_clean)
        for i in range(len(self.prices_clean)):
            data[i] = [self.dates[i], self.prices_clean[i]]

        return data



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

        # dates = df.index.tolist() # BROKEN: outliers already removed!
        dates = self.dates
        # print(dates)

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