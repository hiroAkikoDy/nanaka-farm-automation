#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動スケジューラ - 気象データ収集を定期実行
毎週月曜日 8:00 に実行、エラー時はメール通知（オプション）
"""

import argparse
import logging
import os
import smtplib
import subprocess
import sys
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import schedule

# Windows環境でのUTF-8出力設定
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# ディレクトリ設定
BASE_DIR = Path(__file__).parent.parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# ロガー設定
LOG_FILE = LOGS_DIR / "scheduler.log"
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class EmailNotifier:
    """メール通知クラス（エラー時に送信）"""

    def __init__(self, smtp_server, smtp_port, sender_email, sender_password, recipient_email):
        """
        Args:
            smtp_server: SMTPサーバー（例: smtp.gmail.com）
            smtp_port: SMTPポート（例: 587）
            sender_email: 送信元メールアドレス
            sender_password: 送信元パスワード
            recipient_email: 送信先メールアドレス
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipient_email = recipient_email
        self.enabled = all([smtp_server, smtp_port, sender_email, sender_password, recipient_email])

    def send_error_notification(self, error_message, log_snippet=""):
        """
        エラー通知メールを送信

        Args:
            error_message: エラーメッセージ
            log_snippet: ログの抜粋
        """
        if not self.enabled:
            logger.warning("メール通知が設定されていません。スキップします。")
            return False

        try:
            # メール作成
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = f"[Nanaka Farm] 気象データ収集エラー - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

            body = f"""
気象データ収集処理でエラーが発生しました。

エラー内容:
{error_message}

ログ抜粋:
{log_snippet}

詳細はログファイルを確認してください:
{LOG_FILE}

--
Nanaka Farm 自動化システム
            """

            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            # SMTP接続してメール送信
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)

            logger.info(f"エラー通知メール送信成功: {self.recipient_email}")
            return True

        except Exception as e:
            logger.error(f"メール送信失敗: {e}")
            return False


class WeatherDataScheduler:
    """気象データ収集スケジューラー"""

    def __init__(self, lat=32.8032, lon=130.7075, days=7, use_mock=False, email_notifier=None):
        """
        Args:
            lat: 緯度
            lon: 経度
            days: 過去何日分
            use_mock: モックモード
            email_notifier: メール通知インスタンス
        """
        self.lat = lat
        self.lon = lon
        self.days = days
        self.use_mock = use_mock
        self.email_notifier = email_notifier
        self.workflow_script = BASE_DIR / "scripts" / "collect_and_save_workflow.py"

    def run_collection_workflow(self):
        """気象データ収集ワークフローを実行"""
        logger.info("=" * 70)
        logger.info("気象データ収集開始（スケジュール実行）")
        logger.info("=" * 70)
        logger.info(f"座標: ({self.lat}, {self.lon})")
        logger.info(f"期間: 過去{self.days}日")
        logger.info(f"モード: {'モック' if self.use_mock else '実API'}")

        try:
            # コマンド構築
            command = [
                "python",
                str(self.workflow_script),
                "--lat", str(self.lat),
                "--lon", str(self.lon),
                "--days", str(self.days)
            ]

            if self.use_mock:
                command.append("--mock")

            # ワークフロー実行
            logger.info(f"実行コマンド: {' '.join(command)}")
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                cwd=BASE_DIR
            )

            # 結果確認
            if result.returncode == 0:
                logger.info("✓ 気象データ収集完了")
                logger.info(f"標準出力:\n{result.stdout}")
                return True
            else:
                error_message = f"気象データ収集失敗（終了コード: {result.returncode}）"
                logger.error(error_message)
                logger.error(f"標準エラー出力:\n{result.stderr}")

                # エラー通知送信
                if self.email_notifier:
                    log_snippet = result.stderr[:500] if result.stderr else "エラー詳細なし"
                    self.email_notifier.send_error_notification(error_message, log_snippet)

                return False

        except Exception as e:
            error_message = f"ワークフロー実行中に例外発生: {e}"
            logger.error(error_message, exc_info=True)

            # エラー通知送信
            if self.email_notifier:
                self.email_notifier.send_error_notification(error_message, str(e))

            return False

    def schedule_weekly(self):
        """毎週月曜日 8:00 にスケジュール"""
        schedule.every().monday.at("08:00").do(self.run_collection_workflow)
        logger.info("✓ スケジュール設定完了: 毎週月曜日 8:00")

    def run_immediately(self):
        """即座に実行（テスト用）"""
        logger.info("即座に実行（テストモード）")
        return self.run_collection_workflow()


def main():
    parser = argparse.ArgumentParser(
        description="気象データ収集スケジューラー - 毎週月曜日 8:00 に自動実行"
    )
    parser.add_argument("--lat", type=float, default=32.8032, help="緯度")
    parser.add_argument("--lon", type=float, default=130.7075, help="経度")
    parser.add_argument("--days", type=int, default=7, help="過去何日分")
    parser.add_argument("--mock", action="store_true", help="モックモード")
    parser.add_argument("--test", action="store_true", help="即座にテスト実行")

    # メール通知設定（環境変数から読み込み）
    parser.add_argument(
        "--smtp-server",
        default=os.getenv("SMTP_SERVER", ""),
        help="SMTPサーバー（例: smtp.gmail.com）"
    )
    parser.add_argument(
        "--smtp-port",
        type=int,
        default=int(os.getenv("SMTP_PORT", "587")),
        help="SMTPポート"
    )
    parser.add_argument(
        "--sender-email",
        default=os.getenv("SENDER_EMAIL", ""),
        help="送信元メールアドレス"
    )
    parser.add_argument(
        "--sender-password",
        default=os.getenv("SENDER_PASSWORD", ""),
        help="送信元メールパスワード"
    )
    parser.add_argument(
        "--recipient-email",
        default=os.getenv("RECIPIENT_EMAIL", ""),
        help="送信先メールアドレス"
    )

    args = parser.parse_args()

    logger.info("=" * 70)
    logger.info("Nanaka Farm 気象データ収集スケジューラー")
    logger.info("=" * 70)

    # メール通知設定
    email_notifier = None
    if args.smtp_server and args.sender_email and args.recipient_email:
        email_notifier = EmailNotifier(
            args.smtp_server,
            args.smtp_port,
            args.sender_email,
            args.sender_password,
            args.recipient_email
        )
        logger.info(f"✓ メール通知有効: {args.recipient_email}")
    else:
        logger.info("⚠️  メール通知無効（環境変数未設定）")

    # スケジューラー初期化
    scheduler = WeatherDataScheduler(
        lat=args.lat,
        lon=args.lon,
        days=args.days,
        use_mock=args.mock,
        email_notifier=email_notifier
    )

    # テストモード
    if args.test:
        logger.info("テストモードで即座に実行します...")
        success = scheduler.run_immediately()
        sys.exit(0 if success else 1)

    # 定期実行モード
    scheduler.schedule_weekly()

    logger.info("スケジューラー起動中... (Ctrl+C で停止)")
    logger.info(f"次回実行予定: {schedule.next_run()}")

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1分ごとにチェック

            # 次回実行予定をログ出力（1時間ごと）
            if datetime.now().minute == 0:
                logger.info(f"スケジューラー稼働中 | 次回実行: {schedule.next_run()}")

    except KeyboardInterrupt:
        logger.info("\nスケジューラーを停止します")
        sys.exit(0)


if __name__ == "__main__":
    main()
