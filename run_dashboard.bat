@echo off
TITLE A.R.E.S. System
echo Starting A.R.E.S. Neural Interface...
cd /d "%~dp0"
python -m streamlit run app.py
pause
