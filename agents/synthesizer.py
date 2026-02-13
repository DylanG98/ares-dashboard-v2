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

    def get_signal(self, quant_data: dict, researcher_data: dict) -> dict:
        """
        Calculates the score and verdict based on input data.
        Returns a dict with 'score', 'verdict', 'color', and 'signals' list.
        Used by Telegram Bot /price command and fallback logic.
        """
        rsi = quant_data.get("RSI (14)", 50)
        
        total_debt = researcher_data.get("Total Debt", 0)
        cash = researcher_data.get("Cash", 0)
        fcf = researcher_data.get("Free Cash Flow", 0)
        
        signals = []
        score = 0 # -2.5 to +2.5
        
        # Technical Logic
        if rsi < 30:
            signals.append("🟢 **Bullish**: Stock is Oversold (RSI < 30).")
            score += 1
        elif rsi > 70:
            signals.append("🔴 **Bearish**: Stock is Overbought (RSI > 70).")
            score -= 1
        else:
            signals.append("⚪ **Neutral**: RSI is in normal range.")

        # Fundamental Logic
        if fcf > 0:
            signals.append("🟢 **Bullish**: Positive Free Cash Flow.")
            score += 1
        else:
            signals.append("🔴 **Bearish**: Negative Free Cash Flow.")
            score -= 1
            
        if cash > total_debt:
            signals.append("🟢 **Bullish**: Cash reserves exceed Total Debt.")
            score += 0.5
        else:
            signals.append("🟠 **Caution**: Total Debt exceeds Cash.")
            score -= 0.5

        # Sentiment Logic
        sentiment = researcher_data.get("sentiment", {}).get("sentiment", "Neutral")
        polarity = researcher_data.get("sentiment", {}).get("polarity", 0)
        
        if sentiment == "Bullish":
            signals.append(f"🟢 **Sentiment**: Optimistic (Score: {polarity}).")
            score += 0.5
        elif sentiment == "Bearish":
            signals.append(f"🔴 **Sentiment**: Pessimistic (Score: {polarity}).")
            score -= 0.5

        # Final Verdict
        if score >= 1.5:
            verdict = "STRONG BUY"
            color = "🟢"
        elif score >= 0.5:
            verdict = "BUY"
            color = "🟢"
        elif score <= -1.5:
            verdict = "STRONG SELL"
            color = "🔴"
        elif score <= -0.5:
            verdict = "SELL"
            color = "🔴"
        else:
            verdict = "HOLD"
            color = "⚪"
            
        return {
            "score": score,
            "verdict": verdict,
            "color": color,
            "signals": signals
        }

    def _rule_based_analysis(self, ticker, quant_data, researcher_data, error_msg=None):
        """Fallback logic if AI fails."""
        analysis = self.get_signal(quant_data, researcher_data)
        verdict = analysis["verdict"]
        signals = analysis["signals"]
        
        error_context = f"Error: {error_msg}" if error_msg else "AI generation failed."
        
        return f"""
# A.R.E.S. Fallback Report: {ticker}
## ⚖️ Verdict: {analysis['color']} {verdict}
**Note**: {error_context} Using basic rules.

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
        # Retry logic for API limits
        import time
        max_retries = 3
        backoff = 4 # seconds (increased)
        
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                return response.text
                
            except Exception as e:
                err_str = str(e)
                logger.warning(f"Gemini API attempt {attempt+1} failed: {err_str}")
                
                # Check for 429 (Rate Limit)
                if "429" in err_str:
                    if attempt < max_retries - 1:
                        time.sleep(backoff * (attempt + 2)) # 8s, 12s...
                        continue
                    else:
                        return self._rule_based_analysis(ticker, quant_data, researcher_data, 
                                                         error_msg="Gemini Quota Exceeded (429). Please wait a few seconds.")

                if attempt < max_retries - 1:
                    time.sleep(backoff * (2 ** attempt)) # 4s, 8s
                else:
                    # Clean up the error message for the UI
                    clean_err = err_str.split('\n')[0] # Get only first line
                    return self._rule_based_analysis(ticker, quant_data, researcher_data, error_msg=clean_err)
        
        return self._rule_based_analysis(ticker, quant_data, researcher_data, error_msg="Unknown AI failure.")
