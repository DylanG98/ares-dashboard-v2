import sys
import threading
import os
from datetime import datetime
from agents.quant import QuantEngine
from agents.researcher import Researcher
from agents.synthesizer import Synthesizer
from utils.data_loader import get_market_data
from utils.html_generator import HTMLReporter
from utils.logger import setup_logger

# Initialize Logger
logger = setup_logger()

def main():
    logger.info("Welcome to A.R.E.S. (Autonomous Research & Equity System)")
    
    if len(sys.argv) > 1:
        ticker = sys.argv[1].upper()
    else:
        ticker = input("What asset do you want to analyze today? (Ticker): ").strip().upper()
    
    if not ticker:
        logger.error("Invalid Ticker.")
        return

    logger.info(f"Targeting: {ticker}...")
    
    # Setup Output Directory
    today = datetime.now().strftime("%Y-%m-%d")
    report_dir = os.path.join("reports", ticker, today)
    os.makedirs(report_dir, exist_ok=True)
    logger.info(f"Reports will be saved to: {report_dir}")

    # 1. Fetch Data (Quant Dependency)
    try:
        # Saving raw data in data/raw/{ticker}_{period}_{date}.csv
        df = get_market_data(ticker, period="5y", save_dir=os.path.join("data", "raw"))
    except Exception as e:
        logger.critical(f"Critical Error: {e}")
        return

    # 2. Initialize Agents
    # QuantEngine will save charts to report_dir
    quant_agent = QuantEngine(ticker, df, output_dir=report_dir)
    researcher_agent = Researcher()
    synthesizer_agent = Synthesizer()
    html_reporter = HTMLReporter()

    results = {}
    
    def run_quant():
        logger.info("Quant Agent: Crunching numbers...")
        results['quant'] = quant_agent.analyze()
        logger.info("Quant Agent: Done.")

    def run_researcher():
        logger.info("Researcher Agent: Gathering intel...")
        # Get Fundamentals
        res = researcher_agent.get_market_intel(ticker)
        # Get Sentiment
        sent = researcher_agent.get_sentiment(ticker)
        
        # Merge
        res['data']['sentiment'] = sent
        res['report'] += f"\n\n### 📰 News Sentiment Analysis\n"
        res['report'] += f"**Mood**: {sent['sentiment']} (Score: {sent['polarity']})\n"
        res['report'] += "**Top Headlines:**\n"
        for h in sent['headlines']:
            res['report'] += f"- {h}\n"
            
        results['researcher'] = res
        logger.info("Researcher Agent: Done.")

    # 3. Parallel Execution
    t1 = threading.Thread(target=run_quant)
    t2 = threading.Thread(target=run_researcher)
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()

    # 4. Synthesis & Reporting
    logger.info("Starting Synthesis...")
    
    # Extract data
    quant_res = results.get('quant', {})
    research_res_full = results.get('researcher', {})
    
    if isinstance(research_res_full, dict):
        research_report = research_res_full.get('report', "No Data")
        research_data = research_res_full.get('data', {})
    else:
        research_report = str(research_res_full)
        research_data = {}

    # Generar Reportes Individuales (Markdown)
    save_report(os.path.join(report_dir, f"REPORTE_QUANT_{ticker}.md"), generate_quant_report(ticker, quant_res))
    save_report(os.path.join(report_dir, f"REPORTE_RESEARCHER_{ticker}.md"), research_report)
    
    # Generar Reporte de Síntesis (Markdown)
    synthesis_report = synthesizer_agent.synthesize(ticker, quant_res, research_data)
    save_report(os.path.join(report_dir, f"REPORTE_SYNTHESIS_{ticker}.md"), synthesis_report)
    
    # Generar Reporte Ejecutivo (HTML)
    html_path = os.path.join(report_dir, f"REPORTE_EJECUTIVO_{ticker}.html")
    html_reporter.generate_report(ticker, quant_res, research_data, synthesis_report, html_path)
    logger.info(f"Saved HTML Report: {html_path}")
    
    logger.info(f"All reports generated for {ticker}!")

def generate_quant_report(ticker: str, quant_res: dict) -> str:
    """
    Generates a markdown report for the Quantitative Analysis results.

    Args:
        ticker (str): The stock ticker symbol.
        quant_res (dict): Dictionary containing quantitative metrics and plot paths.

    Returns:
        str: Formatted markdown string.
    """
    if "error" in quant_res:
        return f"# Quant Report: {ticker}\n\nError: {quant_res['error']}"
        
    report = f"# Quantitative Analysis: {ticker}\n\n"
    
    report += "## 📊 Technical Metrics\n"
    report += f"- **Last Price**: ${quant_res.get('Last Price', 0):.2f}\n"
    report += f"- **Annualized Volatility**: {quant_res.get('Annualized Volatility', 0):.2%}\n"
    report += f"- **Max Drawdown**: {quant_res.get('Max Drawdown', 0):.2%}\n"
    report += f"- **RSI (14)**: {quant_res.get('RSI (14)', 0):.2f}\n\n"

    report += "## 📐 Advanced Risk & Trend Metrics\n"
    report += f"- **Sharpe Ratio**: {quant_res.get('Sharpe Ratio', 0):.2f} (Risk-Free assumed 4%)\n"
    report += f"- **Value at Risk (95%)**: {quant_res.get('VaR (95%)', 0):.2%}\n"
    report += f"- **Beta (vs SPY)**: {quant_res.get('Beta', 0):.2f}\n"
    
    slope = quant_res.get('Trend Slope', 0)
    direction = "📈 Up" if slope > 0 else "📉 Down"
    report += f"- **Linear Regression Trend**: {direction} (Slope: {slope:.4f})\n"
    report += f"- **R-Squared (Trend Strength)**: {quant_res.get('R-Squared', 0):.4f}\n\n"
    
    plot_path = quant_res.get('Plot Path')
    if plot_path:
        plot_basename = os.path.basename(plot_path)
        report += f"![Technical Chart]({plot_basename})\n"
    
    return report

def save_report(filename: str, content: str) -> None:
    """Writes the content strings to a file with UTF-8 encoding."""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    logger.info(f"Saved: {filename}")

if __name__ == "__main__":
    main()
