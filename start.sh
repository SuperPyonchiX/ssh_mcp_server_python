#!/bin/bash

echo "SSH MCP Server (Python) - Starting..."
echo "========================================="

# Pythonがインストールされているかチェック
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8 or later"
    exit 1
fi

echo "Python version: $(python3 --version)"

# .envファイルの存在チェック
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found"
    if [ -f ".env.example" ]; then
        echo "Creating .env from .env.example..."
        cp ".env.example" ".env"
        echo ".env file created from .env.example"
        echo "Please edit .env file with your SSH connection details"
        read -p "Press Enter to continue..."
    else
        echo "Error: .env.example file not found"
        echo "Please create .env file manually with your SSH settings"
        exit 1
    fi
fi

# 必要なパッケージがインストールされているかチェック
if ! python3 -c "import fastmcp, paramiko, dotenv" &> /dev/null; then
    echo "Installing required packages..."
    python3 -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install required packages"
        exit 1
    fi
fi

echo ""
echo "Starting SSH MCP Server..."
echo "Press Ctrl+C to stop the server"
echo ""

python3 src/main.py

if [ $? -ne 0 ]; then
    echo ""
    echo "Server exited with error"
else
    echo ""
    echo "Server stopped normally"
fi
