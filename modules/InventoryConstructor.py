import json
from datetime import date
from datetime import datetime
from datetime import timedelta
import pandas as pd
import matplotlib as plt
import numpy as np
import os
from modules import functions as fn
from modules import visuals as vis
from modules import dataAnalysisFunctions as dat

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
            # self.raw_price_data_dict = self._get_raw_price_data() # ONLY NEEDED IF EXTRACTING RAW DATA, COMMENT OUT OTHERWISE
            self.df_full, self.df_filtered, self.date_interval = self._process_price_data_as_df() # adds series iteratively to a df as columns
                        
            # OLD dict method:
            # self.date_interval = self._find_date_interval()
            # print(self.date_interval)
            # self.aligned_dict = self._make_aligned_dict()

            # testing:
            # print(self.aligned_dict.keys())
            # for key, item in self.aligned_dict.items():
            #     print(f"key: {key} items: {len(item)}")
            #####################

            # self.inv_data_frame = self._format_to_dataframe() # FINAL 
        


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
    

    def _get_raw_price_data(self): # same as below but cuts out data cleaning
        filtered_price_data_dict = {}
        for item_name, price_data in self.price_data_dict.items():
            print(f"Now processing item: \"{item_name}\"")
            data_processor = DataProcessor(price_data)
            filtered_price_data_dict.update({f"{item_name}": data_processor.get_raw_data()})

        if self.price_data_dict.keys() == filtered_price_data_dict.keys(): # check keys match
            return filtered_price_data_dict
        else:
            raise Exception("ERROR dict keys don't match after data processing")


    def _process_price_data(self): # (OLD) runs DataProcessor.get_processed_item_data() on each dict entry
        cleaned_price_data_dict = {}
        for item_name, price_data in self.price_data_dict.items():
            print(f"Now processing item: \"{item_name}\"")
            data_processor = DataProcessor(price_data)
            cleaned_price_data_dict.update(
                {f"{item_name}": data_processor.get_processed_item_data_as_list()}
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


    def _process_price_data_as_df(self):
        date_range = [date(2013,8,1), date.today()] # all possible dates included atp
        date_list = pd.date_range(start=date_range[0], end=date_range[1])
        date_list = [dt.date() for dt in date_list]
        df = pd.DataFrame(None, index=date_list)
        start_date = date(1900,1,1)
        end_date = date.today() + timedelta(days=1)
        for item_name, price_data in self.price_data_dict.items():
            print(f"Now processing item: \"{item_name}\"")

            data_processor = DataProcessor(price_data)
            item_data = data_processor.get_processed_item_data() # series
            df[item_name] = item_data

            # updates date_lims to the smallest available date range
            if item_data.index[0] > start_date:
                start_date = item_data.index[0]
            if item_data.index[-1] < end_date:
                end_date = item_data.index[-1]

        if len(df.columns) == len(self.price_data_dict):
            return df, df[start_date:end_date], [start_date, end_date]
        else:
            raise Exception("ERROR number of df columns don't match number of items after data processing")
        



class DataProcessor: # basically just wraps ItemData. Probably shouldn't exist
    def __init__(self, price_data): # pass in ITEM PRICE DATA
        self.item_data = ItemData(price_data)
       
    # def get_processed_item_prices(self): # return list of prices
    #     return self.item_data.prices_clean
    
    def get_processed_item_data(self): # returns a series
        return self.item_data.series
    
    def get_processed_item_data_as_list(self):
        return
        
    
    def get_raw_data(self):
        return self.item_data.price_data



class ItemData:
    def __init__(self, raw_data):
        self.raw_data = raw_data
        self.data_handler = DataHandler(self.raw_data)
        # prices_all = self.data_handler.prices
        # sdates = self.data_handler.dates
        self.price_data = self.data_handler.zipped_data # dates and prices in a 2d list
        data_cleaner = dataCleaner(self.price_data)

        # final product:
        self.series = data_cleaner.series_clean

        # self.processed_item_data = self._generate_2d_processed_data()

    def plot_cleaned_data(self, start_date=date(1900,1,1), end_date=date(1900,1,1)):
        dataCleaner.plot_cleaned_data(self.data_cleaner, start_date, end_date)

    def _generate_2d_processed_data(self):
        data = [0] * len(self.prices_clean)
        for i in range(len(self.prices_clean)):
            data[i] = [self.dates[i], self.prices_clean[i]]

        return data



class DataHandler: # formats raw price data from json ()
    def __init__(self, raw_data):
        self.raw_data = raw_data
        self.dates = self._convert_dates()
        self.prices = self._extract_prices()
        self.zipped_data = self._zip_data(self.dates, self.prices)

        self.volumes = self._extract_volumes()
        self.zipped_volumes = self._zip_data(self.dates, self.volumes)

    
    def _convert_dates(self):
        dates_str = [sublist[0] for sublist in self.raw_data]
        dates_split = [date.split() for date in dates_str] # split string into ['mmm', 'dd, 'yyyy', ...]
        dates_str_simple = [f"{date[0]} {date[1]} {date[2]}" for date in dates_split]
        converted_dates = [datetime.strptime(date, "%b %d %Y").date() for date in dates_str_simple]
        return converted_dates
    

    def _extract_prices(self):
        return [sublist[1] for sublist in self.raw_data]
    
    def _extract_volumes(self):
        return [int(sublist[2]) for sublist in self.raw_data]

    def _zip_data(self, dates, prices):
        zipped_data = []
        for i in range(len(dates)):
            zipped_data.append([dates[i], prices[i]])
        return zipped_data


    
class dataCleaner: # filters outliers, interpolates missing data. SET DATA CLEANING PARAMS HERE
    def __init__(self, raw_data):
        # Outlier filter params:
        self.window_size = 7
        self.threshold = 3.5 # sets the modified z score theshold
        self.eps = 1 # sets the offset added to the MAD (to ignore small price fluctuations when MAD is low)
        self.mad_cap = 10 # sets the minimum MAD, preventing high volatility from hiding outliers
        self.raw_data = raw_data # 2D list of dates and prices
        raw_dates, raw_prices = self._unzip_raw_data(raw_data)

        self.series_no_dupes_no_gaps = self._construct_series(raw_data, raw_dates, raw_prices)
        self.outliers = self._find_outliers(self.series_no_dupes_no_gaps)
        self.series_clean, self.interpolated = self._handle_outliers(self.series_no_dupes_no_gaps, self.outliers, raw_dates)
        self.series_clean.sort_index(inplace=True)

        # For plotting purposes:
        interpolated_prices = self.series_clean[self.interpolated.index]
        # vis.outlier_plot(self.series_no_dupes_no_gaps, self.outliers)
        # vis.outlier_plot(self.series_clean, self.outliers, interpolated_prices)
        

    def _handle_outliers(self, series:pd.Series, outliers, raw_dates):
        series_no_outliers = self._delete_outliers(series, outliers)
        series_clean = self._remove_date_gaps(raw_dates, series_no_outliers)
        series_clean = series_clean.sort_index()
        interpolated = self._flag_missing_prices(series_clean)
        series_clean = series_clean.ffill()
        return series_clean, interpolated


    def _find_outliers(self, series):
        outliers_right = self._flag_outliers(series, window=self.window_size,
                                             threshold=self.threshold, eps=self.eps, mad_cap=self.mad_cap,
                                             func=dat.detect_outliers_modified_z_modified)
        outliers_left = self._flag_outliers(series, window=self.window_size, # not sure this works/does anything
                                            threshold=self.threshold, eps=self.eps, mad_cap=self.mad_cap,
                                            func=dat.detect_outliers_modified_z_modified_left) 
        isolated_dict = dat.detect_isolated(series, tolerance=3)
        out2_dict = outliers_right.to_dict()
        out3_dict = outliers_left.to_dict()
        outliers = {**isolated_dict, **out2_dict}
        outliers = {**outliers, **out3_dict}
        outliers = pd.Series(outliers)
        outliers.sort_index(inplace=True)
        return outliers


    def _unzip_raw_data(self, raw_data):
        raw_dates = [sublist[0] for sublist in raw_data]
        raw_prices = [sublist[1] for sublist in raw_data]
        return raw_dates, raw_prices


    def _construct_series(self, raw_data, raw_dates, raw_prices):
        series_no_dupes = self._consolidate_duplicate_data(raw_data)
        series_no_dupes_no_gaps = self._remove_date_gaps(raw_dates, series_no_dupes)

        return series_no_dupes_no_gaps
    
    def _consolidate_duplicate_data(self, raw_data):
        df_raw = pd.DataFrame(raw_data, columns=["date", "price"])
        mean_prices = df_raw.groupby("date", as_index=True)["price"].mean() # pd.Series
        if mean_prices[mean_prices.index.duplicated(keep=False)].empty == False:
            raise Exception("Error: Remove duplicates failed")
        return mean_prices

    def _remove_date_gaps(self, raw_dates, mean_prices:pd.Series): # takes a SERIES (mean_prices)
        date_range = [raw_dates[0], raw_dates[-1]] # list of datetime.date
        date_list = pd.date_range(start=date_range[0], end=date_range[1])
        date_list = [dt.date() for dt in date_list]
        series = pd.Series(data=np.nan, index=date_list, name="price")
        series.update(mean_prices) # adds incomplete price data to df
        return series

    def _flag_outliers(self, series, window, threshold, eps, mad_cap, func):
        mask = func(series,window=window, threshold=threshold, eps=eps, mad_cap=mad_cap)
        outliers = series[mask]
        return outliers
    
    def _flag_outliers_med(self, s, window, threshold):
        mask = dat.detect_outliers_rolling_med(s, window, threshold)
        outliers = s[mask]
        return outliers
    

    def _delete_outliers(self, series:pd.Series, outliers:pd.Series):
        # outlier_dates = outliers.index.tolist()
        series_no_outliers = series.drop(outliers.index.to_list())
        return series_no_outliers

    def _flag_missing_prices(self, series:pd.Series):
        return series[series.isna()]


    def _interpolate_missing_prices_linear(self, series:pd.Series):
        series_interp = series.interpolate(method='linear', axis=0)
        return series_interp

    def _interpolate_missing_prices_time(self, series:pd.Series):
        series_interp = series.interpolate(method='time', axis=0)
        return series_interp


    def _find_longest_data_gap(self, prices):
        n = 0
        longest_gap = 0
        for price in prices:
            if np.isnan(price):
                n += 1
                if n > longest_gap:
                    longest_gap = n
            else:
                n = 0
        return longest_gap


    def data_report(self): # TO DO: give report on data quality and cleaning done (outliers, missing data, dupes, etc)
        
        pass