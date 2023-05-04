REM activating env
call "%CD%\.venv\Scripts\activate.bat"
echo export PATH="$PATH:%CD%\.venv\Lib\site-packages" >> ~\.bashrc
echo done


REM Run your Python script HexAmerous.py
echo Running your Python script HexAmerous.py
call python HexAmerous.py
echo done