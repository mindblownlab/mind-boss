@echo off
set scriptpath=%~dp0
set PYTHONPATH=%scriptpath%Python
python app.py
exit /b 0
pause