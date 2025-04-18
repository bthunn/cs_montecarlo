import os
import sys
import numpy as np
import pandas as pd
from datetime import date, datetime, timedelta
from typing import Any

import utils as ut
from .ItemData import ItemData
from .ProcessorParams import ProcessorParams

class PortfolioContructor:
    def __init__(self, item_list:list, item_data_path:str,
                 processor_params:ProcessorParams):
        self.item_list = item_list
        self.processor_params = processor_params
        self._check_item_list_formatting(item_list)
        self._check_item_data_exists(item_data_path)
        self.df = self._get_processed_dataframe(item_data_path, processor_params)

    
    def _check_item_list_formatting(self, item_list):
        for item in item_list:
            if not item == ut.format_markethashname(item):
                raise Exception("item_list names must have correct formatting")

    def _check_item_data_exists(self, path):
        counter = 0
        for item in self.item_list:
            if not os.path.exists(
                f"{path}/{ut.format_markethashname(item)}.json"
                ):
                counter += 1
        if counter > 0: 
            raise Exception(
            f"Item price data missing for {counter} items. \
                Import up-to-date price information to continue"
                )

    def _get_processed_dataframe(self, path, params:ProcessorParams):
        # returns a dataframe of historical item prices for all items in item_list
        outlier_strategy = params.outlier_strategy
        outlier_params = params.outlier_params
        interp_strategy = params.interp_strategy

        start_date = date(2013,8,1)
        end_date = date.today() + timedelta(days=1)
        date_list = pd.date_range(start=start_date, end=end_date)
        date_list = [dt.date() for dt in date_list]
        df = pd.DataFrame(None, index=date_list)

        for i, item in enumerate(self.item_list):
            item_data = ItemData(item, path, outlier_strategy, outlier_params, interp_strategy)
            df[item] = item_data.series

        return df

    def get_trimmed_df(self):
        df = self.df
        start_date = max(df.apply(lambda col: col.first_valid_index()))
        end_date = min(df.apply(lambda col: col.last_valid_index()))
        return df.loc[start_date:end_date]

    def export_df_to_csv(df:pd.DataFrame, path:str):
        df.to_csv(path_or_buf=path, )

        

