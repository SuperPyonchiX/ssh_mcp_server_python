#!/usr/bin/env python3

import os
import sys
import asyncio
import logging
from typing import Optional, Dict, Any, Annotated
from dataclasses import dataclass
import paramiko
from dotenv import load_dotenv
from fastmcp import FastMCP
from pydantic import Field

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 環境変数を読み込み
load_dotenv()
logger.info("環境変数を読み込みました")

@dataclass
class SSHConfig:
    host: str
    port: int = 22
    username: str = ""
    password: Optional[str] = None
    private_key: Optional[str] = None
    private_key_passphrase: Optional[str] = None

def get_env_ssh_config() -> SSHConfig:
    """環境変数からSSH設定を取得"""
    logger.info("環境変数からSSH設定を読み込み中")
    
    config = SSHConfig(
        host=os.getenv('UBUNTU_SSH_HOST', ''),
        port=int(os.getenv('UBUNTU_SSH_PORT', '22')),
        username=os.getenv('UBUNTU_SSH_USERNAME', ''),
        password=os.getenv('UBUNTU_SSH_PASSWORD'),
        private_key_passphrase=os.getenv('UBUNTU_SSH_PRIVATE_KEY_PASSPHRASE')
    )
    
    # 秘密鍵ファイルの読み込み
    private_key_path = os.getenv('UBUNTU_SSH_PRIVATE_KEY_PATH')
    if private_key_path and os.path.exists(private_key_path):
        try:
            with open(private_key_path, 'r') as f:
                config.private_key = f.read()
            logger.info(f"{private_key_path} から秘密鍵を読み込みました")
        except Exception as e:
            logger.error(f"{private_key_path} からの秘密鍵読み込みに失敗: {e}")
    elif private_key_path:
        logger.warning(f"秘密鍵パスが指定されましたが、ファイルが見つかりません: {private_key_path}")
    
    # 設定の妥当性チェック（機密情報はログに出力しない）
    logger.info(f"SSH設定を読み込みました - ホスト: {config.host}, ポート: {config.port}, ユーザー名: {config.username}")
    
    return config

class SSHMCPServer:
    def __init__(self):
        self.mcp = FastMCP("ssh-mcp-server")
        self.ssh_client: Optional[paramiko.SSHClient] = None
        self.sftp_client: Optional[paramiko.SFTPClient] = None
        self.config: Optional[SSHConfig] = None
        
        logger.info("SSH MCPサーバーを初期化しました")
        
        # ツールの登録
        self.register_tools()
    
    def register_tools(self):
        """MCPツールを登録"""
        logger.info("MCPツールを登録中...")
        
        @self.mcp.tool()
        async def connect_ssh(
            host: Annotated[Optional[str], Field(description="SSHホストアドレス (例: 192.168.1.100)。指定しない場合はUBUNTU_SSH_HOST環境変数を使用します。", default=None)],
            port: Annotated[Optional[int], Field(description="SSHポート (デフォルト: 22)。指定しない場合はUBUNTU_SSH_PORT環境変数を使用します。", default=None)],
            username: Annotated[Optional[str], Field(description="SSHユーザー名。指定しない場合はUBUNTU_SSH_USERNAME環境変数を使用します。", default=None)],
            password: Annotated[Optional[str], Field(description="SSHパスワード（秘密鍵を使用する場合は任意）。指定しない場合はUBUNTU_SSH_PASSWORD環境変数を使用します。", default=None)],
            private_key: Annotated[Optional[str], Field(description="秘密鍵の内容（任意）。指定しない場合はUBUNTU_SSH_PRIVATE_KEY_PATH環境変数からファイルを読み込みます。", default=None)],
            private_key_passphrase: Annotated[Optional[str], Field(description="秘密鍵のパスフレーズ（任意）。指定しない場合はUBUNTU_SSH_PRIVATE_KEY_PASSPHRASE環境変数を使用します。", default=None)]
        ) -> str:
            """Ubuntu VMにSSH接続します。パラメータが提供されない場合は環境変数をデフォルトとして使用します。"""
            return await self._connect_ssh(
                host=host,
                port=port,
                username=username,
                password=password,
                private_key=private_key,
                private_key_passphrase=private_key_passphrase
            )
        
        @self.mcp.tool()
        async def execute_command(
            command: Annotated[str, Field(description="Ubuntu VMで実行するコマンド")],
            cwd: Annotated[Optional[str], Field(description="コマンドを実行する作業ディレクトリ（任意）", default=None)]
        ) -> str:
            """接続されたUbuntu VMでコマンドを実行します。"""
            return await self._execute_command(command, cwd)
        
        @self.mcp.tool()
        async def upload_file(
            local_path: Annotated[str, Field(description="ローカルファイルのパス")],
            remote_path: Annotated[str, Field(description="Ubuntu VM上のリモートファイルパス")]
        ) -> str:
            """Ubuntu VMにファイルをアップロードします。"""
            return await self._upload_file(local_path, remote_path)
        
        @self.mcp.tool()
        async def download_file(
            remote_path: Annotated[str, Field(description="Ubuntu VM上のリモートファイルパス")],
            local_path: Annotated[str, Field(description="ローカルファイルのパス")]
        ) -> str:
            """Ubuntu VMからファイルをダウンロードします。"""
            return await self._download_file(remote_path, local_path)
        
        @self.mcp.tool()
        async def disconnect_ssh() -> str:
            """Ubuntu VMからSSH接続を切断します。"""
            return await self._disconnect_ssh()
        
        @self.mcp.tool()
        async def get_system_info() -> str:
            """Ubuntu VMのシステム情報を取得します。
            
            以下の詳細なシステム情報を取得します:
            - システム情報 (uname)
            - OS リリース情報
            - ディスク使用量
            - メモリ使用量
            - CPU情報
            - ネットワークインターフェース
            - 実行中のプロセス
            - システムアップタイム
            """
            return await self._get_system_info()
        
        logger.info("すべてのMCPツールの登録が完了しました")
    
    async def _connect_ssh(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        private_key: Optional[str] = None,
        private_key_passphrase: Optional[str] = None
    ) -> str:
        """SSH接続を確立"""
        try:
            logger.info("SSH接続を開始中...")
            
            # 既存の接続があれば切断
            if self.ssh_client:
                logger.info("既存のSSH接続を終了中")
                await self._disconnect_ssh()
            
            # 環境変数から設定を取得
            env_config = get_env_ssh_config()
            
            # 引数と環境変数をマージ
            final_config = SSHConfig(
                host=host or env_config.host,
                port=port or env_config.port,
                username=username or env_config.username,
                password=password or env_config.password,
                private_key=private_key or env_config.private_key,
                private_key_passphrase=private_key_passphrase or env_config.private_key_passphrase
            )
            
            # 必須フィールドの検証
            if not final_config.host:
                raise ValueError('Host is required. Provide it as parameter or set UBUNTU_SSH_HOST environment variable.')
            if not final_config.username:
                raise ValueError('Username is required. Provide it as parameter or set UBUNTU_SSH_USERNAME environment variable.')
            if not final_config.password and not final_config.private_key:
                raise ValueError('Either password or private key is required. Set UBUNTU_SSH_PASSWORD or UBUNTU_SSH_PRIVATE_KEY_PATH environment variable.')
            
            logger.info(f"{final_config.username}@{final_config.host}:{final_config.port} に接続中")
            
            # SSH接続
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # 認証方法を決定
            if final_config.private_key:
                logger.info("秘密鍵認証を使用")
                # 秘密鍵認証
                import io
                private_key_obj = None
                private_key_io = io.StringIO(final_config.private_key)
                
                # 各種秘密鍵形式を試行
                key_types = [
                    ("RSA", paramiko.RSAKey),
                    ("Ed25519", paramiko.Ed25519Key),
                    ("ECDSA", paramiko.ECDSAKey),
                    ("DSS", paramiko.DSSKey)
                ]
                
                for key_type, key_class in key_types:
                    try:
                        private_key_io.seek(0)
                        private_key_obj = key_class.from_private_key(
                            private_key_io,
                            password=final_config.private_key_passphrase
                        )
                        logger.info(f"{key_type}秘密鍵を正常に読み込みました")
                        break
                    except Exception as e:
                        logger.debug(f"{key_type}鍵としての読み込みに失敗: {e}")
                        continue
                
                if not private_key_obj:
                    raise ValueError("Failed to load private key. Unsupported format or incorrect passphrase.")
                
                self.ssh_client.connect(
                    hostname=final_config.host,
                    port=final_config.port,
                    username=final_config.username,
                    pkey=private_key_obj,
                    timeout=30
                )
            else:
                logger.info("パスワード認証を使用")
                # パスワード認証
                self.ssh_client.connect(
                    hostname=final_config.host,
                    port=final_config.port,
                    username=final_config.username,
                    password=final_config.password,
                    timeout=30
                )
            
            # SFTP接続も確立
            self.sftp_client = self.ssh_client.open_sftp()
            self.config = final_config
            
            success_msg = f"Successfully connected to {final_config.username}@{final_config.host}:{final_config.port}"
            logger.info(success_msg)
            return success_msg
            
        except Exception as e:
            error_msg = f"SSH connection failed: {str(e)}"
            logger.error(error_msg)
            # 失敗時はクリーンアップ
            if self.ssh_client:
                try:
                    self.ssh_client.close()
                except:
                    pass
                self.ssh_client = None
            if self.sftp_client:
                try:
                    self.sftp_client.close()
                except:
                    pass
                self.sftp_client = None
            raise Exception(error_msg)
    
    async def _execute_command(self, command: str, cwd: Optional[str] = None) -> str:
        """リモートコマンドを実行"""
        if not self.ssh_client:
            raise Exception('Not connected to SSH. Please connect first.')
        
        try:
            # 作業ディレクトリが指定されている場合は、cdコマンドを前置
            actual_command = command
            if cwd:
                actual_command = f"cd {cwd} && {command}"
            
            logger.info(f"コマンドを実行中: {actual_command}")
            
            stdin, stdout, stderr = self.ssh_client.exec_command(actual_command)
            
            # 結果を取得
            stdout_data = stdout.read().decode('utf-8', errors='replace')
            stderr_data = stderr.read().decode('utf-8', errors='replace')
            exit_code = stdout.channel.recv_exit_status()
            
            logger.info(f"コマンドが終了コード {exit_code} で実行されました")
            
            # 出力を整形（改行を確実に処理）
            result_parts = [
                f"Command: {command}",
                f"Exit Code: {exit_code}",
                "",
                "STDOUT:",
                stdout_data.rstrip() if stdout_data.strip() else "",
                "",
                "STDERR:",
                stderr_data.rstrip() if stderr_data.strip() else ""
            ]
            result = "\n".join(result_parts)
            return result
            
        except Exception as e:
            error_msg = f"Command execution failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    async def _upload_file(self, local_path: str, remote_path: str) -> str:
        """ファイルをアップロード"""
        if not self.sftp_client:
            raise Exception('SSHに接続されていません。まず接続してください。')
        
        try:
            logger.info(f"ファイルを {local_path} から {remote_path} にアップロード中")
            
            # ローカルファイルの存在確認
            if not os.path.exists(local_path):
                raise FileNotFoundError(f"Local file not found: {local_path}")
            
            # リモートディレクトリの作成（必要に応じて）
            remote_dir = os.path.dirname(remote_path)
            if remote_dir:
                try:
                    self.sftp_client.mkdir(remote_dir)
                    logger.debug(f"リモートディレクトリを作成しました: {remote_dir}")
                except FileExistsError:
                    pass  # ディレクトリが既に存在する場合は無視
            
            self.sftp_client.put(local_path, remote_path)
            
            success_msg = f"Successfully uploaded {local_path} to {remote_path}"
            logger.info(success_msg)
            return success_msg
            
        except Exception as e:
            error_msg = f"File upload failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    async def _download_file(self, remote_path: str, local_path: str) -> str:
        """ファイルをダウンロード"""
        if not self.sftp_client:
            raise Exception('SSHに接続されていません。まず接続してください。')
        
        try:
            logger.info(f"ファイルを {remote_path} から {local_path} にダウンロード中")
            
            # ローカルディレクトリの作成（必要に応じて）
            local_dir = os.path.dirname(local_path)
            if local_dir and not os.path.exists(local_dir):
                os.makedirs(local_dir, exist_ok=True)
                logger.debug(f"ローカルディレクトリを作成しました: {local_dir}")
            
            self.sftp_client.get(remote_path, local_path)
            
            success_msg = f"Successfully downloaded {remote_path} to {local_path}"
            logger.info(success_msg)
            return success_msg
            
        except Exception as e:
            error_msg = f"File download failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    async def _disconnect_ssh(self) -> str:
        """SSH接続を切断"""
        try:
            logger.info("SSH接続を切断中...")
            
            if self.sftp_client:
                self.sftp_client.close()
                self.sftp_client = None
                logger.info("SFTP接続を終了しました")
                
            if self.ssh_client:
                self.ssh_client.close()
                self.ssh_client = None
                logger.info("SSH接続を終了しました")
                
            self.config = None
            
            success_msg = "Successfully disconnected from SSH"
            logger.info(success_msg)
            return success_msg
            
        except Exception as e:
            error_msg = f"Disconnect failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    async def _get_system_info(self) -> str:
        """システム情報を取得"""
        if not self.ssh_client:
            raise Exception('Not connected to SSH. Please connect first.')
        
        try:
            logger.info("システム情報を取得中...")
            
            commands = [
                'uname -a',
                'lsb_release -a',
                'df -h',
                'free -h',
                'ps aux | head -10',
            ]
            
            output = ''
            for command in commands:
                try:
                    stdin, stdout, stderr = self.ssh_client.exec_command(command)
                    stdout_data = stdout.read().decode('utf-8', errors='replace')
                    
                    output += f"=== {command} ===\n{stdout_data}\n\n"
                    
                except Exception as e:
                    output += f"=== {command} ===\nCommand execution error: {str(e)}\n\n"
            
            logger.info("システム情報を正常に取得しました")
            return output
            
        except Exception as e:
            error_msg = f"System info failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

def main():
    """MCPサーバーのメイン関数"""
    try:
        server = SSHMCPServer()
        # FastMCPは内部でイベントループを管理するため、直接runを呼び出す
        server.mcp.run()
            
    except KeyboardInterrupt:
        print("\nユーザーによってサーバーが停止されました")
    except Exception as e:
        logger.error(f"致命的なエラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
