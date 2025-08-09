# SSH MCP Server (Python)

SSH接続機能を提供するMCP（Model Context Protocol）サーバーのPython実装です。FastMCPライブラリを使用し、uvでパッケージ管理を行います。

## 📁 プロジェクト構造

```
ssh_mcp_server_python/
├── pyproject.toml          # プロジェクト設定とビルド設定
├── uv.lock                 # 依存関係ロックファイル
├── src/                    # ソースコード
│   └── ssh_mcp_server_python/
│       ├── __init__.py     # パッケージ初期化
│       └── main.py         # メインサーバー実装
├── .env                    # 環境設定（要作成）
├── .env.example            # 環境設定テンプレート
├── start.bat               # Windows起動スクリプト
├── start.sh                # Linux/Mac起動スクリプト
├── test_tools_list.py      # ツールリストテスト
├── validate.py             # 設定検証スクリプト
└── README.md               # このファイル
```

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

| ツール名 | 説明 | 主要パラメータ |
|---------|------|----------------|
| **connect_ssh** | SSH接続を確立 | host, username, password/private_key |
| **execute_command** | リモートコマンド実行 | command, cwd（作業ディレクトリ） |
| **upload_file** | ファイルアップロード | local_path, remote_path |
| **download_file** | ファイルダウンロード | remote_path, local_path |
| **disconnect_ssh** | SSH接続切断 | なし |
| **get_system_info** | システム情報取得 | なし |

### ツールの詳細

- **connect_ssh**: パラメータ未指定時は環境変数（.env）の値を使用
- **execute_command**: 標準出力・標準エラー・終了コードをすべて取得
- **upload_file/download_file**: ディレクトリ自動作成機能付き
- **get_system_info**: uname、ディスク使用量、メモリ、プロセス情報など

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
uv run python src/ssh_mcp_server_python/main.py

# または仮想環境を有効化して実行
uv shell
python src/ssh_mcp_server_python/main.py
```

### 設定検証

設定が正しく構成されているかチェックできます：

```bash
uv run python validate.py
```

このコマンドは以下をチェックします：
- `.env`ファイルの存在
- 必須設定項目の確認
- 秘密鍵ファイルの存在確認
- Pythonパッケージのインストール状況

### テスト実行

ツールリストの動作確認：

```bash
uv run python test_tools_list.py
```

## VS Code / Claude Desktop での設定

### VS Code MCP設定

VS CodeでCopilotと連携する場合、`mcp.json`ファイルに以下の設定を追加してください：

**ファイル場所**: 
- Windows: `%APPDATA%\Code\User\mcp.json`  
- macOS: `~/Library/Application Support/Code/User/mcp.json`
- Linux: `~/.config/Code/User/mcp.json`

```json
{
  "servers": {
    "ssh-mcp-server": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/your/ssh_mcp_server_python",
        "ssh-mcp-server"
      ],
      "env": {
        "UBUNTU_SSH_HOST": "192.168.56.103",
        "UBUNTU_SSH_PORT": "22",
        "UBUNTU_SSH_USERNAME": "your_username",
        "UBUNTU_SSH_PASSWORD": "your_password"
      }
    }
  }
}
```

### Claude Desktop設定

Claude Desktopで使用する場合、設定ファイルに以下を追加：

**ファイル場所**:
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ssh-server": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/your/ssh_mcp_server_python",
        "ssh-mcp-server"
      ],
      "env": {
        "UBUNTU_SSH_HOST": "192.168.56.103",
        "UBUNTU_SSH_PORT": "22",
        "UBUNTU_SSH_USERNAME": "your_username",
        "UBUNTU_SSH_PASSWORD": "your_password"
      }
    }
  }
}
```

### 設定のポイント

1. **パス設定**: `--directory`のパスは、あなたの環境に合わせて変更してください
2. **環境変数**: SSH接続情報は`.env`ファイルまたは設定ファイル内で指定
3. **セキュリティ**: パスワードは設定ファイル内ではなく、`.env`ファイルを推奨

## 使用方法

このサーバーはModel Context Protocolを使用して通信します。MCPクライアント（例：Claude Desktop、VS Code拡張など）から上記のツールを呼び出すことができます。

### 基本的な使用フロー

1. `connect_ssh` でSSH接続を確立
2. `execute_command` でリモートコマンドを実行
3. 必要に応じて `upload_file` / `download_file` でファイル転送
4. `get_system_info` でシステム情報を取得
5. 作業完了後、`disconnect_ssh` で接続を切断

### 使用例：Dockerビルド実行

```
1. connect_ssh() でSSH接続
2. execute_command("docker run --rm -v /home/user/project:/workspace -w /workspace ubuntu-dev bash -c './Build.sh'")
3. disconnect_ssh() で切断
```

### 使用例：ファイル転送とスクリプト実行

```
1. connect_ssh() でSSH接続
2. upload_file("local_script.py", "/tmp/script.py")
3. execute_command("python3 /tmp/script.py", cwd="/tmp")
4. download_file("/tmp/output.txt", "result.txt")
5. disconnect_ssh() で切断
```

## トラブルシューティング

### 一般的な問題

1. **接続エラー**: `.env`ファイルの設定を確認
2. **認証エラー**: パスワードまたは秘密鍵の設定を確認
3. **パッケージエラー**: `uv sync` を実行
4. **コマンドが見つからない**: `uv run ssh-mcp-server` でパスを確認

### uvコマンドの問題

```bash
# 間違い
uv python test_tools_list.py

# 正しい
uv run python test_tools_list.py
```

### ログの確認

サーバー実行時に詳細なログが出力されます。接続やコマンド実行の状況を確認できます。

### デバッグモード

より詳細なログが必要な場合は、`src/ssh_mcp_server_python/main.py`内のログレベルを変更してください：

```python
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
```

## セキュリティに関する注意

- `.env`ファイルには機密情報が含まれるため、バージョン管理に含めないでください
- SSH接続は信頼できるネットワークでのみ使用してください
- 秘密鍵ファイルの権限設定に注意してください（通常は600）
- 本番環境では、環境変数での認証情報管理を推奨します

## 技術仕様

- **プログラミング言語**: Python 3.10+
- **MCPフレームワーク**: FastMCP 2.11.2
- **パッケージマネージャー**: uv
- **プロジェクト構造**: src-layout
- **SSH/SFTPライブラリ**: paramiko
- **設定管理**: python-dotenv

## 開発者向け情報

### uvの特徴
- **高速**: 従来のpipより高速なパッケージ解決・インストール
- **再現可能**: uv.lockによる確実な依存関係管理
- **シンプル**: 仮想環境とパッケージ管理の統合

### src-layout構造の採用
- **標準的**: Python業界で広く採用されている構造
- **分離**: ソースコードとプロジェクトファイルの明確な分離
- **テスト**: テストファイルとソースコードの適切な分離

## ライセンス

MIT License
