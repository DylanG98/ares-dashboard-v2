# A.R.E.S. (Autonomous Research & Equity System) 🤖📈

A.R.E.S. is a modular Python-based financial analysis system powered by multiple specialized agents working in parallel. It demonstrates the power of agentic workflows in financial research.

## 🌟 Features

*   **Multi-Agent Architecture**:
    *   **🤖 Quant Agent**: Performs technical analysis, calculates risk metrics (Volatility, Drawdown), and momentum indicators (RSI, Bollinger Bands).
    *   **🕵️ Researcher Agent**: Analyzes company fundamentals directly from filings (Balance Sheet, Cash Flow, Debt).
    *   **⚖️ Synthesizer Agent**: Acts as a "Consensus Engine", combining quantitative and qualitative data to issue a final **Buy/Sell/Hold** verdict.
*   **Parallel Execution**: Agents run concurrently using threading for high performance.
*   **Comprehensive Reporting**: Generates three markdown reports per ticker:
    1.  `REPORTE_QUANT_{TICKER}.md` (Technical)
    2.  `REPORTE_RESEARCHER_{TICKER}.md` (Fundamental)
    3.  `REPORTE_SYNTHESIS_{TICKER}.md` (Combined Vision)
*   **Visualizations**: Automatically generates technical charts with Bollinger Bands plotted.

## 🚀 Getting Started

### Prerequisites

*   Python 3.10+
*   `pip` (Python Package Installer)

### Installation

1.  **Clone or Download** this repository.
2.  **Navigate** to the project folder:
    ```bash
    cd A.R.E.S
    ```
3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

### Usage

Run the main script with a stock ticker symbol (e.g., AAPL, TSLA, NVDA):

```bash
python main.py AAPL
```

Or run interactively:
```bash
python main.py
```

### 📂 Project Structure

*   `agents/`: Contains the logic for the Quant, Researcher, and Synthesizer agents.
*   `utils/`: Helper functions for data loading.
*   `output/`: Stores generated charts (e.g., `AAPL_analysis.png`).
*   `main.py`: The orchestrator script.

---
*Built with Python, yfinance, and Matplotlib.*
