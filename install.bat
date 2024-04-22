@echo off

REM Upgrading pip
call python -m pip install pip --upgrade
echo Done

REM Create a new virtual environment in the .venv folder
echo Creating a new Python virtual environment in the .venv folder
call python -m venv .venv
echo Done

REM Activate the virtual environment
echo Activating the virtual environment
call %CD%\.venv\Scripts\activate.bat
echo Done

REM Install the required packages from requirements.txt
echo Installing required packages from requirements.txt
call pip install -r requirements.txt
echo Done

REM Install playwright
echo Installing playwright
call playwright install
echo Done

REM Run your Python script HexAmerous.py
echo Running your Python script HexAmerous.py
call python HexAmerous.py