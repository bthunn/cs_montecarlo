import os
import sys

import numpy as np
import pandas as pd
from datetime import date, datetime, timedelta
from abc import ABC, abstractmethod

import utils as ut

class InterpStrategy(ABC):
    @abstractmethod
    def __init__(self, series:pd.Series):
        pass

    @abstractmethod
    def get_interpolated_series(self):
        pass

    # returns only data that has been added
    @abstractmethod
    def get_interpolated_data(self):
        pass

    def _find_missing_data(self, series):
        return series[series.isna()]


class Ffill(InterpStrategy):
    def __init__(self, series:pd.Series):
        self.series_filled = series.ffill()
        filled_dates = self._find_missing_data(series).index
        self.filled = self.series_filled[filled_dates]

    def get_interpolated_series(self):
        return self.series_filled
    
    def get_interpolated_data(self):
        return self.filled


