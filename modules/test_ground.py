import pandas as pd
import numpy as np
from datetime import date
import datetime

dt_range = pd.date_range(start=date(2013, 8, 1), end=date.today(), periods=datetime.timedelta(days=1))
date_range = dt_range.date()
print(date_range)