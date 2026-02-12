import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

class QuantEngine:
    def __init__(self, ticker, data, output_dir="output"):
        self.ticker = ticker
        self.data = data
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def analyze(self):
        """
        Performs technical analysis and risk metrics calculation.
        """
        if self.data.empty:
            return {"error": "No data available"}

        # Flatten MultiIndex columns if present (common issue with yfinance)
        if isinstance(self.data.columns, pd.MultiIndex):
            self.data.columns = self.data.columns.get_level_values(0)

        # Calculate Log Returns
        self.data['Log Returns'] = np.log(self.data['Close'] / self.data['Close'].shift(1))

        # Risk Metrics
        annualized_volatility = self.data['Log Returns'].std() * np.sqrt(252)
        
        # Max Drawdown
        cumulative_returns = (1 + self.data['Log Returns']).cumprod()
        peak = cumulative_returns.expanding(min_periods=1).max()
        drawdown = (cumulative_returns / peak) - 1
        max_drawdown = drawdown.min()

        # Momentum Metrics
        # RSI (14)
        delta = self.data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        self.data['RSI_14'] = 100 - (100 / (1 + rs))
        current_rsi = self.data['RSI_14'].iloc[-1]

        # Bollinger Bands (20, 2)
        sma_20 = self.data['Close'].rolling(window=20).mean()
        std_20 = self.data['Close'].rolling(window=20).std()
        self.data['BBU_20_2.0'] = sma_20 + (std_20 * 2)
        self.data['BBL_20_2.0'] = sma_20 - (std_20 * 2)

        # --- Advanced Analytics ---
        # 1. Sharpe Ratio (Risk Free Rate = 4%)
        risk_free_daily = 0.04 / 252
        excess_returns = self.data['Log Returns'] - risk_free_daily
        sharpe_ratio = (excess_returns.mean() / self.data['Log Returns'].std()) * np.sqrt(252)

        # 2. Value at Risk (VaR 95%)
        var_95 = np.percentile(self.data['Log Returns'].dropna(), 5)

        # 3. Beta (vs SPY)
        beta = self._calculate_beta(self.data['Log Returns'])

        # 4. Linear Regression (Trend)
        y = self.data['Close'].values
        x = np.arange(len(y))
        slope, intercept = np.polyfit(x, y, 1)
        self.data['Regression_Line'] = slope * x + intercept
        r_squared = 1 - (np.sum((y - self.data['Regression_Line'])**2) / np.sum((y - np.mean(y))**2))
        
        # Plotting
        plot_path = self._plot_results()

        return {
            "Annualized Volatility": annualized_volatility,
            "Max Drawdown": max_drawdown,
            "RSI (14)": current_rsi,
            "Last Price": self.data['Close'].iloc[-1],
            "Sharpe Ratio": sharpe_ratio,
            "VaR (95%)": var_95,
            "Beta": beta,
            "Trend Slope": slope,
            "R-Squared": r_squared,
            "Plot Path": plot_path
        }

    def _calculate_beta(self, stock_returns):
        try:
            # Helper to fetch SPY data locally with persistence
            from utils.data_loader import get_market_data
            import os
            spy_data = get_market_data("SPY", period="5y", save_dir=os.path.join("data", "raw"))
            if isinstance(spy_data.columns, pd.MultiIndex):
                spy_data.columns = spy_data.columns.get_level_values(0)
            
            spy_returns = np.log(spy_data['Close'] / spy_data['Close'].shift(1))
            
            # Align data content
            combined = pd.concat([stock_returns, spy_returns], axis=1).dropna()
            combined.columns = ['Stock', 'Market']
            
            covariance = combined.cov().iloc[0, 1]
            market_variance = combined['Market'].var()
            
            return covariance / market_variance
        except Exception as e:
            print(f"Beta calc error: {e}")
            return 1.0 # Default to 1 if fails

    def _plot_results(self):
        plt.figure(figsize=(14, 7))
        plt.plot(self.data.index, self.data['Close'], label='Close Price', color='blue')
        
        # Check for BB columns and plot
        bb_upper = f"BBU_20_2.0"
        bb_lower = f"BBL_20_2.0"
        
        if bb_upper in self.data.columns and bb_lower in self.data.columns:
            plt.plot(self.data.index, self.data[bb_upper], label='Upper BB', linestyle='--', color='green', alpha=0.6)
            plt.plot(self.data.index, self.data[bb_lower], label='Lower BB', linestyle='--', color='red', alpha=0.6)
            plt.fill_between(self.data.index, self.data[bb_upper], self.data[bb_lower], color='gray', alpha=0.1)

        # Plot Regression Line
        if 'Regression_Line' in self.data.columns:
             plt.plot(self.data.index, self.data['Regression_Line'], label='Trend (LinReg)', color='orange', linestyle='-', linewidth=2)

        plt.title(f"Technical Analysis for {self.ticker}")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend()
        plt.grid(True)
        
        output_path = os.path.join(self.output_dir, f"{self.ticker}_analysis.png")
        plt.savefig(output_path)
        plt.close()
        return output_path
