import os
import sys
import numpy as np
import pandas as pd
from datetime import date, datetime, timedelta
from typing import Any
from abc import ABC, abstractmethod

import utils as ut
from data_handlers.OutlierMethods import OutlierStrategy, OutlierParams, ModifiedZ, ModifiedZParams, Raw
from data_handlers.InterpMethods import InterpStrategy, Ffill




class ItemData:
    def __init__(self, item_name:str, base_path:str, outlier_strat:OutlierStrategy,
                 outlier_params:OutlierParams, interp_strategy:InterpStrategy=Ffill):
        self.item_name = item_name
        self.base_path = base_path

        raw_data = self._import_raw_item_data()

        # Raw data with duplicates removed, in a pd.series
        # Missing data added to index and filled with np.nan
        raw_series = self._generate_raw_series(raw_data)

        self.series, altered_data = \
        self._process_data(raw_series, outlier_strat,
                            outlier_params, interp_strategy)
        self.outliers, self.isolated, self.filled = altered_data
        
        
    # === 1. Import item data from JSON ===
    def _import_raw_item_data(self):
        item_filepath = f"{self.base_path}/{self.item_name}.json"
        if not os.path.exists(item_filepath):
            raise Exception(
                f"Faild to load data for {self.item_name}, file not found at: \'{item_filepath}\'")
        raw = ut.load_json(item_filepath)
        return raw['prices']
    # ===== ===== ===== ===== =====


    # === 2. Generate useable series from data ===
    # Control Flow:
    def _generate_raw_series(self, raw_data) -> pd.Series:
        raw_data_list = self._format_raw_data_to_list(raw_data)
        series = self._remove_duplicates(raw_data_list)
        return self._fill_date_gaps(series)
    
    #   HELPER FUNCTIONS:
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

    def _remove_duplicates(self, data_list:list):
        # ONLY DATES AND PRICES STORED (not volume). Accepts self.raw_data_list
        data_list_nv = [(dt, price) for dt, price, _ in data_list]
        df_raw = pd.DataFrame(data=data_list_nv, columns=["date", "price"])
        mean_prices = df_raw.groupby("date", as_index=True)["price"].mean() # returns pd.Series
        if mean_prices[mean_prices.index.duplicated(keep=False)].empty == False:
            raise Exception("Error: Remove duplicates failed")
        return mean_prices.sort_index()

    def _fill_date_gaps(self, series:pd.Series):
        start_date = series.index[0]
        end_date = series.index[-1]
        date_list = pd.date_range(start=start_date, end=end_date)
        date_list = [dt.date() for dt in date_list]
        series_ng = pd.Series(data=np.nan, index=date_list, name="price")
        series_ng.update(series) # adds incomplete price data to df
        return series_ng.sort_index()
    # ===== ===== ===== ===== ===== =====
    

    # === 3. Data processing ===
    # Control Flow:
    def _process_data(self, series:pd.Series, outlier_strat:OutlierStrategy,
                      params:OutlierParams, interp_strat:InterpStrategy):
        series, outliers = self._remove_outliers(series, outlier_strat, params)
        iso_tolerance = self._get_iso_tolerance(params.window)
        series, isolated = self._remove_isolated(series, iso_tolerance)        
        series, filled_data = self._fill_missing_data(series, interp_strat)
        return series, (outliers, isolated, filled_data)
    
    #   Helpers:
    def _remove_outliers(self, series:pd.Series, method:OutlierStrategy,
                      params:list):
        outlier_processor = method(series, params)
        outliers = outlier_processor.get_outliers()
        series = series.drop(outliers.index.to_list())
        series = self._fill_date_gaps(series)
        return series, outliers

    def _fill_missing_data(self, series:pd.Series, strat:InterpStrategy):
        processor = strat(series)
        filled = processor.get_interpolated_data()
        series = processor.get_interpolated_series()
        return series, filled

    def _get_iso_tolerance(self, window):
        # defines tolerance for removing isolated points in terms of outlier
        # rolling window
        return int(np.floor((window/2)))

    def _remove_isolated(self, series:pd.Series, tolerance:int):
        # if tolerance None (i.e. window = None), return unaltered series
        if tolerance == None: return series, pd.Series(dtype=float)

        nan_mask = ~series.isna()
        nan_mask = nan_mask.to_list()
        # nan_mask = [not b for b in nan_mask]
        isolated = {}

        for i, date in enumerate(series.index):
            if not np.isnan(series[date]):
                left = max(0, i - tolerance)
                right = min(len(series), i + tolerance)
                window = nan_mask[left:right]
                if sum(window) <= 2:
                    isolated.update({date : series[date]})

        isolated = pd.Series(isolated).sort_index()
        series = series.drop(isolated.index)

        return self._fill_date_gaps(series), isolated
    # ===== ===== ===== ===== ===== =====


    # === 4. Utils ===
    def show_report(self):
        print(f"Data Processing Report for Item: \"{self.item_name}\"")
        print(f"Outliers removed: {len(self.outliers)} ({self._percent(len(self.outliers), len(self.series))}%)")
        print(f"Isolated points removed: {len(self.isolated)} ({self._percent(len(self.isolated), len(self.series))}%)")
        print(f"Points interpolated: {len(self.filled)} ({self._percent(len(self.filled), len(self.series))}%)")

    def _percent(self, a, b):
        # returns a as a percentage of b
        return np.round(((a/b)*100), decimals=1)
    
    def get_data_quality_score(self):
        return np.round((self._percent(len(self.filled), len(self.series.index))),
                        decimals=1)
    # ===== ===== ===== ===== ===== =====


# OLD:
# class DataReport:
#     def __init__(self, item_name:str, raw_series:pd.Series, series:pd.Series, outliers:pd.Series,
#                  isolated:pd.Series, filled:pd.Series):
#         self.item_name = item_name
#         self.raw_series = raw_series
#         self.series = series
#         self.outliers = outliers
#         self.isolated = isolated
#         self.filled = filled
#         pass

#     def show_report(self):
#         print(f"Data Processing Report for Item: {self.item_name}")
#         print(f"Outliers removed: {len(self.outliers)}")
#         print(f"Isolated points removed: {len(self.isolated)}")
#         print(f"Points interpolated: {len(self.filled)}")

