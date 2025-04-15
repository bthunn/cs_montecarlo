from  config_loader import API_INV_BASE_URL

from abc import ABC, abstractmethod
import json
from typing import Any

import utils as ut


# === Strategy Class (interface) ===
class ItemLoaderStrategy(ABC):
    @abstractmethod
    def get_list(self) -> list[Any]:
        pass

    def load_raw_json(self, path):
        return ut.load_json(path)
    
    def _flag_marketable(self, raw):
        # returns boolean mask where marketable items are True
        return [item['marketable'] for item in raw]
    
    def filter_marketable(self, item_list, raw):
        mask = self._flag_marketable(raw)
        return [item for item, flag in zip(item_list, mask) if flag]


class LoadFromListJSON(ItemLoaderStrategy):
    def __init__(self, path:str, marketable:bool=False):
        self.path = path

    def get_list(self) -> list[Any]:
        pass

        
class LoadFromInvJSON(ItemLoaderStrategy):
    def __init__(self, path:str, marketable:bool=True):
        self.path = path
        self.marketable = marketable

    def get_list(self) -> list[Any]:
        raw = self.load_raw_json(self.path)
        item_list = self._get_list_of_market_hash_names(raw)
        item_list_formatted = [ut.format_markethashname(item) for item in item_list] # standardizes format of item names
        if self.marketable == False:
            return item_list_formatted
        else:
            return self.filter_marketable(item_list_formatted, raw)

    def _get_list_of_market_hash_names(self, raw):
        # extract markethashname from API inventory JSON dump
        return [item['markethashname'] for item in raw]
    
    

class LoadFromInvID(ItemLoaderStrategy):
    def __init__(self, inv_id:str, marketable:bool=False):
        self.base_url = API_INV_BASE_URL
        self.inv_id = inv_id

    def get_list(self) -> list[Any]:
        pass