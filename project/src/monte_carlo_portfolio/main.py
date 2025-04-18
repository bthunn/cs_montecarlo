
import os
from datetime import date, datetime
import requests
import json

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from data_handlers.ItemLoaders import ItemLoaderStrategy, LoadFromListJSON, LoadFromInvJSON, LoadFromInvID
from data_handlers.ItemData import ItemData
from data_handlers.OutlierMethods import OutlierStrategy, OutlierParams, Raw, ModifiedZ, ModifiedZParams
import visuals as vis

def main():
    # === 1. Load item list ===
    # strategies:
    # LoadFromListJSON - load item list from list stored as JSON
    # LoadFromInvJSON - load from inv JSON from API
    # LoadFromInvID - load from inv ID, gets from API
    file_path = r"project/data/raw_data/inventories/one-item-inv.json"
    inv_loader = LoadFromInvJSON(path=file_path, marketable=True)
    item_list = inv_loader.get_list()


    # === 2. Get and process price data for items ===
    price_base_path = r"project/data/raw_data/item_prices/price-data-2024-10-28"
    # Parameters for the outlier detection method
    outlier_params = ModifiedZParams(window=10, threshold=3.5, eps=1, mad_cap=np.inf)
    # Instantiate ItemData
    item_data = ItemData(item_list[0], price_base_path, ModifiedZ, outlier_params)
    # Visualise Data
    vis.post_processor_plot(
        item_data.series, item_data.outliers, item_data.isolated, item_data.filled)
    item_data.show_report()


if __name__ == "__main__":
    main()