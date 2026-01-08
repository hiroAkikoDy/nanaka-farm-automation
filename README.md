# Nanaka Farm Automation

Nanaka Farm の農園管理自動化システム。Neo4jデータベースを使用して農園情報と衛星観測データを管理します。

## 概要

このプロジェクトは、Nanaka Farm（熊本県、座標: 32.8032°N, 130.7075°E）の農園情報と衛星観測データ（温度、湿度、NDVI）を管理するためのツール群です。

## 必要な環境

- Python 3.x
- Neo4j データベース
- neo4j Pythonドライバー

## セットアップ

### 1. 依存パッケージのインストール

```bash
# Neo4j ドライバー
pip install neo4j --break-system-packages

# JAXA G-Portal APIクライアント（オプション）
pip install gportal
```

### 2. Neo4j データベース

- URI: `bolt://localhost:7687`
- ユーザー名: `neo4j`
- パスワード: 環境変数 `NEO4J_PASSWORD` に設定（デフォルト: `nAnAkA0629`）

## 機能

### 1. JAXA G-Portalからの衛星データ取得（最新）

**スクリプト:** `scripts/jaxa_api_client.py`

JAXA G-PortalからGCOM-C「しきさい」/SGLIデータを取得します。LST（地表面温度）とNDVI（植生指標）に対応。

```bash
# LST（地表面温度）データ取得
python scripts/jaxa_api_client.py --lat 32.8032 --lon 130.7075 --product LST --download

# NDVI（植生指標）データ取得
python scripts/jaxa_api_client.py --lat 32.8032 --lon 130.7075 --product NDVI --download

# モックモード（テスト用）
python scripts/jaxa_api_client.py --lat 32.8032 --lon 130.7075 --product LST --mock --download
```

**環境変数:**
- `GPORTAL_USERNAME`: G-Portalユーザー名
- `GPORTAL_PASSWORD`: G-Portalパスワード

**詳細:** [JAXA G-Portal API使用ガイド](docs/JAXA_GPORTAL_API.md)

---

### 1-B. JAXA Earth APIからの衛星データ取得（レガシー）

**スクリプト:** `scripts/jaxa_api.py`

JAXA Earth APIから衛星観測データ（GCOM-C等）を検索し、GeoTIFF形式でダウンロードします。

```bash
python scripts/jaxa_api.py --lat 32.8032 --lon 130.7075 --days 7 --download
```

**パラメータ:**
- `--lat`: 緯度
- `--lon`: 経度
- `--days`: 過去何日分のデータを取得するか（デフォルト: 7日）
- `--dataset`: データセット名（デフォルト: GCOM-C）
- `--download`: GeoTIFFファイルをダウンロードする

**出力:**
- GeoTIFFファイル: `data/geotiff/`
- メタデータJSON: `data/metadata/`
- 観測データ（温度、湿度、NDVI等）をJSON形式で標準出力

**参考リンク:**
- [JAXA Earth API](https://data.earth.jaxa.jp/)
- [データセット一覧](https://data.earth.jaxa.jp/en/datasets/)

**注意:** 現在はモック実装です。実際のAPIアクセスには `pystac-client` ライブラリが必要です。

### 2. 農園情報の取得

**スクリプト:** `scripts/farm_info.py`

農園の基本情報を取得します。Neo4jに接続できない場合はダミーデータを返します。

```bash
python scripts/farm_info.py --lat 32.8032 --lon 130.7075
```

**出力例:**
```json
{
  "name": "Nanaka Farm",
  "latitude": 32.8032,
  "longitude": 130.7075,
  "source": "dummy",
  "timestamp": "2026-01-08T22:36:45.089787"
}
```

### 3. 衛星観測データの保存

**スクリプト:** `scripts/save_weather.py`

日付、温度、湿度、NDVI平均値をNeo4jに保存します。

```bash
python scripts/save_weather.py --date 2026-01-08 --temperature 18.5 --humidity 68.0 --ndvi-avg 0.75
```

**パラメータ:**
- `--date`: 観測日（YYYY-MM-DD形式）
- `--temperature`: 温度（℃）
- `--humidity`: 湿度（%）
- `--ndvi-avg`: NDVI平均値

**出力例:**
```
✓ データ保存成功:
  日付: 2026-01-08
  温度: 18.5℃
  湿度: 68.0%
  NDVI平均: 0.75
```

### 4. 観測データの照会

**スクリプト:** `scripts/query_data.py`

Neo4jに保存された観測データを取得して表示します。

```bash
python scripts/query_data.py
```

**出力例:**
```
📊 Nanaka Farm 観測データ:
======================================================================

観測 #1:
  農園名: Nanaka Farm
  日付: 2026-01-08
  温度: 18.5℃
  湿度: 68.0%
  NDVI平均: 0.75

合計: 1 件のデータ
======================================================================
```

## Claude Code カスタムコマンド

### `/hello-farm` コマンド

Nanaka Farm の情報を表示するカスタムコマンドです。

**定義ファイル:** `.claude/commands/hello-farm.md`

Claude Code CLI を起動後、以下のコマンドで実行できます:

```
/hello-farm
```

内部的に `scripts/farm_info.py` を呼び出します。

### `/collect-weather-data` コマンド（新機能）

JAXA Earth APIからデータを取得し、Neo4jに保存する一連の処理を自動化します。

**定義ファイル:** `.claude/commands/collect-weather-data.md`

Claude Code CLI を起動後、以下のコマンドで実行できます:

```
/collect-weather-data
```

**処理フロー:**
1. JAXA Earth APIから衛星データを検索
2. GeoTIFFファイルをダウンロード
3. メタデータを抽出
4. Neo4jデータベースに保存

詳細は `.claude/commands/collect-weather-data.md` を参照してください。

## フック

### afterCodeChange フック

**ファイル:** `.claude/hooks/afterCodeChange.ts`

`.cypher` ファイルの変更を検知して、自動的に構文チェックを実行します。

**機能:**
- 括弧、角括弧、波括弧のペアチェック
- Cypherキーワードの存在確認
- 構文エラーの検出と修正提案

Claude Code CLI 実行中に `.cypher` ファイルを編集すると自動的に実行されます。

## Cypherクエリ

### サンプルクエリ

**ファイル:** `queries/test.cypher`

Nanaka Farmの観測データを取得するサンプルクエリです。

```cypher
// 最新5件の観測データを取得
MATCH (f:Farm {name: 'Nanaka Farm'})-[:HAS_OBSERVATION]->(s:SatelliteData)
RETURN f.name as farm_name,
       f.latitude as lat,
       f.longitude as lon,
       s.date as observation_date,
       s.temperature as temp,
       s.humidity as humidity,
       s.ndvi_avg as ndvi
ORDER BY s.date DESC
LIMIT 5;

// 最新の観測データのみ取得
MATCH (f:Farm {name: 'Nanaka Farm'})-[:HAS_OBSERVATION]->(s:SatelliteData)
RETURN s
ORDER BY s.date DESC
LIMIT 1;
```

## データモデル

### Neo4jグラフ構造

```
(Farm:Farm)
  - name: String
  - latitude: Float
  - longitude: Float

(SatelliteData:SatelliteData)
  - date: Date
  - temperature: Float
  - humidity: Float
  - ndvi_avg: Float
  - created_at: DateTime

(Farm)-[:HAS_OBSERVATION]->(SatelliteData)
```

## 使用例

### 完全なワークフロー（JAXA Earth API統合版）

1. **JAXA Earth APIからデータ取得:**
   ```bash
   python scripts/jaxa_api.py --lat 32.8032 --lon 130.7075 --days 7 --download
   ```

2. **取得したデータをNeo4jに保存:**
   ```bash
   python scripts/save_weather.py --date 2026-01-08 --temperature 18.5 --humidity 68.0 --ndvi-avg 0.75
   ```

3. **保存したデータの確認:**
   ```bash
   python scripts/query_data.py
   ```

### 基本的なワークフロー（手動入力版）

1. **農園情報の確認:**
   ```bash
   python scripts/farm_info.py --lat 32.8032 --lon 130.7075
   ```

2. **観測データの保存:**
   ```bash
   python scripts/save_weather.py --date 2026-01-08 --temperature 18.5 --humidity 68.0 --ndvi-avg 0.75
   ```

3. **データの確認:**
   ```bash
   python scripts/query_data.py
   ```

## トラブルシューティング

### Neo4j接続エラー

Neo4jに接続できない場合:
1. Neo4jサービスが起動しているか確認
2. `NEO4J_PASSWORD` 環境変数が正しく設定されているか確認
3. URI (`bolt://localhost:7687`) が正しいか確認

### 文字化け（Windows）

すべてのスクリプトはWindows環境でのUTF-8出力に対応しています。それでも文字化けが発生する場合:

```bash
chcp 65001
```

を実行してから、スクリプトを実行してください。

## ライセンス

このプロジェクトはNanaka Farm専用の内部ツールです。

## 作成者

Generated with Claude Code
