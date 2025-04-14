import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import requests
import json
from datetime import datetime
from datetime import date
import pandas as pd
import pandas_datareader as pdr
import os

from modules.PriceGetter import PriceGetter
from modules import functions as fn
from modules.InventoryConstructor import InventoryData
from modules.Simulation import Simulation
from modules import visuals as vis


BASE_URL = "https://steamcommunity.com/market/pricehistory/"

# to get inventory list, use https://steamcommunity.com/profiles/76561198149693785/inventory/json/730/2
# where the large number is the profile ID and 730 is CS2's game ID


def main():
    sub_main()



def sub_main():
    # base directory containing data for items
    item_data_base_path = r"F:\programs\python\cs_montecarlo\data\price-data-2024-10-28"

    # test_inv_raw_data = loadJSON(
    # r"F:\programs\python\cs_montecarlo\data\test-inventory-from-steamwebapi-2024-10-28.json" # filepath of list of inv items, from steam web api
    #     ).data
    
    # TEST:
    test_inv_raw_data = fn.loadJSON(
    r"F:\programs\python\cs_montecarlo\data\three-item-inv.json" # filepath of list of inv items, from steam web api
        ).data
 
    # HOW TO GET VALUES:
    # browse session cookies. Update as necessary by viewing Network -> search:"domain:steamcommunity.com scheme:https"
    # and find 'cookie:'. These fields will be included, copy them in
    cookies = {
        "sessionid": "1bc5949f3ee1adabe5bc6c2a",
        "steamLoginSecure": "76561198149693785%7C%7CeyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0.eyAiaXNzIjogInI6MTAyOF8yNTQxQ0EzN18zODFFRCIsICJzdWIiOiAiNzY1NjExOTgxNDk2OTM3ODUiLCAiYXVkIjogWyAid2ViOmNvbW11bml0eSIgXSwgImV4cCI6IDE3MzAxODAyNzEsICJuYmYiOiAxNzIxNDUyMTU4LCAiaWF0IjogMTczMDA5MjE1OCwgImp0aSI6ICIxMDIxXzI1NDFDQTM2XzcxQjI0IiwgIm9hdCI6IDE3MzAwOTIxNTgsICJydF9leHAiOiAxNzMyNjcxNjI4LCAicGVyIjogMCwgImlwX3N1YmplY3QiOiAiMTQzLjE1OS4xNzIuMTE0IiwgImlwX2NvbmZpcm1lciI6ICIxNDMuMTU5LjE3Mi4xMTQiIH0.DvBClrpajLmQXgbfRJH5JvhnpEcrpOc0IE-U7up7jefTjfNnTjYeGh0sRTVbAXR2sqMcT3uOJJAWDupwBtKZAQ"
    }

    test_inventory = InventoryData(test_inv_raw_data, item_data_base_path).inv_data_frame
    # sim = Simulation(test_inventory)


    # price_getter = PriceGetter(item_list=test_inventory.item_list_marketable, cookies=cookies)
    # # format of item_price_list is a list of price data responses, so a list of dictionaries
    # item_price_list = price_getter.get_data_for_item_list() 
    # with open(f'data\\test-inv-price-data-set-{date.today()}.json', 'w', encoding="utf-8") as file:
    #         file.write(json.dumps(item_price_list, ensure_ascii=False))



def get_request(item_name, skin_name, condition):
    country = 'gb'
    currency = '3'
    endpoint = f'{BASE_URL}?country={country}&currency={currency}\\&appid=730&market_hash_name={item_name}%20|%20{skin_name}%20({condition})'
    return endpoint

if __name__ == "__main__":
      main()
