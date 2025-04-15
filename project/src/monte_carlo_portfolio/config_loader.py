import configparser
import os

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.cfg'))

API_INV_BASE_URL = config.get("API", "inventory_base_url")
API_ITEM_PRICE_HISTORY_BASE_URL = config.get("API", "item_price_history_base_url")