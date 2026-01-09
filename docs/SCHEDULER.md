# 気象データ収集スケジューラー

`scripts/scheduler.py` は気象データ収集を自動化するPythonスケジューラーです。

## 機能

- 毎週月曜日 8:00 に自動実行
- エラー時のメール通知（オプション）
- 包括的なログ記録
- テストモードでの即座実行

## インストール

scheduleライブラリをインストール:

```bash
pip install schedule
```

## 基本的な使用方法

### 1. テスト実行（即座に実行）

```bash
python scripts/scheduler.py --test --mock
```

テストモードでは即座に1回だけ実行されます。

### 2. 定期実行モード

```bash
python scripts/scheduler.py --mock
```

このコマンドでスケジューラーが起動し、毎週月曜日 8:00 に自動実行されます。
Ctrl+C で停止します。

### 3. 実APIモード

```bash
# JAXA G-Portal認証情報を設定
export GPORTAL_USERNAME="your_username"
export GPORTAL_PASSWORD="your_password"

# スケジューラー起動（実API使用）
python scripts/scheduler.py
```

## コマンドラインオプション

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `--lat` | 緯度 | 32.8032 |
| `--lon` | 経度 | 130.7075 |
| `--days` | 過去何日分 | 7 |
| `--mock` | モックモード | False |
| `--test` | 即座にテスト実行 | False |
| `--smtp-server` | SMTPサーバー | 環境変数 SMTP_SERVER |
| `--smtp-port` | SMTPポート | 環境変数 SMTP_PORT (587) |
| `--sender-email` | 送信元メールアドレス | 環境変数 SENDER_EMAIL |
| `--sender-password` | 送信元メールパスワード | 環境変数 SENDER_PASSWORD |
| `--recipient-email` | 送信先メールアドレス | 環境変数 RECIPIENT_EMAIL |

## メール通知設定

エラー発生時に自動でメール通知を送信します。

### 環境変数で設定（推奨）

```bash
# Linux/Mac
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SENDER_EMAIL="your-email@gmail.com"
export SENDER_PASSWORD="your-app-password"
export RECIPIENT_EMAIL="admin@example.com"

# Windows (PowerShell)
$env:SMTP_SERVER="smtp.gmail.com"
$env:SMTP_PORT="587"
$env:SENDER_EMAIL="your-email@gmail.com"
$env:SENDER_PASSWORD="your-app-password"
$env:RECIPIENT_EMAIL="admin@example.com"
```

### コマンドラインで設定

```bash
python scripts/scheduler.py \
  --smtp-server smtp.gmail.com \
  --smtp-port 587 \
  --sender-email your-email@gmail.com \
  --sender-password your-app-password \
  --recipient-email admin@example.com
```

### Gmail設定例

Gmailを使用する場合、アプリパスワードが必要です:

1. Googleアカウントにログイン
2. セキュリティ設定 → 2段階認証を有効化
3. アプリパスワードを生成
4. 生成されたパスワードを `SENDER_PASSWORD` に設定

**注意**: 通常のGmailパスワードは使用できません。必ずアプリパスワードを使用してください。

## ログ

### ログファイル

- `logs/scheduler.log` - スケジューラーの実行ログ
- `logs/collect_weather_YYYYMMDD_HHMMSS.log` - 各実行の詳細ログ
- `logs/errors_YYYYMMDD_HHMMSS.log` - エラーログ

### ログ確認

```bash
# 最新のログを表示
tail -f logs/scheduler.log

# エラーログのみ表示
cat logs/errors_*.log
```

## バックグラウンド実行

### Linux/Mac

```bash
# nohupで実行
nohup python scripts/scheduler.py --mock > logs/scheduler_nohup.log 2>&1 &

# systemdで実行（推奨）
# /etc/systemd/system/nanaka-farm-scheduler.service を作成
```

#### systemd設定例

`/etc/systemd/system/nanaka-farm-scheduler.service`:

```ini
[Unit]
Description=Nanaka Farm Weather Data Collection Scheduler
After=network.target neo4j.service

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/nanaka-farm-automation
Environment="GPORTAL_USERNAME=your_username"
Environment="GPORTAL_PASSWORD=your_password"
ExecStart=/usr/bin/python3 scripts/scheduler.py
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

サービス管理:

```bash
# サービス有効化・起動
sudo systemctl enable nanaka-farm-scheduler
sudo systemctl start nanaka-farm-scheduler

# ステータス確認
sudo systemctl status nanaka-farm-scheduler

# ログ確認
journalctl -u nanaka-farm-scheduler -f
```

### Windows

#### 方法1: タスクスケジューラー（推奨）

1. タスクスケジューラーを開く
2. 「基本タスクの作成」を選択
3. 名前: `Nanaka Farm Scheduler`
4. トリガー: システム起動時
5. 操作: プログラムの開始
   - プログラム: `C:\Python\python.exe`
   - 引数: `scripts\scheduler.py --mock`
   - 開始: `C:\path\to\nanaka-farm-automation`
6. 「ユーザーがログオンしているかどうかにかかわらず実行する」を選択

#### 方法2: バッチファイル + スタートアップ

`start_scheduler.bat`:

```batch
@echo off
cd /d C:\path\to\nanaka-farm-automation
python scripts\scheduler.py --mock > logs\scheduler_startup.log 2>&1
```

スタートアップフォルダに配置:
`C:\Users\YourName\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup`

## トラブルシューティング

### スケジューラーが起動しない

```
ModuleNotFoundError: No module named 'schedule'
```

**解決方法**:
```bash
pip install schedule
```

### メール送信失敗

```
エラー: メール送信失敗: (535, b'5.7.8 Username and Password not accepted')
```

**解決方法**:
- Gmailの場合、アプリパスワードを使用
- 2段階認証が有効になっているか確認
- 環境変数が正しく設定されているか確認

### Neo4j接続エラー

```
エラー: Neo4j保存失敗: Unable to connect to neo4j://localhost:7687
```

**解決方法**:
```bash
# Neo4jサービス確認
systemctl status neo4j  # Linux
# または
neo4j console  # 手動起動
```

### JAXA API認証エラー

```
エラー: G-Portal認証情報が設定されていません
```

**解決方法**:
```bash
export GPORTAL_USERNAME="your_username"
export GPORTAL_PASSWORD="your_password"
```

## 実行例

### テスト実行

```bash
$ python scripts/scheduler.py --test --mock
[2026-01-08 23:42:50,964] [INFO] ======================================================================
[2026-01-08 23:42:50,964] [INFO] Nanaka Farm 気象データ収集スケジューラー
[2026-01-08 23:42:50,965] [INFO] ======================================================================
[2026-01-08 23:42:50,965] [INFO] ⚠️  メール通知無効（環境変数未設定）
[2026-01-08 23:42:50,965] [INFO] テストモードで即座に実行します...
[2026-01-08 23:42:50,965] [INFO] 即座に実行（テストモード）
[2026-01-08 23:42:50,965] [INFO] ======================================================================
[2026-01-08 23:42:50,965] [INFO] 気象データ収集開始（スケジュール実行）
[2026-01-08 23:42:50,965] [INFO] ======================================================================
[2026-01-08 23:42:50,966] [INFO] 座標: (32.8032, 130.7075)
[2026-01-08 23:42:50,966] [INFO] 期間: 過去7日
[2026-01-08 23:42:50,966] [INFO] モード: モック
[2026-01-08 23:43:16,485] [INFO] ✓ 気象データ収集完了
```

### 定期実行モード

```bash
$ python scripts/scheduler.py --mock
[2026-01-08 23:45:00,000] [INFO] ======================================================================
[2026-01-08 23:45:00,000] [INFO] Nanaka Farm 気象データ収集スケジューラー
[2026-01-08 23:45:00,000] [INFO] ======================================================================
[2026-01-08 23:45:00,001] [INFO] ⚠️  メール通知無効（環境変数未設定）
[2026-01-08 23:45:00,001] [INFO] ✓ スケジュール設定完了: 毎週月曜日 8:00
[2026-01-08 23:45:00,001] [INFO] スケジューラー起動中... (Ctrl+C で停止)
[2026-01-08 23:45:00,001] [INFO] 次回実行予定: 2026-01-13 08:00:00
```

## 出力ファイル

スケジューラー実行時に以下のファイルが生成されます:

- `logs/scheduler.log` - スケジューラーログ
- `logs/collect_weather_YYYYMMDD_HHMMSS.log` - 実行ログ
- `logs/errors_YYYYMMDD_HHMMSS.log` - エラーログ
- `reports/summary_YYYYMMDD_HHMMSS.json` - サマリーレポート

## 参考資料

- [完全ワークフローガイド](../.claude/commands/collect-weather-data.md)
- [JAXA G-Portal API使用ガイド](./JAXA_GPORTAL_API.md)
- [schedule ライブラリドキュメント](https://schedule.readthedocs.io/)

## 注意事項

- スケジューラーはデーモンとして実行されるため、システム起動時に自動起動する設定が推奨されます
- メール通知を有効にする場合、認証情報を安全に管理してください
- ログファイルは定期的にクリーンアップしてください（logrotate等を使用）
- 実APIモードに切り替える前に、必ずモックモードでテストしてください
