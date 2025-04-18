import os
import numpy as np
import pandas as pd
from datetime import date, datetime, timedelta
from typing import Any

import utils as ut
from project.src.monte_carlo_portfolio.data_handlers.ItemData import ItemPrice

class PortfolioData:
    def __init__(self, item_list, price_data_dir_path):
        self._check_item_list(item_list)
        self.item_list = item_list

        self._check_item_data_exists(price_data_dir_path)

    
    def _check_item_list(item_list):
        for item in item_list:
            if not item == ut.format_markethashname(item):
                raise Exception("item_list names must have correct formatting")


    def _check_item_data_exists(self):
        counter = 0
        for item in self.item_list:
            if not os.path.exists(
                f"data\\price-data-{date.today()}\\{ut.format_markethashname(item)}.json"
                ):
                counter += 1
        if counter > 0: 
            raise Exception(
            f"Item price data missing for {counter} items. \
                Import up-to-date price information to continue"
                )


    def _get_price_data(self, item_name):
        pass


    def _get_processed_series():
        pass
        

print()

