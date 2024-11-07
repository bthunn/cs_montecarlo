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
from modules.DataProcessor import DataProcessor
from modules.Simulation import Simulation


BASE_URL = "https://steamcommunity.com/market/pricehistory/"

def main():
    sub_main()

def sub_main():
    # base directory containing data for items
    item_data_base_path = r"F:\programs\python\cs_montecarlo\data\price-data-2024-10-28"

    test_inv_raw_data = loadJSON(
    r"F:\programs\python\cs_montecarlo\data\test-inventory-from-steamwebapi-2024-10-28.json" # filepath of list of inv items, from steam web api
        ).data
    
    # HOW TO GET VALUES:
    # browse session cookies. Update as necessary by viewing Network -> search:"domain:steamcommunity.com scheme:https"
    # and find 'cookie:'. These fields will be included, copy them in
    cookies = {
        "sessionid": "1bc5949f3ee1adabe5bc6c2a",
        "steamLoginSecure": "76561198149693785%7C%7CeyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0.eyAiaXNzIjogInI6MTAyOF8yNTQxQ0EzN18zODFFRCIsICJzdWIiOiAiNzY1NjExOTgxNDk2OTM3ODUiLCAiYXVkIjogWyAid2ViOmNvbW11bml0eSIgXSwgImV4cCI6IDE3MzAxODAyNzEsICJuYmYiOiAxNzIxNDUyMTU4LCAiaWF0IjogMTczMDA5MjE1OCwgImp0aSI6ICIxMDIxXzI1NDFDQTM2XzcxQjI0IiwgIm9hdCI6IDE3MzAwOTIxNTgsICJydF9leHAiOiAxNzMyNjcxNjI4LCAicGVyIjogMCwgImlwX3N1YmplY3QiOiAiMTQzLjE1OS4xNzIuMTE0IiwgImlwX2NvbmZpcm1lciI6ICIxNDMuMTU5LjE3Mi4xMTQiIH0.DvBClrpajLmQXgbfRJH5JvhnpEcrpOc0IE-U7up7jefTjfNnTjYeGh0sRTVbAXR2sqMcT3uOJJAWDupwBtKZAQ"
    }

    test_inventory = InventoryData(test_inv_raw_data, item_data_base_path)
    print(test_inventory.data_frame)

    # price_getter = PriceGetter(item_list=test_inventory.item_list_marketable, cookies=cookies)
    # # format of item_price_list is a list of price data responses, so a list of dictionaries
    # item_price_list = price_getter.get_data_for_item_list() 
    # with open(f'data\\test-inv-price-data-set-{date.today()}.json', 'w', encoding="utf-8") as file:
    #         file.write(json.dumps(item_price_list, ensure_ascii=False))

class InventoryData:
    def __init__(self, raw_inv_json, item_data_base_path):
        self.raw_json = raw_inv_json
        self.item_data_base_path = item_data_base_path
    
        self.item_list = self._get_list_of_market_hash_names()
        self.item_list_marketable = self._get_list_of_filtered_market_hash_names() # gets only items listed on market

        # raises excpetion if check fails.
        if self._check_inv_item_data_present: 
            self.price_data_dict = self._load_item_price_data_to_dict() # dict in format {"item" : [prices]}
        self.cleaned_price_data_dict = self._process_price_data() # keys in filename format (incompatable chars replaced)
        self.date_interval = self._find_date_interval()
        self.aligned_dict = self._make_aligned_dict()
        self.data_frame = self._format_to_dataframe()

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
            return False
        else:
            return True

    def _load_item_price_data_to_dict(self):
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
        for item in self.aligned_dict:
            print(len(item))
        print(self.aligned_dict[fn.replace_invalid_chars_for_filepath(self.item_list_marketable[0])])

        # return pd.DataFrame.from_dict(self.aligned_dict)






class loadJSON:
    def __init__(self, path):
        self.data = self._get_data_from_json(path)

    def _get_data_from_json(self, path):
        with open(path, 'r', encoding="utf-8") as file:
            data = json.load(file)
            return data

def get_request(item_name, skin_name, condition):
    country = 'gb'
    currency = '3'
    endpoint = f'{BASE_URL}?country={country}&currency={currency}\\&appid=730&market_hash_name={item_name}%20|%20{skin_name}%20({condition})'
    return endpoint

if __name__ == "__main__":
      main()
