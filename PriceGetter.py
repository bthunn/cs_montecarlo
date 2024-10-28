import json
import requests
import time
import os
import re
from datetime import date

class PriceGetter:
    def __init__(self, item_list, cookies):
        self.base_url = "https://steamcommunity.com/market/pricehistory/?country=gb&currency=3\\&appid=730&market_hash_name="
        self.item_list = item_list # list of market_hash_name for all items in inv
        self.cookies = cookies

    def get_response(self, url):
        response = requests.get(url, cookies=self.cookies)
        return response

    def get_item_data(self, url):
        response = self.get_response(url)
        sucess_status = False
        data = response.json()

        # if response.status_code == 200:
        #     # data = response.json()
        #     # with open(f'price_data.json', 'w', encoding="utf-8") as file:
        #     #     file.write(json.dumps(data, ensure_ascii=False))
        #     sucess_status = True
        # else:
        #     print("Failed to retrieve data:", response.status_code)

        return data, response.status_code

    def get_data_for_item_list(self):
        def _replace_unprintable(text, placeholder='?'):
            # Encode the string to bytes, ignoring errors, then decode back to string
            return text.encode('ascii', 'replace').decode().replace('?', placeholder)
        def _replace_invalid_chars_for_filepath(text, placeholder='-'):
            invalid_chars = r'[<>:"/\\|?*]'
            return re.sub(invalid_chars, placeholder, _replace_unprintable(text))
        
        range_ = len(self.item_list)
        # range_ = 3
        item_price_list = [0] * range_
        for i in range(range_):
            item = self.item_list[i]

            if not os.path.exists(f"data\\price-data-{date.today()}\\{_replace_invalid_chars_for_filepath(item)}.json"):
                request_interval = 0 # wait time in s
                data, status_code = self.get_item_data(f"{self.base_url}{item}")
                while status_code != 200:
                    if status_code == 429:
                        print(f"Rate limit hit. Retrying in {request_interval} seconds...")
                        time.sleep(request_interval)
                        request_interval = 1 + request_interval*2
                    else:
                        print(f"Request failed, status: {status_code}")
                
                with open(f'data\\price-data-{date.today()}\\{_replace_invalid_chars_for_filepath(item)}.json', 'w', encoding="utf-8") as file:
                    file.write(json.dumps(data, ensure_ascii=False))
                
                print(f"Data for item: {_replace_unprintable(item)} succesfully retrieved")
                # print(f"contents: {_replace_unprintable(data)}")
                item_price_list[i] = data
            else:
                print(f"Data for item: {_replace_unprintable(item)} already exists, skipping request")
        return item_price_list
        
        # for item in item_price_list:
        #     print(_replace_unprintable(item['price_prefix']))
        # return item_price_list
            
            # with open(f'data\price-data\{item}.json', 'w', encoding="utf-8") as file:
            #     file.write(json.dumps(data, ensure_ascii=False))


# # Set up the URL and parameters
# url = "https://steamcommunity.com/market/pricehistory/"
# params = {
#     "country": "gb",
#     "currency": "3",
#     "appid": "730",
#     "market_hash_name": "Sticker%20|%20Team%20LDLC.com%20|%20DreamHack%202014"
# }

# # Replace with your actual session cookies
# cookies = {
#     "sessionid": "1bc5949f3ee1adabe5bc6c2a",
#     "steamLoginSecure": "76561198149693785%7C%7CeyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0.eyAiaXNzIjogInI6MTAyOF8yNTQxQ0EzN18zODFFRCIsICJzdWIiOiAiNzY1NjExOTgxNDk2OTM3ODUiLCAiYXVkIjogWyAid2ViOmNvbW11bml0eSIgXSwgImV4cCI6IDE3MzAxODAyNzEsICJuYmYiOiAxNzIxNDUyMTU4LCAiaWF0IjogMTczMDA5MjE1OCwgImp0aSI6ICIxMDIxXzI1NDFDQTM2XzcxQjI0IiwgIm9hdCI6IDE3MzAwOTIxNTgsICJydF9leHAiOiAxNzMyNjcxNjI4LCAicGVyIjogMCwgImlwX3N1YmplY3QiOiAiMTQzLjE1OS4xNzIuMTE0IiwgImlwX2NvbmZpcm1lciI6ICIxNDMuMTU5LjE3Mi4xMTQiIH0.DvBClrpajLmQXgbfRJH5JvhnpEcrpOc0IE-U7up7jefTjfNnTjYeGh0sRTVbAXR2sqMcT3uOJJAWDupwBtKZAQ"
# }

# # Make the request
# # response = requests.get(url, params=params, cookies=cookies)
# response = requests.get('https://steamcommunity.com/market/pricehistory/?country=gb&currency=3\&appid=730&market_hash_name=%E2%98%85%20Bayonet%20|%20Blue%20Steel%20(Minimal%20Wear)', cookies=cookies)

# def get_data(): 
#     if response.status_code == 200:
#         data = response.json()
#         with open(f'price_data.json', 'w', encoding="utf-8") as file:
#             file.write(json.dumps(data, ensure_ascii=False))
#     else:
#         print("Failed to retrieve data:", response.status_code)
