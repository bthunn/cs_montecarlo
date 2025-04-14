import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def custom_month_formatter(x, pos):
    date = mdates.num2date(x)
    # date = x
    if date.month == 1:
        return date.strftime('%Y')
    else:
        return date.strftime('')


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


def outlier_plot(price_series:pd.Series, outliers):
    fig, ax = plt.subplots()

    # Plot the price data
    ax.plot(price_series, label='Price Data', color='blue', marker="x")

    # Plot the outlier points in red
    ax.scatter(outliers.index, outliers.values, color='red', label='Outliers')

    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(plt.FuncFormatter(custom_month_formatter))

    # Customize plot
    plt.title('Price Data with Outliers')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()

    # Show the plot
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()