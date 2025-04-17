
import os
from datetime import date, datetime
import requests
import json

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from data_handlers.ItemLoaders import ItemLoaderStrategy, LoadFromListJSON, LoadFromInvJSON, LoadFromInvID
from data_handlers.PriceHandlers import ItemData
from data_handlers.OutlierMethods import OutlierStrategy, OutlierParams, Raw, ModifiedZ, ModifiedZParams


def main():
    # main flow:
    # get item_list from JSON, INV JSON or INV ID
    # give item list to data loaders
    

    # === 1. Package item list path and type for Data Loader ===
    # strategies:
    # LoadFromListJSON - load item list from list stored as JSON
    # LoadFromInvJSON - load from inv JSON from API
    # LoadFromInvID - load from inv ID, gets from API

    file_path = r"project/data/raw_data/inventories/one-item-inv.json"
    strategy = LoadFromInvJSON(path=file_path, marketable=True)
    item_list = strategy.get_list()

    price_base_path = r"project/data/raw_data/item_prices/price-data-2024-10-28"
    # Parameters for the outlier detection method
    outlier_params = ModifiedZParams(window=7, threshold=3.5, eps=1, mad_cap=np.inf)
    item_data = ItemData(item_list[0], price_base_path, ModifiedZ, outlier_params)
    print(f"data: \n{item_data.series}")
    print(f"outliers: \n{item_data.outliers}")
    print(f"filled: \n{item_data.filled_data}")







    


    pass

def get_item_list(info:str, strategy:ItemLoaderStrategy):
    if not len(info) == 0:
        return strategy.get_list(info)


if __name__ == "__main__":
    main()