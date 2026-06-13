@echo off
title FIN-BOT
cd /d "%~dp0"
echo Abrindo o painel FIN-BOT no navegador...
python -m streamlit run dashboard.py
pause
