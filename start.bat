@echo off
set scriptpath=%~dp0
set PYTHONPATH=%scriptpath%Python;%scriptpath%library
python app.py %scriptpath%
exit /b 0
pause