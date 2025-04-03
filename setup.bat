@echo off
echo Setting up Dog Training Assistant...

REM Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python and try again.
    exit /b
)

REM Check if Node.js is installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo Node.js is not installed. Please install Node.js and try again.
    exit /b
)

REM Backend Setup
echo Setting up backend...
cd backend

REM Create a virtual environment if not already created
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created.
)

REM Activate the virtual environment
call venv\Scripts\activate

REM Install the backend dependencies
pip install -r requirements.txt

echo Backend setup complete.
cd ..

REM Frontend Setup
echo Setting up frontend...
cd frontend

REM Install frontend dependencies
if exist "node_modules" (
    echo Node modules already installed.
) else (
    npm install
    echo Frontend dependencies installed.
)

cd ..

echo Setup complete! Run 'perro.bat' to start the application.
