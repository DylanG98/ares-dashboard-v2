import yfinance as yf
import pandas as pd

class Researcher:
    def __init__(self):
        pass

    def get_market_intel(self, ticker: str) -> str:
        """
        Fetches fundamental data (Balance Sheet, Cash Flow) from yfinance and summarizes findings.
        """
        try:
        import time
        stock = yf.Ticker(ticker)
        
        # Robust Fetching with retries
        info = {}
        bs = pd.DataFrame()
        cf = pd.DataFrame()
        
        for attempt in range(3):
            try:
                if not info: info = stock.info
                if bs.empty: bs = stock.balance_sheet
                if cf.empty: cf = stock.cashflow
                
                # If we got at least something, break
                if info and (not bs.empty or not cf.empty):
                    break
            except Exception as e:
                print(f"[WARN] yfinance attempt {attempt+1} fail: {e}")
            
            if attempt < 2:
                time.sleep(1.5) # Wait before retry

        report = f"### Fundamental Analysis for {ticker}\n\n"
            
            # Company Profile
            sector = info.get('sector', 'N/A')
            industry = info.get('industry', 'N/A')
            market_cap = info.get('marketCap', 0)
            
            # Fallback for Market Cap (Fast Info)
            if market_cap == 0:
                try:
                    market_cap = stock.fast_info['market_cap']
                except:
                    pass

            report += f"**Sector**: {sector} | **Industry**: {industry}\n"
            report += f"**Market Cap**: ${market_cap:,.0f}\n\n"

            # Prepare structured data for Synthesizer
            data = {
                "Market Cap": market_cap,
                "Total Debt": 0,
                "Cash": 0,
                "Free Cash Flow": 0
            }

            # Balance Sheet Analysis
            report += "**Balance Sheet Highlights (Latest):**\n"
            
            # Helper to safely get latest value from DF or Info
            def get_financial_metric(dfs, keys, info_keys, default=0):
                # 1. Try DataFrames (e.g. Balance Sheet, Cash Flow)
                for df in dfs:
                    if not df.empty:
                        # Ensure columns are dates and sorted recent first
                        try:
                            df_sorted = df.T.sort_index(ascending=False).T
                            latest_col = df_sorted.iloc[:, 0] # Series of latest data
                            
                            for key in keys:
                                if key in latest_col.index:
                                    val = latest_col[key]
                                    if pd.notna(val) and val != 0:
                                        return val
                        except Exception:
                            pass # Fallback if sorting fails

                # 2. Try Info Dict
                for k in info_keys:
                    val = info.get(k, 0)
                    if val and val != 0:
                        return val
                        
                return default

            # Extraction
            total_debt = get_financial_metric(
                [bs], 
                ['Total Debt', 'Long Term Debt'], 
                ['totalDebt', 'longTermDebt']
            )
            
            total_cash = get_financial_metric(
                [bs], 
                ['Cash And Cash Equivalents', 'Cash Cash Equivalents And Short Term Investments'], 
                ['totalCash', 'cash']
            )
            
            fcf = get_financial_metric(
                [cf], 
                ['Free Cash Flow', 'Free Cashflow'], 
                ['freeCashflow']
            )
            
            op_cash = get_financial_metric(
                [cf], 
                ['Operating Cash Flow', 'Total Cash From Operating Activities'], 
                ['operatingCashflow']
            )

            # Assign to Data
            data["Total Debt"] = total_debt
            data["Cash"] = total_cash
            data["Free Cash Flow"] = fcf
            
            print(f"[RESEARCHER DEBUG] {ticker} -> MC: {market_cap}, Debt: {total_debt}, Cash: {total_cash}, FCF: {fcf}")
            
            # Formatting Report
            if total_debt or total_cash:
                report += f"- **Total Debt**: ${total_debt:,.0f}\n"
                report += f"- **Cash & Equivalents**: ${total_cash:,.0f}\n"
                if total_debt > 0 and total_cash > 0:
                    net_cash = total_cash - total_debt
                    report += f"- **Net Cash Position**: ${net_cash:,.0f}\n"
            else:
                report += "*Balance Sheet data unavailable.*\n"
            
            report += "\n**Cash Flow Highlights (Latest):**\n"
            if fcf or op_cash:
                report += f"- **Free Cash Flow**: ${fcf:,.0f}\n"
                report += f"- **Operating Cash Flow**: ${op_cash:,.0f}\n"
            else:
                 report += "\n*Cash Flow data unavailable.*\n"

            return {
                "report": report,
                "data": data
            }

        except Exception as e:
            return {
                "report": f"Error fetching fundamental data: {str(e)}",
                "data": {}
            }

    def get_sentiment(self, ticker: str) -> dict:
        """
        Analyzes news headlines to determine market sentiment.
        Returns: {'polarity': float, 'sentiment': str, 'headlines': list}
        """
        try:
            from textblob import TextBlob
            stock = yf.Ticker(ticker)
            news = stock.news
            
            if not news:
                return {"polarity": 0, "sentiment": "Neutral", "headlines": []}

            titles = []
            for n in news:
                # Handle different yfinance news structures
                if 'content' in n and 'title' in n['content']:
                    titles.append(n['content']['title'])
                elif 'title' in n:
                    titles.append(n['title'])
            
            scores = []
            
            for title in titles:
                blob = TextBlob(title)
                scores.append(blob.sentiment.polarity)

            avg_polarity = sum(scores) / len(scores) if scores else 0
            
            if avg_polarity > 0.05:
                sentiment = "Bullish"
            elif avg_polarity < -0.05:
                sentiment = "Bearish"
            else:
                sentiment = "Neutral"
                
            return {
                "polarity": round(avg_polarity, 2),
                "sentiment": sentiment,
                "headlines": titles[:3] # Return top 3 for context
            }
            
        except Exception as e:
            return {"polarity": 0, "sentiment": "Error", "error": str(e)}
