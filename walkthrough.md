# A.R.E.S. Architecture & Operations Report

## 🏗️ System Architecture

The A.R.E.S. (Autonomous Research & Equity System) is designed as a modular, multi-agent Python application for financial analysis. The core principle is **Separation of Concerns**, where distinct agents handle specific domains (Quantitative vs. Qualitative) in parallel.

### Component Overview

1.  **Orchestrator (`main.py`)**:
    - **Role**: The central nervous system. It initializes the agents, manages user input (Ticker), and orchestrates parallel execution using threading.
    - **Logic**: Spawns two threads (`run_quant` and `run_researcher`) to ensure that heavy data processing does not block the collection of market intelligence.
    - **Output**: Consolidates results into a structured Markdown report (`REPORTE_{TICKER}.md`).

2.  **The Quant Agent (`agents/quant.py`)**:
    - **Role**: Mathematical and Statistical Analysis.
    - **Data Source**: OHLCV data from `yfinance`.
    - **Calculations**:
        - **Log Returns**: For accurate volatility estimation.
        - **Annualized Volatility**: A key risk metric.
        - **RSI (Relative Strength Index)**: Momentum indicator (14-period). *Implemented manually due to dependency constraints.*
        - **Bollinger Bands**: Volatility bands (20-period SMA ± 2 STD). *Implemented manually.*
    - **Artifacts**: Generates a technical chart (`output/{TICKER}_analysis.png`).

3.  **The Researcher Agent (`agents/researcher.py`)**:
    - **Role**: Fundamental Analysis (Balance Sheet & Cash Flow).
    - **Tooling**: Uses `yfinance`.
    - **Logic**: extracting key financial metrics (Debt, Cash, FCF) directly from company filings instead of relying on web scraping.

4.  **The Synthesizer Agent (`agents/synthesizer.py`)**:
    - **Role**: Consensus Engine.
    - **Logic**: Reads outputs from Quant and Researcher. Applies rule-based logic to determine a verdict (Buy/Sell/Hold) based on RSI and Cash Flow/Debt ratios.
    - **Output**: Generates a unified `REPORTE_SYNTHESIS_{TICKER}.md`.

5.  **Data Utility (`utils/data_loader.py`)**:
    - **Role**: Robust data fetching wrapper. Handles connection to `yfinance` and basic error checking.

### 5. Backend Fix
- **Matplotlib**: Set backend to `Agg` to prevent GUI threading errors during report generation.

---

## 🛠️ Operations Log & Implementation Details

### 1. Project Setup
- **Directory Structure**: Created a scalable folder structure (`agents/`, `utils/`, `output/`) to separate logic, utilities, and artifacts.
- **Environment**: Set up a virtual environment metadata and `requirements.txt`.

### 2. Dependency Management Challenge
- **Issue**: The original plan included `pandas_ta` for technical analysis. However, `pandas_ta` requires `numba`, which failed to compile on **Python 3.14** (the user's current environment) due to lack of wheel support for this newer version.
- **Resolution**: Removing `pandas_ta` and manually implementing the RSI and Bollinger Bands algorithms using `pandas` and `numpy` vectorization. This kept the system lightweight and compatible without waiting for upstream updates.

### 3. Concurrency Implementation
- **Design Choice**: Used `threading` in `main.py` instead of `multiprocessing`. Since the tasks are I/O bound (network requests for data and search), threads are sufficient and entail less overhead than spawning full processes.

### 4. Bug Fix: Console Encoding
- **Issue**: The Windows console (cp1252) crashed when trying to print emoji characters (🤖, 🕵️) used in the status updates.
- **Fix**: Removed non-standard characters from `print()` statements in `main.py` to ensure cross-platform compatibility without requiring the user to change their system locale.

## ✅ Verification Status
- **Codebase**: Fully implemented.
- **Dependencies**: Installed and verified.
- **Test Run**: Ready to execute on Ticker "AAPL" to generate the final report and chart.
