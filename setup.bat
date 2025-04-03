@echo off

REM Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python.
    exit /b
)

REM Create a virtual environment if not already created
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created.
)

REM Activate the virtual environment
call venv\Scripts\activate

REM Install the dependencies
pip install -r requirements.txt

echo Setup complete. Virtual environment is activated.
