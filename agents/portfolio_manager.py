import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.optimize as sco
from utils.data_loader import get_market_data
from utils.logger import setup_logger
import os

logger = setup_logger("PORTFOLIO", "logs")

class PortfolioManager:
    def __init__(self, tickers, period="2y"):
        self.tickers = tickers
        self.period = period
        self.data = pd.DataFrame()
        self.output_dir = "reports/portfolio"
        os.makedirs(self.output_dir, exist_ok=True)

    def load_data(self):
        """Fetches and aligns historical data for all tickers."""
        logger.info(f"Loading data for portfolio: {self.tickers}")
        df_list = []
        
        for ticker in self.tickers:
            df = get_market_data(ticker, period=self.period, save_dir="data/portfolio")
            if not df.empty:
                # Keep only Close price and rename col to Ticker
                df_close = df[['Close']].rename(columns={'Close': ticker})
                df_list.append(df_close)
            else:
                logger.warning(f"Could not load data for {ticker}")

        if df_list:
            self.data = pd.concat(df_list, axis=1).dropna()
            logger.info(f"Data aligned. Shape: {self.data.shape}")
        else:
            logger.error("No data loaded for portfolio.")

    def plot_correlation_matrix(self):
        """Generates and saves a correlation heatmap."""
        if self.data.empty: return
        
        corr_matrix = self.data.pct_change().corr()
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
        plt.title(f"Correlation Matrix ({self.period})")
        
        plot_path = os.path.join(self.output_dir, "correlation_matrix.png")
        plt.savefig(plot_path)
        plt.close()
        logger.info(f"Correlation matrix saved to {plot_path}")
        return plot_path

    def optimize_efficient_frontier(self, risk_free_rate=0.04):
        """
        Calculates the Max Sharpe Ratio portfolio using Scipy Optimize.
        """
        if self.data.empty: return None

        returns = self.data.pct_change()
        mean_returns = returns.mean() * 252
        cov_matrix = returns.cov() * 252
        num_assets = len(mean_returns)

        def portfolio_performance(weights):
            returns = np.sum(mean_returns * weights)
            std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            return returns, std

        def neg_sharpe_ratio(weights):
            p_ret, p_std = portfolio_performance(weights)
            return -(p_ret - risk_free_rate) / p_std

        # Constraints: Weights sum to 1
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        # Bounds: 0 <= weight <= 1 for each asset
        bounds = tuple((0, 1) for _ in range(num_assets))
        # Initial Guess: Equal weights
        init_guess = num_assets * [1. / num_assets,]

        result = sco.minimize(neg_sharpe_ratio, init_guess, method='SLSQP', bounds=bounds, constraints=constraints)
        
        best_weights = result.x
        best_ret, best_std = portfolio_performance(best_weights)
        best_sharpe = (best_ret - risk_free_rate) / best_std

        allocation = {self.data.columns[i]: round(best_weights[i], 4) for i in range(num_assets)}
        
        logger.info("Optimization Complete.")
        logger.info(f"Max Sharpe Ratio: {best_sharpe:.2f}")
        logger.info(f"Allocation: {allocation}")
        
        return {
            "allocation": allocation,
            "return": best_ret,
            "volatility": best_std,
            "sharpe": best_sharpe,
            "type": "Max Sharpe"
        }

    def optimize_min_volatility(self):
        """
        Calculates the Minimum Volatility portfolio (Conservative).
        """
        if self.data.empty: return None

        returns = self.data.pct_change()
        mean_returns = returns.mean() * 252
        cov_matrix = returns.cov() * 252
        num_assets = len(mean_returns)

        def portfolio_volatility(weights):
            return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

        def portfolio_return(weights):
             return np.sum(mean_returns * weights)

        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) for _ in range(num_assets))
        init_guess = num_assets * [1. / num_assets,]

        result = sco.minimize(portfolio_volatility, init_guess, method='SLSQP', bounds=bounds, constraints=constraints)
        
        weights = result.x
        ret = portfolio_return(weights)
        std = result.fun
        sharpe = (ret - 0.04) / std

        allocation = {self.data.columns[i]: round(weights[i], 4) for i in range(num_assets)}
        
        return {
            "allocation": allocation,
            "return": ret,
            "volatility": std,
            "sharpe": sharpe,
            "type": "Min Volatility"
        }

    def optimize_target_risk(self, target_volatility=0.30):
        """
        Maximizes return for a specific target volatility (Custom Risk).
        """
        if self.data.empty: return None

        returns = self.data.pct_change()
        mean_returns = returns.mean() * 252
        cov_matrix = returns.cov() * 252
        num_assets = len(mean_returns)

        def portfolio_return(weights):
            return -np.sum(mean_returns * weights) # Minimize negative return = Maximize return

        def portfolio_volatility(weights):
             return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

        # Constraints: 
        # 1. Weights sum to 1
        # 2. Volatility <= target_volatility
        constraints = (
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
            {'type': 'eq', 'fun': lambda x: portfolio_volatility(x) - target_volatility} 
        )
        bounds = tuple((0, 1) for _ in range(num_assets))
        init_guess = num_assets * [1. / num_assets,]

        # We assume such a portfolio exists. If target is too low, optimization might fail or return min_vol.
        result = sco.minimize(portfolio_return, init_guess, method='SLSQP', bounds=bounds, constraints=constraints)
        
        weights = result.x
        ret = -result.fun
        std = portfolio_volatility(weights)
        sharpe = (ret - 0.04) / std
        
        allocation = {self.data.columns[i]: round(weights[i], 4) for i in range(num_assets)}
        
        return {
            "allocation": allocation,
            "return": ret,
            "volatility": std,
            "sharpe": sharpe,
            "type": f"Target Vol ({target_volatility*100}%)"
        }
