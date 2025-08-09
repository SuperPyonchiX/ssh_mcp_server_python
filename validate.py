#!/usr/bin/env python3

"""
SSH MCP Server用の設定検証ツール
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def check_env_file():
    """環境設定ファイルをチェック"""
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    print("[INFO] Environment file check:")
    
    if not env_file.exists():
        print("  [ERROR] .env file not found")
        if env_example.exists():
            print("  [INFO] Creating .env from .env.example...")
            with open(env_example, 'r', encoding='utf-8') as src, open(env_file, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
            print("  [OK] .env file created")
        else:
            print("  [ERROR] .env.example file also not found")
            return False
    else:
        print("  [OK] .env file found")
    
    return True

def validate_ssh_config():
    """SSH設定の妥当性をチェック"""
    load_dotenv()
    
    print("\n[INFO] SSH configuration validation:")
    
    required_vars = {
        'UBUNTU_SSH_HOST': 'SSH Host',
        'UBUNTU_SSH_USERNAME': 'SSH Username'
    }
    
    missing_vars = []
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            print(f"  [ERROR] {description} ({var}) is not set")
            missing_vars.append(var)
        else:
            print(f"  [OK] {description} is set")
    
    # 認証方法のチェック
    password = os.getenv('UBUNTU_SSH_PASSWORD')
    private_key_path = os.getenv('UBUNTU_SSH_PRIVATE_KEY_PATH')
    
    if not password and not private_key_path:
        print("  [ERROR] Neither password nor private key path is set")
        print("     Please set either UBUNTU_SSH_PASSWORD or UBUNTU_SSH_PRIVATE_KEY_PATH")
        missing_vars.append('authentication')
    elif password:
        print("  [OK] Password authentication is configured")
    elif private_key_path:
        if os.path.exists(private_key_path):
            print("  [OK] Private key authentication is configured")
        else:
            print(f"  [ERROR] Private key file not found: {private_key_path}")
            missing_vars.append('private_key_file')
    
    # ポート番号のチェック
    port = os.getenv('UBUNTU_SSH_PORT', '22')
    try:
        port_num = int(port)
        if 1 <= port_num <= 65535:
            print(f"  [OK] SSH Port: {port_num}")
        else:
            print(f"  [ERROR] Invalid port number: {port_num}")
            missing_vars.append('port')
    except ValueError:
        print(f"  [ERROR] Invalid port format: {port}")
        missing_vars.append('port')
    
    return len(missing_vars) == 0

def check_python_dependencies():
    """Python依存関係をチェック"""
    print("\n[INFO] Python dependencies check:")
    
    required_packages = ['fastmcp', 'paramiko', 'python-dotenv']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'python-dotenv':
                __import__('dotenv')
            else:
                __import__(package)
            print(f"  [OK] {package} is installed")
        except ImportError:
            print(f"  [ERROR] {package} is not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n[INFO] To install missing packages, run:")
        print(f"   pip install {' '.join(missing_packages)}")
        print(f"   Or: pip install -r requirements.txt")
    
    return len(missing_packages) == 0

def main():
    print("SSH MCP Server - Configuration Validator")
    print("=" * 50)
    
    all_good = True
    
    # 各チェックを実行
    if not check_env_file():
        all_good = False
    
    if not validate_ssh_config():
        all_good = False
    
    if not check_python_dependencies():
        all_good = False
    
    print("\n" + "=" * 50)
    
    if all_good:
        print("[SUCCESS] All checks passed! Your SSH MCP Server is ready to run.")
        print("\nTo start the server:")
        print("  Windows: start.bat")
        print("  Linux/Mac: ./start.sh")
        print("  Direct: python src/main.py")
    else:
        print("[ERROR] Some issues were found. Please fix them before running the server.")
        sys.exit(1)

if __name__ == "__main__":
    main()
