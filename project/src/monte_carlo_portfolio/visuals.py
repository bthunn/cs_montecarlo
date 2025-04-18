import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
from matplotlib.ticker import MultipleLocator
from matplotlib.ticker import AutoMinorLocator

# === Utils ===
def custom_month_formatter(x, pos):
    date = mdates.num2date(x)
    # date = x
    if date.month == 1:
        return date.strftime('%Y')
    else:
        return date.strftime('')

def pounds(x, pos):
    return f'£{x:,.0f}'
# ===== ===== ===== ===== ===== 

def basic_plot(x,y):
    plt.plot(x, y, marker="x", markersize="7", linestyle="None")
    plt.show()
    

def plot_series(s:pd.Series):
    plot = s.plot(marker="x", markersize="7", linestyle="None")
    # plt.show()


def best_fit_plot(x, y):
    plt.plot(x, y, marker="x", markersize="5", linestyle="None")
    m, c = np.polyfit(x, y, 1)
    func = np.vectorize(lambda x: x*m + c)
    y_pred = func(x)
    plt.plot(x, y_pred, linewidth = "2", color="r")
    plt.show()


def post_processor_plot(price_series:pd.Series, outliers:pd.Series, isolated:pd.Series, interped:pd.Series):
    fig, ax = plt.subplots()

    # Plot the price data
    ax.plot(price_series, label='Price Data', color='black', marker="None", zorder=0, markersize='5', linewidth='1')

    # Plot the outlier points in red
    ax.scatter(outliers.index, outliers.values, color='red', label='Outliers', s=10, zorder=10)

    # Plot isolated points in green
    ax.plot(isolated.index, isolated.values, color='green', label='Isolated points', markersize='6', linestyle="None",
        marker='s', markerfacecolor='None', zorder=5)

    # Plot interpolated/filled values in purple
    ax.plot(interped.index, interped.values, color='purple', label='Forward-filled values', markersize='6', linestyle="None",
            marker='s', markerfacecolor='None', zorder=5)

    ax.minorticks_on()
    ax.grid(visible=True, which='major', axis='both', linewidth=0.8)
    ax.grid(visible=True, which='minor', axis='both', linewidth=0.4, linestyle='--')
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.xaxis.set_minor_locator(AutoMinorLocator(12, ))
    ax.yaxis.set_major_formatter(FuncFormatter(pounds))
    ax.set_ylim((0, None))

    # Customize plot
    plt.title('Price Data with Outliers and Forward-Filled Prices', fontsize=20)
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend(loc='upper center', fontsize=16)

    # Show the plot
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()