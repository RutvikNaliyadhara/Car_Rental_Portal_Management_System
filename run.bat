@echo off
echo Activating virtual environment and starting Django server...
call .\venv\Scripts\activate.bat
python manage.py runserver
pause
