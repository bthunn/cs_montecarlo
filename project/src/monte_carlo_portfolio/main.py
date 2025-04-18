
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
from data_handlers.InterpMethods import InterpStrategy, Ffill
from data_handlers.ProcessorParams import ProcessorParams
from data_handlers.PortfolioConstructor import PortfolioContructor
import visuals as vis

def main():
    # === 1. Load item list ===
    # strategies:
    # LoadFromListJSON - load item list from list stored as JSON
    # LoadFromInvJSON - load from inv JSON from API
    # LoadFromInvID - load from inv ID, gets from API
    file_path = r"project/data/raw_data/inventories/three-item-inv.json"
    inv_loader = LoadFromInvJSON(path=file_path, marketable=True)
    item_list = inv_loader.get_list()

   
    # # === 2. Get and process price data for items ===
    price_base_path = r"project/data/raw_data/item_prices/price-data-2024-10-28"
    outlier_params = ModifiedZParams(window=10, threshold=3.5, eps=1, mad_cap=np.inf)
    processor_params = ProcessorParams(outlier_strategy= ModifiedZ,
                                       outlier_params= outlier_params,
                                       interp_strategy= Ffill)
    
    portfolio_data = PortfolioContructor(item_list= item_list,
                                         item_data_path= price_base_path,
                                         processor_params= processor_params)

    trimmed_df = portfolio_data.get_trimmed_df()
    PortfolioContructor.export_df_to_csv(trimmed_df, r"F:\programs\python\cs_montecarlo\project\data\processed_data\dataframe_test.csv")
    
    # Visualise Data
    # vis.post_processor_plot(
    #     item_data.series, item_data.outliers, item_data.isolated, item_data.filled)
    # item_data.show_report()


if __name__ == "__main__":
    main()