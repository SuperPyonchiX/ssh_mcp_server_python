@echo off
echo SSH MCP Server (Python) - Starting...
echo =========================================

REM Pythonがインストールされているかチェック
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or later
    pause
    exit /b 1
)

REM .envファイルの存在チェック
if not exist ".env" (
    echo Warning: .env file not found
    echo Creating .env from .env.example...
    if exist ".env.example" (
        copy ".env.example" ".env"
        echo .env file created from .env.example
        echo Please edit .env file with your SSH connection details
        pause
    ) else (
        echo Error: .env.example file not found
        echo Please create .env file manually with your SSH settings
        pause
        exit /b 1
    )
)

REM 必要なパッケージがインストールされているかチェック
python -c "import fastmcp, paramiko, dotenv" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install required packages
        pause
        exit /b 1
    )
)

echo.
echo Starting SSH MCP Server...
echo Press Ctrl+C to stop the server
echo.

python src\main.py

if errorlevel 1 (
    echo.
    echo Server exited with error
    pause
) else (
    echo.
    echo Server stopped normally
)
