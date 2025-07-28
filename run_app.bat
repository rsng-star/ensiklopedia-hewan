@echo off
cd /d %~dp0
call venv\Scripts\activate.bat

REM Menjalankan server
python server\main.py

REM Menjalankan client
start cmd /k "call venv\Scripts\activate.bat && streamlit run client\app.py"

pause