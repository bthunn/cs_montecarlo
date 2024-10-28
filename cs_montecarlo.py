import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import requests
import json
from datetime import datetime
from datetime import date
import pandas as pd
import os
from modules.PriceGetter import PriceGetter
from modules import functions as fn
from modules.DataProcessor import DataProcessor


BASE_URL = "https://steamcommunity.com/market/pricehistory/"

def main():
    sub_main()

def sub_main():
    test_inv_raw_data = loadJSON(
    r"F:\programs\python\cs_montecarlo\data\test-inventory-from-steamwebapi-2024-10-28.json" # filepath of list of inv items, from steam web api
        ).data
    
    # browse session cookies. Update as necessary by viewing Network -> search:"domain:steamcommunity.com scheme:https"
    # and find 'cookie:'. These fields will be included, copy them in
    cookies = {
        "sessionid": "1bc5949f3ee1adabe5bc6c2a",
        "steamLoginSecure": "76561198149693785%7C%7CeyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0.eyAiaXNzIjogInI6MTAyOF8yNTQxQ0EzN18zODFFRCIsICJzdWIiOiAiNzY1NjExOTgxNDk2OTM3ODUiLCAiYXVkIjogWyAid2ViOmNvbW11bml0eSIgXSwgImV4cCI6IDE3MzAxODAyNzEsICJuYmYiOiAxNzIxNDUyMTU4LCAiaWF0IjogMTczMDA5MjE1OCwgImp0aSI6ICIxMDIxXzI1NDFDQTM2XzcxQjI0IiwgIm9hdCI6IDE3MzAwOTIxNTgsICJydF9leHAiOiAxNzMyNjcxNjI4LCAicGVyIjogMCwgImlwX3N1YmplY3QiOiAiMTQzLjE1OS4xNzIuMTE0IiwgImlwX2NvbmZpcm1lciI6ICIxNDMuMTU5LjE3Mi4xMTQiIH0.DvBClrpajLmQXgbfRJH5JvhnpEcrpOc0IE-U7up7jefTjfNnTjYeGh0sRTVbAXR2sqMcT3uOJJAWDupwBtKZAQ"
    }

    test_inventory = InventoryData(test_inv_raw_data)
    
    # price_getter = PriceGetter(item_list=test_inventory.item_list_marketable, cookies=cookies)
    # # format of item_price_list is a list of price data responses, so a list of dictionaries
    # item_price_list = price_getter.get_data_for_item_list() 
    # with open(f'data\\test-inv-price-data-set-{date.today()}.json', 'w', encoding="utf-8") as file:
    #         file.write(json.dumps(item_price_list, ensure_ascii=False))



class InventoryData:
    def __init__(self, raw_json):
        self.raw_json = raw_json
        self.item_list = self._get_list_of_market_hash_names()
        self.item_list_marketable = self._get_list_of_filtered_market_hash_names()

        # raises excpetion if check fails
        if self._check_inv_item_data_present: self.price_data_dict = self._load_item_price_data_to_dict()
        self.cleaned_price_data_dict = self._process_price_data()

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

            if os.path.exists(
                f"data\\price-data-{date.today()}\\{item_filename}.json"
                ):

                with open(
                    f'data\\price-data-{date.today()}\\{item_filename}.json', 'r', encoding="utf-8"
                    ) as file:
                    item_data = json.load(file)
                # item_price_list.append(item_data['prices'])
                item_price_dict.update({f"{item_filename}": item_data['prices']})

            else:
                print(f"Faild to load data for {fn.replace_unprintable(item)}, file not found")

        # if len(item_price_dict.keys()) == len(self.item_list_marketable):
        #     return item_price_dict
        # else: raise Exception("ERROR: incomplete price data")
        return item_price_dict

    # def _generate_price_dict_from_list(self):
    #     item_dict = {}
    #     for i in range(len(self.item_price_data)):
    #         item_dict.update({f"{self.item_list_marketable[i]}": f"{self.item_price_data[i]}"})
    #     return item_dict


    def _process_price_data(self):
        cleaned_price_data_dict = {}
        for item_name, price_data in self.price_data_dict.items():
            data_processor = DataProcessor(price_data)
            cleaned_price_data_dict.update({f"{item_name}": data_processor.get_processed_item_data()})
        
        if self.price_data_dict.keys() == cleaned_price_data_dict.keys(): 
            return cleaned_price_data_dict
        else:
            raise Exception("ERROR dict keys don't match after processing")

            

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
    endpoint = f'{BASE_URL}?country={country}&currency={currency}\&appid=730&market_hash_name={item_name}%20|%20{skin_name}%20({condition})'
    return endpoint

if __name__ == "__main__":
      main()
