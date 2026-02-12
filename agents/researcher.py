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
            stock = yf.Ticker(ticker)
            bs = stock.balance_sheet
            cf = stock.cashflow
            info = stock.info

            report = f"### Fundamental Analysis for {ticker}\n\n"
            
            # Company Profile
            sector = info.get('sector', 'N/A')
            industry = info.get('industry', 'N/A')
            market_cap = info.get('marketCap', 0)
            
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
            if not bs.empty:
                report += "**Balance Sheet Highlights (Latest):**\n"
                latest_date = bs.columns[0]
                total_debt = bs.loc['Total Debt', latest_date] if 'Total Debt' in bs.index else 0
                total_cash = bs.loc['Cash And Cash Equivalents', latest_date] if 'Cash And Cash Equivalents' in bs.index else 0
                
                data["Total Debt"] = total_debt
                data["Cash"] = total_cash
                
                report += f"- **Total Debt**: ${total_debt:,.0f}\n"
                report += f"- **Cash & Equivalents**: ${total_cash:,.0f}\n"
            else:
                report += "*Balance Sheet data unavailable.*\n"
            
            # Cash Flow Analysis
            if not cf.empty:
                report += "\n**Cash Flow Highlights (Latest):**\n"
                latest_cf_date = cf.columns[0]
                fcf = cf.loc['Free Cash Flow', latest_cf_date] if 'Free Cash Flow' in cf.index else 0
                op_cash = cf.loc['Operating Cash Flow', latest_cf_date] if 'Operating Cash Flow' in cf.index else 0
                
                data["Free Cash Flow"] = fcf
                
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
