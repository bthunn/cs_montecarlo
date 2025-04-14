import re
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import json

class loadJSON:
    def __init__(self, path):
        self.data = self._get_data_from_json(path)

    def _get_data_from_json(self, path):
        with open(path, 'r', encoding="utf-8") as file:
            data = json.load(file)
            return data

# global function for replacing non-ascii characters
def replace_unprintable(text, placeholder='?'):
    # Encode the string to bytes, ignoring errors, then decode back to string
    return text.encode('ascii', 'replace').decode().replace('?', placeholder)

# global function for replacing characters that cant be included in file path names
def replace_invalid_chars_for_filepath(text, placeholder='-'):
    invalid_chars = r'[<>:"/\\|?*]'
    return re.sub(invalid_chars, placeholder, replace_unprintable(text))

def format_markethashnames(item_names): # converts markethashnames to format seen in dataframes
    return [name.replace(" ", "%20") for name in item_names]


def display_chart(prices, converted_dates):
    fig, ax = plt.subplots()
    ax.plot(converted_dates, prices)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.grid()
    plt.show()



if __name__ == "__main__":
      main()
