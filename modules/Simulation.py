from modules.InventoryConstructor import InventoryData
import pandas as pd

class Simulation:
    def __init__(self, data: pd.DataFrame): # passed inventory data as obj
            self.dataFrame = data
            self.startDate, self.endDate = self.get_date_range()

    def sim(self):
         pass
    
    def get_date_range(self): # also checks start dates are equal
        #  for row in self.dataFrame:
        pass
              
         
         

            
    def step1(self):
        data = self.dataFrame
        returns = data.pct_change()
        meanReturns = returns.mean()
        covMatrix = returns.cov()
        return meanReturns, covMatrix
    
