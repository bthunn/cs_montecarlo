import numpy as np
import pandas as pd
import json

from InventoryConstructor import InventoryData
import functions as fn
import visuals as vis


def main():
    # data = create_data()
    data = get_dict_from_JSON("mean_MAD_dict_mean_x.json")
    data.pop("-%20Bayonet%20-%20Blue%20Steel%20(Minimal%20Wear)")
    data_list = []
    for key in data:
        item = data[key]
        data_list.append([item[0], item[1]])
    medians = [sublist[0] for sublist in data_list]
    MADs = [sublist[1] for sublist in data_list]
    m, c = np.polyfit(medians, MADs, 1)
    print(f"y = {m}x + {c}")
    vis.best_fit_plot(medians, MADs)
    R_sqr = calculate_r_squared(medians, MADs, m, c)
    print(f"R Squared = {R_sqr}")

    

def calculate_r_squared(x, y, m, c):
    func = np.vectorize(lambda x: x*m + c)
    y_pred = func(x)

    SS_res = sum(np.square(y_pred - y))
    SS_tot = sum(np.square(y - np.mean(y)))
    R_sqr = 1 - (SS_res/SS_tot)
    return R_sqr



def create_data():
    item_data_base_path = r"F:\programs\python\cs_montecarlo\data\price-data-2024-10-28"
    test_inv_raw_data = fn.loadJSON(
    r"F:\programs\python\cs_montecarlo\data\test-inventory-from-steamwebapi-2024-10-28.json" # filepath of list of inv items, from steam web api
        ).data
    test_inventory = InventoryData(test_inv_raw_data, item_data_base_path).raw_price_data_dict
    # rolling_MAD_dict, mean_MAD_dict = calculate_rolling_MADs(test_inventory, window=14)
    mean_MAD_dict = calculate_mean_MADs(test_inventory, window=14)
    exp_to_JSON(mean_MAD_dict)


def plot_trend(dict:dict):
    pass

def exp_to_JSON(dict:dict):
    with open("mean_MAD_dict_mean_x.json", "w") as f:
        json.dump(dict, f)

def get_dict_from_JSON(path):
    with open(path, "r") as f:
        return json.load(f)
    

def calculate_mean_MADs(inv:dict, window):
    mean_MAD_dict = {} # contains [mean_rolling_med, mean_rolling_mad]
    for item in inv:
        data = inv[item]
        prices = [sublist[1] for sublist in data]
        dates = [sublist[0] for sublist in data]
        s = pd.Series(prices, index=dates)
        rolling_med = s.rolling(window=window, center=True).median()
        mad = lambda x : np.median(np.abs(x - np.median(x)))
        rolling_mad = s.rolling(window=window, center=True).apply(mad, raw=True)
        rolling_mean = s.rolling(window=window, center=True).mean()
        mean_MAD_dict.update({item: [np.mean(rolling_mean), np.mean(rolling_mad)]})
    
    return mean_MAD_dict


def calculate_mean_MADs_log_price(inv:dict, window):
    mean_MAD_dict = {} # contains [mean_rolling_med, mean_rolling_mad]
    for item in inv:
        data = inv[item]
        prices = [sublist[1] for sublist in data]
        log_prices = np.log(prices)
        dates = [sublist[0] for sublist in data]
        s = pd.Series(log_prices, index=dates)
        rolling_med = s.rolling(window=window, center=True).median()
        mad = lambda x : np.median(np.abs(x - np.median(x)))
        rolling_mad = s.rolling(window=window, center=True).apply(mad, raw=True)
        rolling_mean = s.rolling(window=window, center=True).mean()
        mean_MAD_dict.update({item: [np.mean(rolling_mean), np.mean(rolling_mad)]})
    
    return mean_MAD_dict



def calculate_rolling_MADs(inv : dict, window):
    rolling_MAD_dict = {} # contains [[rolling_med, rolling_mad]]
    mean_MAD_dict = {} # contains [mean_rolling_med, mean_rolling_mad]
    for item in inv:
        data = inv[item]
        prices = [sublist[1] for sublist in data]
        dates = [sublist[0] for sublist in data]
        s = pd.Series(prices, index=dates)
        rolling_med = s.rolling(window=window, center=True).median()
        mad = lambda x : np.median(np.abs(x - np.median(x)))
        rolling_mad = s.rolling(window=window, center=True).apply(mad, raw=True)
        zipped_list = zip_data(rolling_med, rolling_mad)
        rolling_MAD_dict.update({item : zipped_list})

        mean_MAD_dict.update({item: [np.mean(rolling_med), np.mean(rolling_mad)]})
    
    return rolling_MAD_dict, mean_MAD_dict




def zip_data(a, b):
    zipped_data = []
    for i in range(len(a)):
        zipped_data.append([a[i], b[i]])
    return zipped_data          
          
          
     



if __name__ == "__main__":
      main()

