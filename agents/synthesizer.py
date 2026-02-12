class Synthesizer:
    def __init__(self):
        pass

    def get_signal(self, quant_data: dict, researcher_data: dict) -> dict:
        """
        Calculates the score and verdict based on input data.
        Returns a dict with 'score', 'verdict', 'color', and 'signals' list.
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
            signals.append(f"🟢 **Sentiment**: Market News are Optimistic (Score: {polarity}).")
            score += 0.5
        elif sentiment == "Bearish":
            signals.append(f"🔴 **Sentiment**: Market News are Pessimistic (Score: {polarity}).")
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

    def synthesize(self, ticker: str, quant_data: dict, researcher_data: dict) -> str:
        """
        Combines quantitative and fundamental data to generate a consensus report.
        """
        analysis = self.get_signal(quant_data, researcher_data)
        
        report = f"# A.R.E.S. Synthesis Report: {ticker}\n\n"
        
        # Extract breakdown
        score = analysis["score"]
        verdict = analysis["verdict"]
        color = analysis["color"]
        signals = analysis["signals"]
        
        rsi = quant_data.get("RSI (14)", 50)
        volatility = quant_data.get("Annualized Volatility", 0)
        total_debt = researcher_data.get("Total Debt", 0)
        cash = researcher_data.get("Cash", 0)
        fcf = researcher_data.get("Free Cash Flow", 0)
        sent_val = researcher_data.get("sentiment", {}).get("polarity", 0)

        # Construct Report
        report += f"## ⚖️ Final Verdict: {color} {verdict}\n"
        report += f"**Confidence Score**: {score:.1f} / 3.0\n\n"
        
        report += "### 🧠 Decision Rationale\n"
        for signal in signals:
            report += f"- {signal}\n"
            
        report += "\n### 📊 Data Summary\n"
        report += "| Metric | Value | Source |\n"
        report += "| :--- | :--- | :--- |\n"
        report += f"| RSI (14) | {rsi:.2f} | Quant Agent |\n"
        report += f"| Volatility (Ann) | {volatility:.2%} | Quant Agent |\n"
        report += f"| Free Cash Flow | ${fcf:,.0f} | Researcher Agent |\n"
        report += f"| Net Cash Position | ${(cash - total_debt):,.0f} | Researcher Agent |\n"
        report += f"| Sentiment Score | {sent_val} | NLP Agent |\n"

        return report
