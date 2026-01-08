# Collect Weather Data コマンド

JAXA Earth APIから衛星データを取得し、Neo4jに保存する一連の処理を自動化します。

## 処理フロー

1. **JAXA Earth APIアクセス**: Nanaka Farm周辺の衛星データを検索
2. **GeoTIFFダウンロード**: 観測データをdata/geotiffに保存
3. **メタデータ抽出**: 温度、湿度、NDVI等の観測データを抽出
4. **Neo4j保存**: 抽出したデータをグラフデータベースに保存

## 実行コマンド

```bash
# 1. JAXA Earth APIからデータ取得（過去7日分）
python scripts/jaxa_api.py --lat 32.8032 --lon 130.7075 --days 7 --download

# 2. 取得したデータからメタデータを読み込み
# 最新のメタデータファイルを確認
ls -lt data/metadata/*.json | head -1

# 3. 観測データをNeo4jに保存
# （jaxa_api.pyの出力からパラメータを取得）
python scripts/save_weather.py --date 2026-01-08 --temperature 18.5 --humidity 68.0 --ndvi-avg 0.75

# 4. 保存したデータを確認
python scripts/query_data.py
```

## 自動化スクリプト（推奨）

上記の処理を自動化するには、以下のシェルスクリプトを作成してください:

**scripts/collect_and_save.sh** (Linux/Mac):
```bash
#!/bin/bash
# JAXA APIからデータ取得してNeo4jに保存

LAT=32.8032
LON=130.7075
DAYS=7

echo "=== Nanaka Farm 気象データ収集 ==="

# JAXA APIからデータ取得
python scripts/jaxa_api.py --lat $LAT --lon $LON --days $DAYS --download > /tmp/jaxa_output.json

# JSONから観測データを抽出してNeo4jに保存
# (jqコマンドを使用してJSONパース)
if command -v jq &> /dev/null; then
    DATE=$(jq -r '.observation.date' /tmp/jaxa_output.json)
    TEMP=$(jq -r '.observation.temperature' /tmp/jaxa_output.json)
    HUM=$(jq -r '.observation.humidity' /tmp/jaxa_output.json)
    NDVI=$(jq -r '.observation.ndvi_avg' /tmp/jaxa_output.json)

    python scripts/save_weather.py --date "$DATE" --temperature "$TEMP" --humidity "$HUM" --ndvi-avg "$NDVI"
else
    echo "jqコマンドが必要です: sudo apt-get install jq"
fi

echo "=== 完了 ==="
```

**scripts/collect_and_save.ps1** (Windows PowerShell):
```powershell
# JAXA APIからデータ取得してNeo4jに保存

$LAT = 32.8032
$LON = 130.7075
$DAYS = 7

Write-Host "=== Nanaka Farm 気象データ収集 ==="

# JAXA APIからデータ取得
$output = python scripts/jaxa_api.py --lat $LAT --lon $LON --days $DAYS --download | Out-String
$json = $output | ConvertFrom-Json

# 観測データをNeo4jに保存
$date = $json.observation.date
$temp = $json.observation.temperature
$hum = $json.observation.humidity
$ndvi = $json.observation.ndvi_avg

python scripts/save_weather.py --date $date --temperature $temp --humidity $hum --ndvi-avg $ndvi

Write-Host "=== 完了 ==="
```

## 注意事項

- 現在のjaxa_api.pyはモック実装です
- 実際のJAXA Earth API使用には認証情報が必要な場合があります
- GeoTIFFファイルは大容量になる可能性があります
- 定期実行にはcronジョブやタスクスケジューラーを使用してください

## 参考リンク

- JAXA Earth API: https://data.earth.jaxa.jp/
- データセット一覧: https://data.earth.jaxa.jp/en/datasets/
