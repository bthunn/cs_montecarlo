import pandas as pd
import numpy as np
from matplotlib import pyplot as plt




class MonteCarlo:
    def __init__(self, df:pd.Series):
        returns = df.pct_change()
        mean_returns = returns.mean()
        cov_matrix = returns.cov()

        # weights = np.random.random(len(mean_returns))
        # weights /= np.sum(weights)

        # 1 item owned is equivalent to 1 share of each stock
        start_prices = df.loc[df.index[-1]]
        V_0 = np.sum(start_prices)
        weights = start_prices / V_0
        weights = pd.array()
        sims = self.sim(mean_returns, weights, cov_matrix, V_0)

        print(f"Initial portfolio value: {V_0}")
        plt.plot(sims)
        plt.ylabel('Portfolio Value (£)')
        plt.xlabel('Days')
        plt.title('Monte Carlo Simulation of portfolio')
        plt.show()
    





    def sim(self, mean_returns, weights, cov_matrix, V_0):
        n = len(weights)
        n_sims = 100
        T = 100 # days

        mean_matrix = np.full(shape=(T, n), fill_value=(mean_returns))
        # mean_matrix = mean_matrix.T

        portfolio_sims = np.full(shape=(T, n_sims), fill_value=0.0)

        
        for m in range(0, n_sims):
            Z = np.random.normal(size=(T, n))
            L = np.linalg.cholesky(cov_matrix)
            # R: [T x n]
            R = mean_matrix + np.matmul(Z, L.T)
            portfolio_sims[:,m] = np.cumprod(np.dot(weights, R.T)+1)*V_0
        
        return portfolio_sims


