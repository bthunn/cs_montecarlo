import os
import numpy as np
import pandas as pd
from datetime import date, datetime, timedelta
from typing import Any

import utils as ut

class ItemPrice:
    def __init__(self, item_name:str, base_path:str):
        self.item_name = item_name
        self.base_path = base_path

        raw_data = self._import_raw_item_data()
        self.raw_data_list = self._format_raw_data_to_list(raw_data)
        
    def get_raw_series(self) -> pd.Series:
        # returns series with no duplicates and missing prices filled with np.nan
        s = self._convert_list_to_series(self.raw_data_list)
        return self._fill_date_gaps(s)
    
    def set_raw_series(self):
        self.raw_series = self.get_raw_series()


    def _import_raw_item_data(self):
        item_filepath = f"{self.base_path}/{self.item_name}.json"
        if not os.path.exists(item_filepath):
            raise Exception(
                f"Faild to load data for {self.item_name}, file not found at: \'{item_filepath}\'")
        raw = ut.load_json(item_filepath)
        return raw['prices']
    # \/ 
    def _format_raw_data_to_list(self, raw_data):
        # returns list of tuples in form (date, price, volume)
        price_data_list = []
        for entry in raw_data:
            date_split = entry[0].split()
            date_str_filtered = f"{date_split[0]} {date_split[1]} {date_split[2]}"
            converted_date = datetime.strptime(date_str_filtered, "%b %d %Y")
            price = entry[1]
            volume = int(entry[2])
            price_data_list.append((converted_date, price, volume))

        if len(price_data_list) == len(raw_data):
            return price_data_list
        else:
            raise Exception("Error: price data list length does not match after processing")


    def _convert_list_to_series(self, data_list:list):
        # ONLY DATES AND PRICES STORED (not volume). Accepts self.raw_data_list
        data_list_nv = [(dt, price) for dt, price, _ in data_list]
        df_raw = pd.DataFrame(data=data_list_nv, columns=["date", "price"])
        mean_prices = df_raw.groupby("date", as_index=True)["price"].mean() # returns pd.Series
        if mean_prices[mean_prices.index.duplicated(keep=False)].empty == False:
            raise Exception("Error: Remove duplicates failed")
        return mean_prices.sort_index()
    # \/
    def _fill_date_gaps(self, series:pd.Series):
        start_date = series.index[0]
        end_date = series.index[-1]
        date_list = pd.date_range(start=start_date, end=end_date)
        date_list = [dt.date() for dt in date_list]
        series_ng = pd.Series(data=np.nan, index=date_list, name="price")
        series_ng.update(series) # adds incomplete price data to df
        return series_ng

