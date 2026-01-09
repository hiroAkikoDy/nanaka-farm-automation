# JAXA G-Portal 実API使用ガイド

gportal-pythonライブラリを使用して実際のJAXA G-Portal APIに接続する方法。

## インストール

```bash
pip install gportal
```

## 認証情報の設定

### 1. G-Portalアカウント登録

1. [JAXA G-Portal](https://gportal.jaxa.jp/)にアクセス
2. 「新規ユーザ登録」からアカウント作成
3. ユーザー名とパスワードを取得

### 2. 環境変数設定

**Linux/Mac:**
```bash
export GPORTAL_USERNAME="your_username"
export GPORTAL_PASSWORD="your_password"
```

**Windows (PowerShell):**
```powershell
$env:GPORTAL_USERNAME="your_username"
$env:GPORTAL_PASSWORD="your_password"
```

**Windows (コマンドプロンプト):**
```cmd
set GPORTAL_USERNAME=your_username
set GPORTAL_PASSWORD=your_password
```

### 3. 環境変数の永続化

**Linux/Mac (`~/.bashrc` または `~/.zshrc`):**
```bash
export GPORTAL_USERNAME="your_username"
export GPORTAL_PASSWORD="your_password"
```

**Windows (システム環境変数):**
1. 「システムのプロパティ」→「環境変数」を開く
2. 「新規」をクリック
3. 変数名: `GPORTAL_USERNAME`, 値: `your_username`
4. 変数名: `GPORTAL_PASSWORD`, 値: `your_password`

## 利用可能なデータセット

### GCOM-C/SGLI (しきさい)

#### LST (Land Surface Temperature - 地表面温度)

| レベル | データセット名 | ID |
|-------|--------------|-----|
| L2 | L2-LST | 10002019 |
| L2 統計 | L2 statistics-LST | 10002054 |
| L3 | L3-LST (月次) | 10003120 |
| L3 | L3-LST (8日) | 10003121 |

#### NDVI (Normalized Difference Vegetation Index - 正規化植生指標)

| レベル | データセット名 | ID |
|-------|--------------|-----|
| L2 統計 | L2 statistics-NDVI | 10002047 |
| L3 | L3-NDVI (月次) | 10003106 |
| L3 | L3-NDVI (8日) | 10003107 |

#### その他の植生指標

| パラメータ | L2統計 ID | L3月次 ID | L3 8日 ID |
|-----------|----------|----------|---------|
| EVI (Enhanced Vegetation Index) | 10002048 | 10003108 | 10003109 |
| LAI (Leaf Area Index) | 10002051 | 10003114 | 10003115 |
| FPAR (Fraction of Photosynthetically Active Radiation) | 10002050 | 10003112 | 10003113 |

## 実API使用例

### 1. 基本的な検索

```python
import gportal
from datetime import datetime

# 認証情報設定（環境変数から自動読み込み）
gportal.username = os.getenv("GPORTAL_USERNAME")
gportal.password = os.getenv("GPORTAL_PASSWORD")

# データセット検索
results = gportal.search(
    dataset_ids=['10003107'],  # L3-NDVI (8日)
    bbox=[130.0, 32.0, 131.0, 33.0],  # [west, south, east, north]
    start_time=datetime(2026, 1, 1),
    end_time=datetime(2026, 1, 8),
    count=10
)

# 検索結果の表示
print(f"総件数: {results.total_count}")
for product in results:
    print(f"  {product.id}: {product.begin_time} - {product.end_time}")
```

### 2. データダウンロード

```python
from gportal import download

# 検索結果から最初のプロダクトをダウンロード
for product in results:
    # ダウンロード先ディレクトリ
    output_dir = "data/geotiff"

    # ダウンロード実行
    download(
        product.id,
        output_dir,
        username=gportal.username,
        password=gportal.password
    )

    print(f"✓ ダウンロード完了: {product.id}")
    break  # 最初の1件のみ
```

### 3. 複数データセットの検索

```python
# LST + NDVI を同時検索
results = gportal.search(
    dataset_ids=[
        '10003120',  # L3-LST (月次)
        '10003106'   # L3-NDVI (月次)
    ],
    bbox=[130.7, 32.8, 130.8, 32.9],  # Nanaka Farm周辺
    start_time='2026-01-01',
    end_time='2026-01-31'
)
```

## scripts/jaxa_api_client.py の実API使用

既存のスクリプトは環境変数が設定されていれば自動的に実APIに切り替わります:

```bash
# 環境変数設定
export GPORTAL_USERNAME="your_username"
export GPORTAL_PASSWORD="your_password"

# 実API使用（--mockフラグなし）
python scripts/jaxa_api_client.py \
  --lat 32.8032 \
  --lon 130.7075 \
  --product NDVI \
  --download

# モックモード（テスト用）
python scripts/jaxa_api_client.py \
  --lat 32.8032 \
  --lon 130.7075 \
  --product NDVI \
  --mock \
  --download
```

## データセット選択のガイドライン

### 農業用途の推奨データセット

| 目的 | 推奨データセット | 理由 |
|------|----------------|------|
| 植生モニタリング | L3-NDVI (8日) | 8日間隔、雲除去済み、広域カバー |
| 地表面温度 | L3-LST (8日) | 8日間隔、品質管理済み |
| 詳細解析 | L2統計データ | より細かい時間解像度 |

### データレベルの違い

- **L2 (Level 2)**: センサー観測データを物理量に変換したもの
- **L2統計**: L2データの統計処理版（日次・地域別）
- **L3 (Level 3)**: グリッド化・雲除去済み（8日・月次）

**推奨**: 農業用途ではL3データが使いやすい（雲の影響が少ない）

## バウンディングボックス設定

```python
# Nanaka Farm 周辺（5km範囲）
bbox = [
    130.7075 - 0.05,  # west (経度 - 約5km)
    32.8032 - 0.05,   # south (緯度 - 約5km)
    130.7075 + 0.05,  # east (経度 + 約5km)
    32.8032 + 0.05    # north (緯度 + 約5km)
]
# => [130.6575, 32.7532, 130.7575, 32.8532]
```

緯度・経度 0.1度 ≈ 約11km

## トラブルシューティング

### 認証エラー

```
AuthenticationError: Invalid username or password
```

**解決方法**:
1. G-Portalアカウントが有効か確認
2. 環境変数が正しく設定されているか確認:
   ```bash
   echo $GPORTAL_USERNAME
   echo $GPORTAL_PASSWORD
   ```
3. パスワードに特殊文字が含まれる場合、引用符で囲む

### データが見つからない

```
Total count: 0
```

**解決方法**:
1. バウンディングボックスを広げる
2. 期間を延ばす
3. データセットIDを確認（L2 vs L3）
4. GCOM-C/SGLIの観測周期を確認（2-3日に1回）

### ダウンロードが遅い

- G-PortalはSFTP経由でダウンロード（数MB/秒）
- HDF5ファイルは1ファイル数百MB〜数GB
- 待機時間を見込む（1ファイル数分〜10分）

## 参考資料

- [JAXA G-Portal](https://gportal.jaxa.jp/)
- [gportal-python GitHub](https://github.com/nttcom/gportal-python)
- [GCOM-C/SGLI プロダクト一覧](https://gportal.jaxa.jp/gpr/search?tab=0)
- [GCOM-C/SGLI データ利用ハンドブック](https://suzaku.eorc.jaxa.jp/GCOM_C/data/product_std.html)

## 使用例: 完全ワークフロー

```bash
# 1. 認証情報設定
export GPORTAL_USERNAME="your_username"
export GPORTAL_PASSWORD="your_password"

# 2. データ検索・ダウンロード
python scripts/jaxa_api_client.py \
  --lat 32.8032 \
  --lon 130.7075 \
  --days 7 \
  --product NDVI \
  --download

# 3. データ処理
python scripts/geotiff_processor.py \
  data/geotiff/GC1SG1_*.h5 \
  --lat 32.8032 \
  --lon 130.7075 \
  --dataset NDVI

# 4. Neo4j保存
python scripts/save_weather.py \
  --date 2026-01-08 \
  --temperature 18.5 \
  --humidity 68.0 \
  --ndvi-avg 0.75

# 5. または完全自動化
python scripts/collect_and_save_workflow.py \
  --lat 32.8032 \
  --lon 130.7075 \
  --days 7
```

## セキュリティ上の注意

1. **認証情報を直接コードに書かない**
   - 必ず環境変数を使用
   - `.env` ファイルを使う場合は `.gitignore` に追加

2. **パスワード管理**
   - 強力なパスワードを使用
   - 定期的に変更
   - 共有しない

3. **ログファイル**
   - 認証情報がログに記録されないよう注意
   - ログファイルのアクセス権限を制限
