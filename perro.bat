@echo off
call venv\Scripts\activate
cd /d backend
start cmd /k "python app.py"
cd ../frontend
start cmd /k "npm start"
exit
