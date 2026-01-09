# 🌾 Nanaka Farm Automation System

> 衛星データ × グラフDB × AI で実現する次世代農業データ管理システム

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.x-008CC1.svg)](https://neo4j.com/)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000.svg)](https://flask.palletsprojects.com/)

---

## 📖 プロジェクト概要

**Nanaka Farm Automation System** は、JAXA衛星データを活用した次世代農業管理プラットフォームです。GCOM-C「しきさい」の観測データ（地表面温度・植生指標）をグラフデータベースで統合管理し、リアルタイムダッシュボードで可視化します。週次自動実行により、農園の健康状態を継続的にモニタリングできます。

**対象ユーザー**: 農園経営者、農業IoT開発者、衛星データ分析研究者

---

## ✨ 主要機能

- 📡 **JAXA衛星データ自動収集** - GCOM-C/SGLIからLST・NDVIデータを自動取得
- 🗄️ **Neo4jグラフDB統合管理** - 農園と観測データを関係性で管理
- 📊 **リアルタイムダッシュボード** - Chart.js + Leaflet.jsによる可視化
- 🔍 **異常検出アルゴリズム** - Z-scoreベースの植生異常アラート
- ⏰ **週次自動実行** - スケジューラーによる無人運用
- 🌍 **GeoJSON/QGIS連携** - 地理空間データのエクスポート機能

---

## 🎬 デモ

### ダッシュボード画面
![Dashboard Screenshot](docs/images/dashboard-preview.png)
*リアルタイムNDVIトレンド、圃場マップ、作業時間分析を一画面で表示*

### 実行例
```bash
# データ収集 → 分析 → ダッシュボード表示まで
$ python scripts/collect_and_save_workflow.py --mock
✓ JAXA APIからデータ取得完了
✓ Neo4jに38件の観測データを保存
✓ ダッシュボード起動: http://localhost:5000
```

---

## 🏗️ アーキテクチャ

```
┌─────────────────────┐
│ JAXA G-Portal API   │  (GCOM-C/SGLI衛星データ)
└──────────┬──────────┘
           │ HDF5 Download
           ▼
┌─────────────────────┐
│ HDF5/GeoTIFF Parser │  (LST, NDVI抽出)
└──────────┬──────────┘
           │ JSON
           ▼
┌─────────────────────┐     ┌──────────────────┐
│  Neo4j Graph DB     │◄────┤  Flask REST API  │
│  (Farm + Satellite) │     │  (5 Endpoints)   │
└──────────┬──────────┘     └────────┬─────────┘
           │                         │
           ▼                         ▼
┌─────────────────────┐     ┌──────────────────┐
│   Scheduler         │     │ Chart.js         │
│   (週次自動実行)     │     │ Dashboard        │
└─────────────────────┘     └──────────────────┘
```

---

## 🚀 クイックスタート

### 前提条件
- Python 3.11以上
- Neo4j 5.x（起動済み）
- 8GB RAM推奨
- OS: Windows 10/11, macOS, Linux

### インストール（3ステップ）

```bash
# 1. リポジトリのクローン
git clone https://github.com/hiroAkikoDy/nanaka-farm-automation.git
cd nanaka-farm-automation

# 2. 依存パッケージのインストール
pip install -r requirements.txt

# 3. 環境変数の設定
cp .env.example .env
# .env ファイルを編集してJAXA G-PortalとNeo4j認証情報を入力
```

### 初回実行

```bash
# テストモードで動作確認（モックデータ使用）
python scripts/collect_and_save_workflow.py --mock

# APIサーバー起動
python scripts/api_server.py

# ダッシュボードを開く
start dashboard/index.html  # Windows
open dashboard/index.html   # macOS
```

ブラウザで `dashboard/index.html` を開くと、NDVIトレンドグラフと圃場マップが表示されます。

---

## 📋 詳細なインストール

### 1. Python環境セットアップ

```bash
# Python 3.11+ を確認
python --version  # Python 3.11.x 以上

# 仮想環境の作成（推奨）
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### 2. Neo4jインストール

**Neo4j Desktop使用（推奨）**:
1. [Neo4j Desktop](https://neo4j.com/download/) をダウンロード
2. 新規データベース作成
3. ユーザー: `neo4j`、パスワード: 任意（`.env`に設定）
4. データベースを起動

**Dockerを使用する場合**:
```bash
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password \
  neo4j:5-community
```

### 3. 環境変数の設定

`.env` ファイルを作成:

```bash
# JAXA G-Portal認証情報
GPORTAL_USERNAME=your_username
GPORTAL_PASSWORD=your_password

# Neo4j接続情報
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password

# メール通知（オプション）
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
RECIPIENT_EMAIL=admin@example.com
```

**JAXA G-Portalアカウント登録**: https://gportal.jaxa.jp/

### 4. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

主な依存パッケージ:
- `neo4j` - Neo4jドライバー
- `flask`, `flask-cors` - REST APIサーバー
- `h5py`, `numpy` - HDF5データ処理
- `matplotlib` - データ可視化
- `schedule` - 定期実行スケジューラー

---

## 💡 使用例

### 基本的なワークフロー

```bash
# 1. データ収集（JAXA G-Portal API）
python scripts/jaxa_api_client.py \
  --lat 32.8032 --lon 130.7075 \
  --product LST --download

python scripts/jaxa_api_client.py \
  --lat 32.8032 --lon 130.7075 \
  --product NDVI --download

# 2. HDF5データ解析
python scripts/geotiff_processor.py \
  data/geotiff/GC1SG1_20260108_LST.h5 \
  --lat 32.8032 --lon 130.7075 \
  --dataset LST --viz

# 3. Neo4jに保存
python scripts/save_weather.py \
  --date 2026-01-08 \
  --temperature 18.5 \
  --humidity 68.0 \
  --ndvi-avg 0.75

# 4. データ確認
python scripts/query_data.py

# 5. GeoJSONエクスポート（QGIS用）
python scripts/export_geojson.py
```

### 統合ワークフロー（推奨）

```bash
# 全処理を一括実行
python scripts/collect_and_save_workflow.py --mock

# 実APIモード（JAXA G-Portal認証が必要）
export GPORTAL_USERNAME="your_username"
export GPORTAL_PASSWORD="your_password"
python scripts/collect_and_save_workflow.py
```

### ダッシュボードの起動

```bash
# ターミナル1: APIサーバー起動
python scripts/api_server.py

# ターミナル2: ブラウザでダッシュボードを開く
start dashboard/index.html  # Windows
open dashboard/index.html   # macOS
xdg-open dashboard/index.html  # Linux
```

ダッシュボードURL: `file:///path/to/dashboard/index.html`

### 週次自動実行

```bash
# バックグラウンドで定期実行（毎週月曜 8:00）
nohup python scripts/scheduler.py > logs/scheduler.log 2>&1 &

# テストモード（即座に1回実行）
python scripts/scheduler.py --test --mock
```

---

## 📁 プロジェクト構造

```
nanaka-farm-automation/
├── .claude/
│   ├── commands/           # カスタムコマンド
│   │   ├── hello-farm.md
│   │   └── collect-weather-data.md
│   └── hooks/              # Git フック
│       └── afterCodeChange.ts
├── dashboard/
│   └── index.html          # Chart.js ダッシュボード (575行)
├── data/
│   ├── geotiff/            # HDF5/GeoTIFFファイル
│   ├── metadata/           # メタデータJSON
│   └── visualizations/     # 生成されたグラフ
├── docs/
│   ├── DASHBOARD_TESTING.md
│   ├── GPORTAL_REAL_API_SETUP.md
│   ├── QGIS_VISUALIZATION.md
│   └── SCHEDULER.md
├── exports/
│   ├── nanaka_farm_fields.geojson
│   └── satellite_observations.geojson
├── queries/
│   ├── test.cypher
│   └── visualization/      # Neo4j可視化クエリ (5ファイル)
│       ├── 01_farm_overview.cypher
│       ├── 02_temporal_data.cypher
│       ├── 03_work_density.cypher
│       ├── 04_seasonal_pattern.cypher
│       └── 05_anomaly_detection.cypher
├── scripts/
│   ├── api_server.py       # Flask REST API (269行)
│   ├── collect_and_save_workflow.py
│   ├── export_geojson.py   # GeoJSONエクスポート (315行)
│   ├── farm_info.py
│   ├── geotiff_processor.py
│   ├── jaxa_api_client.py
│   ├── query_data.py
│   ├── save_weather.py
│   └── scheduler.py        # スケジューラー
├── tests/                  # テストファイル
│   └── test_api.py
├── .env                    # 環境変数（.gitignoreで除外）
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── QUICKSTART.md
├── README.md
├── requirements.txt
└── TEST_REPORT.md
```

---

## 🧪 テスト

```bash
# 全テスト実行
pytest tests/ -v

# カバレッジ測定
pytest tests/ --cov=scripts --cov-report=html

# 特定のテストのみ実行
pytest tests/test_api.py -k "test_health_check"
```

---

## 🔧 API仕様

Flask REST APIは5つのエンドポイントを提供します:

### `GET /api/health`
ヘルスチェック

**レスポンス例**:
```json
{
  "status": "healthy",
  "neo4j": "connected",
  "timestamp": "2026-01-09T12:00:00"
}
```

### `GET /api/summary`
サマリー情報

**レスポンス例**:
```json
{
  "totalFields": 1,
  "totalArea": 10000,
  "monthlyWorkHours": 120,
  "avgNDVI": 0.752
}
```

### `GET /api/ndvi-trend?days=7`
NDVI時系列データ

**パラメータ**:
- `days` (int, optional): 取得日数（デフォルト: 7）

**レスポンス例**:
```json
[
  {"date": "01/01", "ndvi": 0.68},
  {"date": "01/02", "ndvi": 0.71}
]
```

### `GET /api/work-hours`
圃場別作業時間

**レスポンス例**:
```json
[
  {"field": "圃場A", "hours": 35},
  {"field": "圃場B", "hours": 28}
]
```

### `GET /api/fields`
圃場位置情報とNDVI状態

**レスポンス例**:
```json
[
  {
    "id": 1,
    "name": "Nanaka Farm",
    "lat": 32.8032,
    "lon": 130.7075,
    "area": 10000,
    "ndvi": 0.752,
    "status": "healthy"
  }
]
```

詳細は [QUICKSTART.md](QUICKSTART.md) を参照してください。

---

## 📊 データモデル

### Neo4jグラフ構造

```cypher
// 農園ノード
(f:Farm {
  name: "Nanaka Farm",
  latitude: 32.8032,
  longitude: 130.7075,
  area: 10000
})

// 衛星観測データノード
(s:SatelliteData {
  date: date("2026-01-08"),
  temperature: 18.5,
  humidity: 68.0,
  ndvi_avg: 0.752,
  created_at: datetime()
})

// リレーション
(f)-[:HAS_OBSERVATION]->(s)
```

### サンプルクエリ

```cypher
// 最新7日間の平均NDVI
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
WHERE s.date >= date() - duration('P7D')
RETURN AVG(s.ndvi_avg) AS avgNDVI;

// 異常値検出（Z-score > 2.0）
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
WITH AVG(s.ndvi_avg) AS mean, stdev(s.ndvi_avg) AS stddev
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
WITH s, abs(s.ndvi_avg - mean) / stddev AS zscore
WHERE zscore > 2.0
RETURN s.date, s.ndvi_avg, zscore
ORDER BY zscore DESC;
```

詳細は [queries/visualization/README.md](queries/visualization/README.md) を参照してください。

---

## 🤝 コントリビューション

コントリビューションを歓迎します！バグ報告、機能要望、プルリクエストをお待ちしています。

詳細は [CONTRIBUTING.md](CONTRIBUTING.md) をご覧ください。

### 開発フロー

1. このリポジトリをFork
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'feat: Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

### コーディング規約

- PEP 8準拠
- Black フォーマッター使用
- docstring必須（Google形式）
- テストカバレッジ80%以上

---

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は [LICENSE](LICENSE) を参照してください。

---

## 👤 作者

**古閑 弘晃 (Hiroaki Koga)**

- GitHub: [@hiroAkikoDy](https://github.com/hiroAkikoDy)
- プロジェクト: [Nanaka Farm Automation](https://github.com/hiroAkikoDy/nanaka-farm-automation)

---

## 🙏 謝辞

このプロジェクトは以下の素晴らしいツール・サービスを使用しています:

- **JAXA G-Portal** - 衛星データ提供
- **Neo4j** - グラフデータベース
- **Flask** - REST APIフレームワーク
- **Chart.js** - データ可視化ライブラリ
- **Leaflet.js** - 地図表示ライブラリ
- **Claude by Anthropic** - AIアシスタント（開発支援）

---

## 📚 関連ドキュメント

- [QUICKSTART.md](QUICKSTART.md) - 3ステップ起動ガイド
- [TEST_REPORT.md](TEST_REPORT.md) - 統合テストレポート
- [CHANGELOG.md](CHANGELOG.md) - 変更履歴
- [docs/DASHBOARD_TESTING.md](docs/DASHBOARD_TESTING.md) - ダッシュボードテストガイド
- [docs/QGIS_VISUALIZATION.md](docs/QGIS_VISUALIZATION.md) - QGIS可視化ガイド
- [docs/SCHEDULER.md](docs/SCHEDULER.md) - スケジューラー詳細

---

## 🔗 リンク

- [JAXA G-Portal](https://gportal.jaxa.jp/) - 衛星データポータル
- [Neo4j Documentation](https://neo4j.com/docs/) - Neo4j公式ドキュメント
- [GCOM-C/SGLI](https://suzaku.eorc.jaxa.jp/GCOM_C/index_j.html) - 衛星「しきさい」

---

<p align="center">
  🌾 Generated with <a href="https://claude.com/claude-code">Claude Code</a>
</p>
