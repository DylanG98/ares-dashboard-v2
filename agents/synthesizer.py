import google.generativeai as genai
import logging
from utils.config_loader import load_config

logger = logging.getLogger("Synthesizer")

class Synthesizer:
    def __init__(self):
        self.config = load_config()
        self.api_key = self.config.get("gemini", {}).get("api_key")
        self.model_name = self.config.get("gemini", {}).get("model", "gemini-1.5-flash")
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        else:
            self.model = None
            logger.warning("Gemini API Key not found. Falling back to rule-based logic.")

    def _rule_based_analysis(self, ticker, quant_data, researcher_data):
        """Fallback logic if AI fails."""
        rsi = quant_data.get("RSI (14)", 50)
        score = 0
        signals = []
        
        if rsi < 30:
            signals.append("🟢 Bullish: Oversold (RSI < 30)")
            score += 1
        elif rsi > 70:
            signals.append("🔴 Bearish: Overbought (RSI > 70)")
            score -= 1
            
        fcf = researcher_data.get("Free Cash Flow", 0)
        if fcf > 0:
            signals.append("🟢 Bullish: Positive Free Cash Flow")
            score += 1
            
        verdict = "BUY" if score > 0 else "SELL" if score < 0 else "HOLD"
        
        return f"""
# A.R.E.S. Fallback Report: {ticker}
## ⚖️ Verdict: {verdict}
**Note**: AI generation failed. Using basic rules.

### Signals
{chr(10).join(['- ' + s for s in signals])}
"""

    def synthesize(self, ticker: str, quant_data: dict, researcher_data: dict) -> str:
        """
        Generates a professional financial report using Gemini AI.
        """
        if not self.model:
            return self._rule_based_analysis(ticker, quant_data, researcher_data)
            
        # Construct the Prompt
        prompt = f"""
Act as a Senior Wall Street Analyst. Analyze the following data for {ticker} and write a professional, concise executive summary.

### Technical Data (Quant Agent)
- RSI (14): {quant_data.get('RSI (14)', 'N/A')}
- Volatility (Ann): {quant_data.get('Annualized Volatility', 'N/A')}
- Beta: {quant_data.get('Beta', 'N/A')}
- Sharpe Ratio: {quant_data.get('Sharpe Ratio', 'N/A')}

### Fundamental Data (Researcher Agent)
- Free Cash Flow: {researcher_data.get('Free Cash Flow', 'N/A')}
- Total Debt: {researcher_data.get('Total Debt', 'N/A')}
- Cash Position: {researcher_data.get('Cash', 'N/A')}
- Market Cap: {researcher_data.get('Market Cap', 'N/A')}

### Market Sentiment (NLP Agent)
- Sentiment: {researcher_data.get('sentiment', {}).get('sentiment', 'Neutral')}
- Polarity Score: {researcher_data.get('sentiment', {}).get('polarity', 0)}

### Instructions
1. **Verdict**: Start with a clear BUY, SELL, or HOLD recommendation based on the data.
2. **Analysis**: Explain WHY, citing specific metrics (e.g., "RSI indicates conditions...").
3. **Tone**: Professional, objective, and institutional. No emojis, just facts.
4. **Format**: Use Markdown. Keep it under 200 words.
"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini AI failed: {e}")
            return self._rule_based_analysis(ticker, quant_data, researcher_data)
