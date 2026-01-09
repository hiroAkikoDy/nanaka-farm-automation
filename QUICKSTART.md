# 🚀 Nanaka Farm Dashboard クイックスタート

Flask API + Chart.js Dashboard の起動・テスト手順（最速3ステップ）

---

## 📋 前提条件

- ✅ Python 3.11以上
- ✅ Neo4j Desktop（起動済み）
- ✅ Flask / flask-cors インストール済み
- ✅ モダンブラウザ（Chrome, Firefox, Edge等）

---

## ⚡ 3ステップで起動

### ステップ1: Neo4jを起動

Neo4j Desktopでデータベースを起動してください。

### ステップ2: Flask APIサーバーを起動

```bash
cd "C:\Users\Koga Hiroaki\Desktop\hiroaki_\workingFolder\nanaka-farm-automation"
python scripts/api_server.py
```

**起動成功の表示:**
```
============================================================
🚀 Nanaka Farm API Server Starting...
============================================================
📡 API Server: http://localhost:5000
 * Running on http://127.0.0.1:5000
```

> ⚠️ このターミナルは閉じないでください！

### ステップ3: Dashboardを開く

```bash
start dashboard\index.html
```

または、`dashboard\index.html` をダブルクリック

---

## ✅ 動作確認

### ブラウザで確認

1. **ページが開いたら:**
   - ヘッダー: "🌾 Nanaka Farm Dashboard"
   - タイムスタンプが1秒ごとに更新

2. **成功メッセージを確認:**
   - ✅ **緑色**: "API接続成功！Neo4jからリアルタイムデータを取得中"
     → API経由でNeo4jデータを取得

   - ⚠️ **オレンジ色**: "API接続失敗 - モックデータを表示中"
     → APIサーバーが起動していない（モックデータで動作）

3. **表示内容:**
   - サマリーカード（4つ）: 圃場数、面積、作業時間、NDVI
   - NDVIグラフ: 緑色の折れ線グラフ
   - 作業時間グラフ: カラフルな棒グラフ
   - 地図: Nanaka Farmの位置にマーカー

### ブラウザの開発者ツールで確認

**F12** を押して開発者ツールを開き、**Console** タブを確認:

```
🚀 Dashboard initializing...
📊 Data sources: {summary: 'api', ndviTrend: 'api', workHours: 'api', fields: 'api'}
✅ Dashboard loaded successfully
```

---

## 🔄 自動更新機能

- **60秒ごと**に自動的にAPIからデータを再取得
- Consoleに `🔄 Refreshing dashboard data...` が表示される

---

## 🐛 トラブルシューティング

### 問題: オレンジ色の警告メッセージ

**表示:** "⚠️ API接続失敗 - モックデータを表示中"

**解決:** Flask APIサーバーを起動してください
```bash
python scripts/api_server.py
```

### 問題: Neo4j接続エラー

**解決:** Neo4j Desktopでデータベースを起動

---

## 📚 詳細ドキュメント

- **docs/DASHBOARD_TESTING.md** - 完全なテストガイド
- **scripts/api_server.py** - Flask APIサーバー
- **dashboard/index.html** - Chart.js Dashboard

---

## 旧版: データ収集システムのセットアップ

### 前提条件

- Python 3.x
- Neo4j データベース（起動済み）

## 1. インストール（5分）

```bash
# すべての依存パッケージをインストール
pip install neo4j h5py numpy matplotlib schedule

# オプション: JAXA G-Portal APIクライアント（実API使用時）
pip install gportal
```

## 2. 環境変数設定（2分）

```bash
# Neo4j認証情報
export NEO4J_PASSWORD="nAnAkA0629"

# JAXA G-Portal認証情報（実API使用時のみ）
export GPORTAL_USERNAME="your_username"
export GPORTAL_PASSWORD="your_password"

# メール通知（オプション）
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SENDER_EMAIL="your-email@gmail.com"
export SENDER_PASSWORD="your-app-password"
export RECIPIENT_EMAIL="admin@example.com"
```

**Windows (PowerShell):**
```powershell
$env:NEO4J_PASSWORD="nAnAkA0629"
$env:GPORTAL_USERNAME="your_username"
$env:GPORTAL_PASSWORD="your_password"
```

## 3. テスト実行（3分）

### 即座にテスト実行

```bash
# スケジューラーをテストモードで実行（モックデータ使用）
python scripts/scheduler.py --test --mock
```

このコマンドは以下を自動的に実行します:
1. モックデータ取得（JAXA G-Portal API）
2. HDF5ファイル処理（6ファイル）
3. 統計値抽出（NDVI、LST）
4. Neo4j保存
5. サマリーレポート生成

**実行時間:** 約25秒

**出力:**
- `logs/scheduler.log` - スケジューラーログ
- `logs/collect_weather_YYYYMMDD_HHMMSS.log` - 実行ログ
- `reports/summary_YYYYMMDD_HHMMSS.json` - サマリーレポート

## 4. 結果確認（1分）

```bash
# 保存されたデータを確認
python scripts/query_data.py
```

**期待される出力:**
```
📊 Nanaka Farm 観測データ:
======================================================================

観測 #1:
  農園名: Nanaka Farm
  日付: 2026-01-08
  温度: 18.4℃
  湿度: 65.0%
  NDVI平均: 0.725

合計: 6 件のデータ
======================================================================
```

## 5. 定期実行設定（2分）

### 毎週月曜日 8:00 に自動実行

```bash
# モックモードで起動（テスト用）
python scripts/scheduler.py --mock
```

スケジューラーが起動し、次回実行予定が表示されます:
```
[INFO] スケジューラー起動中... (Ctrl+C で停止)
[INFO] 次回実行予定: 2026-01-13 08:00:00
```

### バックグラウンド実行

**Linux/Mac:**
```bash
nohup python scripts/scheduler.py --mock > logs/scheduler_nohup.log 2>&1 &
```

**Windows:**
タスクスケジューラーで設定（詳細は [docs/SCHEDULER.md](docs/SCHEDULER.md) 参照）

## 実API使用への切り替え

モックモードでテストが成功したら、実APIに切り替えます:

```bash
# 環境変数を設定（上記参照）
export GPORTAL_USERNAME="your_username"
export GPORTAL_PASSWORD="your_password"

# --mockフラグを外して実行
python scripts/scheduler.py --test
```

## トラブルシューティング

### Neo4j接続エラー

```
Neo4jに接続できません
```

**解決方法:**
```bash
# Neo4jサービス起動確認
systemctl status neo4j  # Linux
# または
neo4j console  # 手動起動
```

### schedule モジュールがない

```
ModuleNotFoundError: No module named 'schedule'
```

**解決方法:**
```bash
pip install schedule
```

### 文字化け（Windows）

```bash
chcp 65001
python scripts/scheduler.py --test --mock
```

## コマンド一覧

| コマンド | 説明 | 実行時間 |
|---------|------|---------|
| `python scripts/scheduler.py --test --mock` | テスト実行（モック） | ~25秒 |
| `python scripts/scheduler.py --test` | テスト実行（実API） | ~3分 |
| `python scripts/scheduler.py --mock` | 定期実行（モック） | - |
| `python scripts/scheduler.py` | 定期実行（実API） | - |
| `python scripts/query_data.py` | データ確認 | <1秒 |
| `python scripts/farm_info.py` | 農園情報 | <1秒 |

## 次のステップ

1. **メール通知を設定**
   - Gmailアプリパスワードを取得
   - 環境変数を設定
   - 詳細: [docs/SCHEDULER.md](docs/SCHEDULER.md)

2. **systemd/タスクスケジューラーで自動起動**
   - システム起動時に自動実行
   - 詳細: [docs/SCHEDULER.md](docs/SCHEDULER.md)

3. **実APIに切り替え**
   - JAXA G-Portal認証情報を取得
   - モックモードから実APIモードへ
   - 詳細: [docs/JAXA_GPORTAL_API.md](docs/JAXA_GPORTAL_API.md)

## 参考資料

- [README.md](README.md) - 完全なドキュメント
- [docs/SCHEDULER.md](docs/SCHEDULER.md) - スケジューラー詳細
- [docs/JAXA_GPORTAL_API.md](docs/JAXA_GPORTAL_API.md) - API使用ガイド
- [.claude/commands/collect-weather-data.md](.claude/commands/collect-weather-data.md) - ワークフロー詳細
