import os

import numpy as np
import pandas as pd
from datetime import date, datetime, timedelta
from abc import ABC, abstractmethod

import utils as ut

# 
class OutlierParams(ABC):
    @property
    @abstractmethod
    def window(self) -> int:
        pass

    @abstractmethod
    def get_params_as_dict(self) -> dict:
        pass


class OutlierStrategy(ABC):
    @abstractmethod
    def __init__(self, raw_series:pd.Series, params:OutlierParams):
        pass

    @abstractmethod
    def get_outliers(self) -> pd.Series:
        pass

# returns an empty series
class Raw(OutlierStrategy):
    def __init__(self, raw_series:pd.Series=None, params:OutlierParams=None):
        pass

    def get_outliers(self):
        return pd.Series(dtype=float)

# Modified z-score with added constant to decrease outlier sensitivity when MAD is low
# (reduces false positives)
# runs both ways over series to deal with edges and increase reliability
class ModifiedZParams(OutlierParams):
    def __init__(self, window:int=7, threshold=3.5, eps=1, mad_cap=np.inf):
        self._window = window
        self.threshold = threshold
        self.eps = eps
        self.mad_cap = mad_cap

    @property
    def window(self): return self._window

    def get_params_as_tuple(self):
        d = self.get_params_as_dict()
        return (d['window'], d['threshold'], d['eps'], d['mad_cap'])
    
    def get_params_as_dict(self):
        return {'window':self.window, 'threshold':self.threshold, 'eps':self.eps,
                'mad_cap':self.mad_cap}
        

class ModifiedZ(OutlierStrategy):
    def __init__(self, raw_series:pd.Series, params:ModifiedZParams):
        window = params.window
        threshold = params.threshold
        eps = params.eps
        mad_cap = params.mad_cap
        self.outliers = self._detect_outliers(raw_series, window, threshold, eps, mad_cap)

    def get_outliers(self):
        return self.outliers

    def _detect_outliers(self, series:pd.Series, window, threshold, eps, mad_cap):
        mask_forward = self._get_mask_with_modified_z(
            series, window, threshold, eps, mad_cap)
        mask_reverse = self._get_mask_with_modified_z(
            series[::-1], window, threshold, eps, mad_cap)
        
        outliers_forward = series[mask_forward]
        outliers_reverse = series[::-1][mask_reverse]
        outliers_reverse.sort_index(inplace=True)

        # Combine masks:
        outliers = outliers_forward
        outliers.update(outliers_reverse)

        # outlier_mask = [f or r for f, r in zip(mask_forward, mask_reverse)]
        # outliers = series[outlier_mask]
        return outliers

    def _get_mask_with_modified_z(self, series, window, threshold, eps, mad_cap):
        cent = False
        minp = 3
        rolling_med = series.rolling(window=window, center=cent, min_periods=minp).median()
        mad = lambda x : np.median(np.abs(x - np.median(x)))
        rolling_mad = series.rolling(window=window, center=cent, min_periods=minp).apply(mad, raw=True)
        mad_cap = mad_cap * rolling_med
        # capped_mad = np.minimum(rolling_mad, mad_cap)
        capped_mad = rolling_mad
        rolling_z = (series - rolling_med) / (capped_mad + eps)
        # threshold = np.percentile(rolling_z.abs(), 99) # threshold defined as 99th percentile z score (1% of total data removed)
        return rolling_z.abs() > threshold

