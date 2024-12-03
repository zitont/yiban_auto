@echo off
REM Activate the virtual environment
call D:\project\yiban_auto\venv\Scripts\activate

REM Navigate to the directory where the Python script is located
cd /d D:\project\yiban_auto

REM Execute the Python script
python run.py

REM End of the batch file