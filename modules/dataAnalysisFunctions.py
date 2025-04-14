import numpy as np
import pandas as pd
from modules import visuals as vis

def detect_outliers_rolling_med(s, window=7, threshold=10): # performance: good
    # rolling_mean = s.rolling(window=window, center=True).mean()
    # rolling_std = s.rolling(window=window, center=True).std()
    # z = (s - rolling_mean) / rolling_std

    rolling_med = s.rolling(window=window, center=False, min_periods=3).median()
    z = (s - rolling_med)/(0.01*rolling_med)
    print(z.to_list())
    return z.abs() > threshold


def detect_outliers_rolling_iqr(s, window=7, tolerance=1.5): # performance: poor. Data too scuffed to normalize to mean
    rolling_q1 = s.rolling(window=window, center=True).quantile(0.25)
    rolling_q3 = s.rolling(window=window, center=True).quantile(0.75)

    rolling_iqr = rolling_q3 - rolling_q1
    rolling_lower_bound = rolling_q1 - (tolerance * rolling_iqr)
    rolling_upper_bound = rolling_q3 + (tolerance * rolling_iqr)
    outlier_mask = (s < rolling_lower_bound) | (s > rolling_upper_bound)
    return outlier_mask

def detect_outliers_modified_z(s, window=7, threshold = 10): # performance: meh. Better than mean but same problem with normalization to local deviations
    rolling_med = s.rolling(window=window, center=True).median()
    mad = lambda x : np.median(np.abs(x - np.median(x)))
    rolling_mad = s.rolling(window=window, center=True).apply(mad, raw=True)
    rolling_z = (s - rolling_med) / rolling_mad
    return rolling_z.abs() > threshold


def detect_outliers_modified_z_modified(s, window, threshold, eps, mad_cap): # best. Adds constant offset to the MAD, reducing the normalization problem.
    cent = False
    minp = 3
    rolling_med = s.rolling(window=window, center=cent, min_periods=minp).median()
    mad = lambda x : np.median(np.abs(x - np.median(x)))
    rolling_mad = s.rolling(window=window, center=cent, min_periods=minp).apply(mad, raw=True)
    mad_cap = mad_cap * rolling_med
    capped_mad = np.minimum(rolling_mad, mad_cap)
    rolling_z = (s - rolling_med) / (capped_mad + eps)
    # threshold = np.percentile(rolling_z.abs(), 99) # threshold defined as 99th percentile z score (1% of total data removed)
    return rolling_z.abs() > threshold

def detect_outliers_modified_z_modified_left(s, window, threshold, eps, mad_cap): # best. Adds constant offset to the MAD, reducing the normalization problem.
    cent = False
    minp = 3
    rolling_med = s[::-1].rolling(window=window, center=cent, min_periods=minp).median()[::-1]
    mad = lambda x : np.median(np.abs(x - np.median(x)))
    rolling_mad = s[::-1].rolling(window=window, center=cent, min_periods=minp).apply(mad, raw=True)[::-1]
    # mad_cap = mad_cap + 0.1 * np.mean(rolling_med)
    capped_mad = np.maximum(rolling_mad, mad_cap)
    rolling_z = (s - rolling_med) / (capped_mad + eps)
    # threshold = np.percentile(rolling_z.abs(), 99) # threshold defined as 99th percentile z score (1% of total data removed)
    return rolling_z.abs() > threshold


def detect_isolated(s:pd.Series, tolerance):
    mask = s.notna()
    cleaned = s.copy()
    isolated_dict = {}

    rolling_sum  = s.rolling(window=tolerance, center=True, min_periods=4).sum()

    s_dates = s.index.tolist()
    s_prices = s.array.tolist()
    # s_list = []
    # for i in range(len(s_dates)):
    #     s_list.append([s_dates[i], s_prices[i]])


    for i in range(len(s_dates)):
        if not np.isnan(s_prices[i]):
            left = max(0, i - tolerance)
            right = min(len(s_dates), i + tolerance)
                   



    for i in range(len(s)):
        if not pd.isna(s.iloc[i]):
            left = max(0, i - tolerance)
            right = min(len(s), i + tolerance)
            window = mask.iloc[left:right]
            if window.sum() <= 1:
                # cleaned.iloc[i] = np.nan
                isolated_dict.update({s.iloc[i].index, s.iloc[i].value})
    return isolated_dict




def calc_rolling_mad(s, window):
    rolling_med = s.rolling(window=window, center=True).median()
    mad = lambda x : np.median(np.abs(x - np.median(x)))
    rolling_mad = s.rolling(window=window, center=True).apply(mad, raw=True)
    return rolling_mad



