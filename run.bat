@echo off
REM activating env
call "%CD%\.venv\Scripts\activate.bat"
echo done


REM Run your Python script (chappy.py)
echo Running your Python script (chappy.py)
call python chappy.py
echo done