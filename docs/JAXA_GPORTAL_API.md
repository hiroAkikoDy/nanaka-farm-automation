# JAXA G-Portal API 使用ガイド

## 概要

JAXA G-Portalは、JAXA地球観測衛星データを無料で提供するシステムです。GCOM-C「しきさい」（SHIKISAI）のSGLI（Second Generation Global Imager）センサーデータにアクセスできます。

## 対応データプロダクト

### GCOM-C/SGLI Level 2 プロダクト

| プロダクト | 説明 | 用途 |
|----------|------|------|
| **L2-LST** | Land Surface Temperature（地表面温度） | 気温推定、熱環境分析 |
| **L2-VGI** | Vegetation Index（植生指標）| NDVI含む、農作物生育監視 |

## セットアップ

### 1. gportal-python のインストール

```bash
pip install gportal
```

### 2. G-Portal ユーザー登録

1. [G-Portal 登録ページ](https://gportal.jaxa.jp/gpr/auth) にアクセス
2. アカウントを作成（無料）
3. メール認証を完了

### 3. 環境変数の設定

```bash
# Linux/Mac
export GPORTAL_USERNAME="your_username"
export GPORTAL_PASSWORD="your_password"

# Windows PowerShell
$env:GPORTAL_USERNAME="your_username"
$env:GPORTAL_PASSWORD="your_password"

# Windows コマンドプロンプト
set GPORTAL_USERNAME=your_username
set GPORTAL_PASSWORD=your_password
```

## 使用方法

### 基本的な使い方

```bash
# LST（地表面温度）データを取得
python scripts/jaxa_api_client.py \
  --lat 32.8032 \
  --lon 130.7075 \
  --days 7 \
  --product LST \
  --download

# NDVI（植生指標）データを取得
python scripts/jaxa_api_client.py \
  --lat 32.8032 \
  --lon 130.7075 \
  --days 7 \
  --product NDVI \
  --download
```

### モックモード（テスト用）

G-Portalアカウントなしでテストする場合:

```bash
python scripts/jaxa_api_client.py \
  --lat 32.8032 \
  --lon 130.7075 \
  --days 1 \
  --product LST \
  --mock \
  --download
```

### パラメータ説明

| パラメータ | 必須 | デフォルト | 説明 |
|----------|------|-----------|------|
| `--lat` | ✓ | - | 緯度（度） |
| `--lon` | ✓ | - | 経度（度） |
| `--days` | | 7 | 過去何日分のデータを取得するか |
| `--product` | | LST | プロダクトタイプ（LST/NDVI/VGI） |
| `--download` | | False | データをダウンロードする |
| `--mock` | | False | モックモードで実行 |

## 出力データ

### ダウンロードファイル

- **保存先**: `data/geotiff/`
- **形式**: HDF5 (`.h5`)
- **ファイル名例**: `GC1SG1_2026010701D01D_LST.h5`

### メタデータJSON

- **保存先**: `data/metadata/`
- **ファイル名例**: `GC1SG1_2026010701D01D_LST_metadata.json`

**メタデータ構造:**

```json
{
  "product_id": "GC1SG1_2026010701D01D_LST.h5",
  "dataset": "GCOM-C/SGLI/L2-LST",
  "observation_date": "2026-01-07",
  "bbox": [130.2075, 32.3032, 131.2075, 33.3032],
  "parameters": {
    "LST": 291.5,
    "NDVI": 0.75,
    "quality_flag": "good"
  },
  "file_path": "C:\\...\\data\\geotiff\\GC1SG1_2026010701D01D_LST.h5",
  "file_size_mb": 245.8,
  "download_time": "2026-01-08T23:12:32.283387",
  "source": "gportal"
}
```

## 実装例

### Python コードでの使用

```python
import gportal

# データセット取得
datasets = gportal.datasets()

# LST データ検索
res = gportal.search(
    dataset_ids=datasets["GCOM-C/SGLI"]["LEVEL2"]["Land area"]["L2-LST"],
    start_time="2026-01-01T00:00:00",
    end_time="2026-01-07T23:59:59",
    bbox=[130.2, 32.3, 131.2, 33.3],  # [west, south, east, north]
    params={}
)

# プロダクト取得
products = res.products()

# 認証設定
gportal.username = "your_username"
gportal.password = "your_password"

# ダウンロード
gportal.download(products, local_dir="data/geotiff")
```

## データ処理

### HDF5ファイルの読み込み

```python
import h5py
import numpy as np

# HDF5ファイルを開く
with h5py.File('data/geotiff/GC1SG1_2026010701D01D_LST.h5', 'r') as f:
    # データセット一覧
    print(list(f.keys()))

    # LST データ読み込み
    lst_data = f['Image_data/LST'][:]

    # 緯度経度データ
    lat_data = f['Geometry_data/Latitude'][:]
    lon_data = f['Geometry_data/Longitude'][:]
```

### 温度変換（Kelvin → Celsius）

```python
# LSTはケルビン単位
lst_kelvin = 291.5
lst_celsius = lst_kelvin - 273.15  # 18.35°C
```

## トラブルシューティング

### 認証エラー

```
⚠️  G-Portal認証情報が設定されていません
```

**解決方法:**
- 環境変数 `GPORTAL_USERNAME` と `GPORTAL_PASSWORD` を設定
- G-Portalアカウントが有効か確認

### gportal-python がインストールされていない

```
⚠️  gportal-pythonがインストールされていません
```

**解決方法:**
```bash
pip install gportal
```

### データが見つからない

**原因:**
- 指定期間・範囲にデータが存在しない
- 雲に覆われている
- 衛星軌道が通過していない

**解決方法:**
- 検索期間を広げる
- 異なる日付を試す

## 参考リンク

### 公式ドキュメント

- [G-Portal](https://gportal.jaxa.jp/gpr/?lang=en) - JAXA地球観測衛星データ提供システム
- [gportal-python ドキュメント](https://gportal.readthedocs.io/) - Python API リファレンス
- [G-Portal ユーザーマニュアル](https://gportal.jaxa.jp/gpr/assets/mng_upload/COMMON/upload/GPortalUserManual_en.pdf) - 詳細な使用方法
- [GCOM-C データユーザーハンドブック](https://gportal.jaxa.jp/gpr/assets/mng_upload/GCOM-C/GCOM-C_SHIKISAI_Data_Users_Handbook_en.pdf) - SGLI製品仕様

### 関連情報

- [JAXA Earth API](https://data.earth.jaxa.jp/) - 別のデータアクセス方法
- [G-Portal サポート](https://gportal.jaxa.jp/gpr/information/support?lang=en) - 問い合わせ先

## ライセンスと利用規約

GCOM-C/SGLIデータは、G-Portalユーザー登録後、無料で利用できます。詳細は[G-Portal利用規約](https://gportal.jaxa.jp/gpr/)を参照してください。

## 更新履歴

- 2026-01-08: 初版作成
- モック実装とリアルAPI実装の両対応
- LST, NDVI, VGI プロダクトサポート
