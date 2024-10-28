import re
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# global function for replacing non-ascii characters
def replace_unprintable(text, placeholder='?'):
    # Encode the string to bytes, ignoring errors, then decode back to string
    return text.encode('ascii', 'replace').decode().replace('?', placeholder)

# global function for replacing characters that cant be included in file path names
def replace_invalid_chars_for_filepath(text, placeholder='-'):
    invalid_chars = r'[<>:"/\\|?*]'
    return re.sub(invalid_chars, placeholder, replace_unprintable(text))

def display_chart(prices, converted_dates):
    fig, ax = plt.subplots()
    ax.plot(converted_dates, prices)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.grid()
    plt.show()