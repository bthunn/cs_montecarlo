import os

import numpy as np
import pandas as pd
from datetime import date, datetime, timedelta
from abc import ABC, abstractmethod

import utils as ut

class ProcessorStrategy(ABC):
    @abstractmethod
    def get_series(self) -> pd.Series:
        pass

    def _remove_date_gaps(self, raw_prices):
        # basic processing; miniuim requirement for price cleaning
        pass