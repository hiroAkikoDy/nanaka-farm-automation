# Collect Weather Data コマンド

JAXA G-Portal APIから衛星データを取得し、処理してNeo4jに保存する完全自動化ワークフロー。

## 処理フロー

1. **JAXA G-Portal API検索** - GCOM-C/SGLI衛星データを検索
2. **データダウンロード** - HDF5ファイルをdata/geotiffに保存
3. **GeoTIFF処理** - 統計値抽出（NDVI、LST等）
4. **Neo4j保存** - SatelliteDataノード作成
5. **サマリーレポート** - 取得データ数、NDVI傾向、異常値検出

## 使用方法

Claude Code CLI起動後:

```
# デフォルト（過去7日間）
/collect-weather-data

# 開始日指定
/collect-weather-data 2026-01-01

# 期間指定
/collect-weather-data 2026-01-01 2026-01-07
```

## 自動化スクリプト

**Pythonスクリプトを実行:**

```bash
python scripts/collect_and_save_workflow.py \
  --lat 32.8032 \
  --lon 130.7075 \
  --days 7 \
  --retry 3
```

## 実装詳細

以下のPythonスクリプトを作成して自動化を実現:

**scripts/collect_and_save_workflow.py**

このスクリプトは:
1. JAXA G-Portal APIクライアント呼び出し
2. 各HDF5ファイルをgeotiff_processorで処理
3. 抽出した統計値をNeo4jに保存
4. サマリーレポート生成

### エラーハンドリング

- **API接続失敗**: 3回リトライ（指数バックオフ）
- **ダウンロード失敗**: エラーログ記録、スキップして継続
- **Neo4j保存失敗**: トランザクションロールバック、エラー詳細記録
- **データ破損**: 検証後、破損ファイルを隔離

### 出力

1. **処理ログ** - `logs/collect_weather_YYYYMMDD.log`
2. **エラーログ** - `logs/errors_YYYYMMDD.log`
3. **サマリーレポート** - `reports/summary_YYYYMMDD.json`

**サマリーレポート形式:**

```json
{
  "execution_time": "2026-01-08T23:30:00",
  "period": {
    "start": "2026-01-01",
    "end": "2026-01-07"
  },
  "data_collection": {
    "total_files": 7,
    "successful": 6,
    "failed": 1,
    "failed_files": ["GC1SG1_20260103_corrupted.h5"]
  },
  "ndvi_analysis": {
    "mean": 0.742,
    "trend": "increasing",
    "change_rate": 0.015,
    "anomalies": []
  },
  "lst_analysis": {
    "mean_celsius": 18.5,
    "min": 15.2,
    "max": 22.3
  },
  "neo4j_records": {
    "created": 6,
    "failed": 0
  }
}
```

## 手動実行手順

自動化スクリプトを使用しない場合:

### 1. データ取得

```bash
# JAXA G-Portal APIでデータ検索・ダウンロード
python scripts/jaxa_api_client.py \
  --lat 32.8032 --lon 130.7075 \
  --days 7 \
  --product LST \
  --mock --download

python scripts/jaxa_api_client.py \
  --lat 32.8032 --lon 130.7075 \
  --days 7 \
  --product NDVI \
  --mock --download
```

### 2. データ処理

```bash
# 各HDF5ファイルを処理
for file in data/geotiff/*.h5; do
  python scripts/geotiff_processor.py "$file" \
    --lat 32.8032 --lon 130.7075 \
    --dataset LST \
    --output "results/$(basename $file .h5)_stats.json"
done
```

### 3. Neo4j保存

```bash
# JSONから値を読み取ってNeo4jに保存
# （処理済みデータを使用）
python scripts/save_weather.py \
  --date 2026-01-07 \
  --temperature 18.5 \
  --humidity 68.0 \
  --ndvi-avg 0.75
```

### 4. 確認

```bash
# 保存したデータを照会
python scripts/query_data.py
```

## 定期実行設定

### Linux/Mac (cron)

```bash
# 毎日午前2時に実行
0 2 * * * cd /path/to/nanaka-farm-automation && python scripts/collect_and_save_workflow.py --days 1 >> logs/cron.log 2>&1
```

### Windows (タスクスケジューラー)

1. タスクスケジューラーを開く
2. 「基本タスクの作成」を選択
3. トリガー: 毎日午前2時
4. 操作: プログラムの開始
   - プログラム: `python`
   - 引数: `scripts/collect_and_save_workflow.py --days 1`
   - 開始: `C:\path\to\nanaka-farm-automation`

## トラブルシューティング

### API接続エラー

```
エラー: ⚠️ G-Portal認証情報が設定されていません
```

**解決方法:**
```bash
export GPORTAL_USERNAME="your_username"
export GPORTAL_PASSWORD="your_password"
```

### ダウンロード失敗

ログファイルで詳細確認:
```bash
cat logs/errors_YYYYMMDD.log
```

### Neo4j保存失敗

Neo4jサービス稼働確認:
```bash
# サービス確認
systemctl status neo4j  # Linux
# または
neo4j console  # 手動起動
```

## 参考資料

- [JAXA G-Portal API使用ガイド](../docs/JAXA_GPORTAL_API.md)
- [GeoTIFF処理ドキュメント](../README.md#1-c-geotiffhdf5データ処理新機能)
- [Neo4jデータモデル](../README.md#データモデル)

## 注意事項

- 初回実行時は環境変数とNeo4j接続を確認
- 大量データダウンロード時はディスク容量に注意
- モックモードでテスト後、実APIに切り替え
- ログファイルは定期的にクリーンアップ
