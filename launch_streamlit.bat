@echo off
REM Lancer l'application Streamlit avec l'environnement virtuel

echo Demarrage de l'application Streamlit...
echo.

REM Lancer PowerShell avec les commandes nécessaires
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass; & '.\.venv\Scripts\Activate.ps1'; streamlit run app.py"

pause
