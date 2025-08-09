# SSH MCP Server (Python)

SSH接続機能を提供するMCP（Model Context Protocol）サーバーのPython実装です。FastMCPライブラリを使用し、uvでパッケージ管理を行います。

## 機能

- **SSH接続管理**: パスワード認証および秘密鍵認証に対応
- **リモートコマンド実行**: 作業ディレクトリ指定も可能
- **ファイル転送**: SFTP経由でのアップロード・ダウンロード
- **システム情報取得**: 接続先の詳細な情報を取得
- **自動設定検証**: 設定の妥当性を自動でチェック
- **詳細ログ出力**: デバッグに便利なログ機能

## 前提条件

- Python 3.10以上
- uv（Python パッケージマネージャー）

uvのインストール：
```bash
# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## クイックスタート

### 1. 依存関係のセットアップ

```bash
uv sync
```

このコマンドで以下が実行されます：
- 仮想環境の自動作成
- 必要なPythonパッケージのインストール
- ロックファイル（uv.lock）の生成

### 2. SSH接続情報の設定

`.env`ファイルを編集してSSH接続情報を設定してください：

```env
# 基本設定
UBUNTU_SSH_HOST=192.168.1.100
UBUNTU_SSH_PORT=22
UBUNTU_SSH_USERNAME=your_username

# パスワード認証の場合
UBUNTU_SSH_PASSWORD=your_password

# または秘密鍵認証の場合
UBUNTU_SSH_PRIVATE_KEY_PATH=/path/to/your/private/key
UBUNTU_SSH_PRIVATE_KEY_PASSPHRASE=your_passphrase_if_needed
```

### 3. サーバーの起動

```bash
# uvを使った実行（推奨）
uv run ssh-mcp-server

# または起動スクリプトを使用
# Windows
start.bat

# Linux/Mac
./start.sh
```

## 利用可能なツール

1. **connect_ssh** - パラメータを指定してSSH接続を確立
2. **connect_ssh_env** - 環境変数のみを使用してSSH接続
3. **execute_command** - リモートコマンドの実行（作業ディレクトリ指定可能）
4. **upload_file** - ファイルのアップロード（ディレクトリ自動作成）
5. **download_file** - ファイルのダウンロード（ローカルディレクトリ自動作成）
6. **disconnect_ssh** - SSH接続を切断
7. **get_system_info** - 詳細なシステム情報を取得

## 手動セットアップ（詳細）

### 依存関係のインストール

```bash
# uvを使用（推奨）
uv sync

# または従来のpip
pip install fastmcp paramiko python-dotenv
```

必要なパッケージ：
- `fastmcp` - MCP（Model Context Protocol）サーバーフレームワーク
- `paramiko` - SSH/SFTPクライアント
- `python-dotenv` - 環境変数管理

### 開発環境での実行

```bash
# 開発モードでの実行
uv run python ssh_mcp_server_python/main.py

# または仮想環境を有効化して実行
uv shell
python ssh_mcp_server_python/main.py
```

### 設定検証

設定が正しく構成されているかチェックできます：

```bash
python validate.py
```

このコマンドは以下をチェックします：
- `.env`ファイルの存在
- 必須設定項目の確認
- 秘密鍵ファイルの存在確認
- Pythonパッケージのインストール状況

## 使用方法

このサーバーはModel Context Protocolを使用して通信します。MCPクライアント（例：Claude Desktop、VS Code拡張など）から上記のツールを呼び出すことができます。

### 基本的な使用フロー

1. `connect_ssh_env` でSSH接続を確立
2. `execute_command` でリモートコマンドを実行
3. 必要に応じて `upload_file` / `download_file` でファイル転送
4. `get_system_info` でシステム情報を取得
5. 作業完了後、`disconnect_ssh` で接続を切断

### 例：リモートでのPythonスクリプト実行

```
1. connect_ssh_env()
2. upload_file("local_script.py", "/tmp/script.py")
3. execute_command("python3 /tmp/script.py", cwd="/tmp")
4. download_file("/tmp/output.txt", "result.txt")
5. disconnect_ssh()
```

## トラブルシューティング

### 一般的な問題

1. **接続エラー**: `.env`ファイルの設定を確認
2. **認証エラー**: パスワードまたは秘密鍵の設定を確認
3. **パッケージエラー**: `pip install -r requirements.txt` を実行

### ログの確認

サーバー実行時に詳細なログが出力されます。接続やコマンド実行の状況を確認できます。

### デバッグモード

より詳細なログが必要な場合は、`src/main.py`内のログレベルを変更してください：

```python
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
```

## セキュリティに関する注意

- `.env`ファイルには機密情報が含まれるため、バージョン管理に含めないでください
- SSH接続は信頼できるネットワークでのみ使用してください
- 秘密鍵ファイルの権限設定に注意してください（通常は600）

## ライセンス

MIT License
