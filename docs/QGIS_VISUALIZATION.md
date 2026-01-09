# QGIS可視化ガイド

Neo4jデータをQGISで地理空間可視化する方法

## 📋 目次

1. [環境準備](#環境準備)
2. [データエクスポート](#データエクスポート)
3. [QGISでの表示](#qgisでの表示)
4. [スタイル設定](#スタイル設定)
5. [GeoTIFFとの重ね合わせ](#geotiffとの重ね合わせ)
6. [高度な可視化](#高度な可視化)

---

## 環境準備

### 必要なソフトウェア

1. **QGIS** (最新版推奨)
   - ダウンロード: https://qgis.org/
   - インストール: 長期サポート版（LTR）を推奨

2. **Python環境**
   - Neo4jドライバー: `pip install neo4j`

---

## データエクスポート

### 基本的なエクスポート

```bash
# 農園データと観測データをエクスポート
python scripts/export_geojson.py

# 農園データのみをエクスポート
python scripts/export_geojson.py --farms-only

# 観測データの数を制限
python scripts/export_geojson.py --observations-limit 50
```

### エクスポート結果

```
exports/
├── nanaka_farm_fields.geojson       # 農園ポイント
└── satellite_observations.geojson   # 衛星観測ポイント
```

### GeoJSON構造

**農園データ (nanaka_farm_fields.geojson):**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [130.7075, 32.8032]
      },
      "properties": {
        "name": "Nanaka Farm",
        "area": 10000,
        "observation_count": 25,
        "avg_ndvi": 0.7521,
        "avg_temperature": 18.5
      }
    }
  ]
}
```

**観測データ (satellite_observations.geojson):**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [130.7075, 32.8032]
      },
      "properties": {
        "farm_name": "Nanaka Farm",
        "observation_date": "2026-01-08",
        "ndvi": 0.7500,
        "temperature": 18.4,
        "ndvi_status": "healthy"
      }
    }
  ]
}
```

---

## QGISでの表示

### ステップ1: QGISを起動

1. QGISを開く
2. 新しいプロジェクトを作成

### ステップ2: ベースマップを追加

1. **メニュー**: `レイヤ` → `レイヤの追加` → `XYZ タイル`
2. **接続**: `OpenStreetMap` を選択
3. **追加**: ダブルクリックで地図を表示

### ステップ3: GeoJSONレイヤを追加

#### 農園データの追加

1. **メニュー**: `レイヤ` → `レイヤの追加` → `ベクタレイヤの追加`
2. **ソースタイプ**: `ファイル`
3. **ベクタデータセット**: `...` ボタンをクリック
4. **ファイル選択**: `exports/nanaka_farm_fields.geojson`
5. **追加** → **閉じる**

#### 観測データの追加

1. 同様の手順で `exports/satellite_observations.geojson` を追加
2. レイヤパネルに2つのレイヤが表示される

### ステップ4: 表示範囲の調整

1. レイヤを右クリック
2. **レイヤの範囲にズーム** を選択
3. Nanaka Farm周辺にズーム

---

## スタイル設定

### 農園ポイントのスタイル

#### 基本スタイル

1. `nanaka_farm_fields` レイヤを右クリック
2. **プロパティ** → **シンボロジー**
3. **シンプルマーカー** を選択

**設定例:**
- **マーカー形状**: 星
- **サイズ**: 5mm
- **色**: 緑 (#00FF00)
- **枠線**: 黒、1px

#### NDVI値による色分け

1. **シンボロジー** → **カテゴリ値による定義**
2. **値**: `avg_ndvi`
3. **分類** をクリック

**カラーランプ:**
```
NDVI範囲    色          説明
> 0.7      濃緑        健康
0.5-0.7    黄緑        普通
0.3-0.5    黄色        注意
< 0.3      赤          警告
```

#### 観測数による円サイズ

1. **シンボロジー** → **サイズ**
2. **データ定義の上書き**: `observation_count`
3. **スケール方法**: 線形
4. **最小サイズ**: 2mm
5. **最大サイズ**: 10mm

### 観測ポイントのスタイル

#### 日付による色分け

1. `satellite_observations` レイヤのプロパティ
2. **シンボロジー** → **段階に分けられた**
3. **値**: `observation_date`
4. **カラーランプ**: Spectral (古い→新しい: 青→赤)

#### NDVI状態による分類

1. **カテゴリ値による定義**
2. **値**: `ndvi_status`
3. **分類**:
   ```
   healthy     → 緑 (#00AA00)
   moderate    → 黄緑 (#AAAA00)
   poor        → オレンジ (#FF8800)
   very_poor   → 赤 (#FF0000)
   ```

---

## GeoTIFFとの重ね合わせ

### HDF5からGeoTIFFへの変換

```bash
# rasterioがインストールされている場合
python scripts/geotiff_processor.py \
  data/geotiff/GC1SG1_20260108D01D_T0528_L2SG_LST_Q_3000.h5 \
  --lat 32.8032 \
  --lon 130.7075 \
  --dataset LST \
  --export-tif
```

### GeoTIFFをQGISに追加

1. **メニュー**: `レイヤ` → `レイヤの追加` → `ラスタレイヤの追加`
2. **ソース**: GeoTIFFファイルを選択
3. **追加**

### ラスタスタイル設定

#### 温度データ（LST）

1. ラスタレイヤのプロパティ
2. **シンボロジー** → **レンダータイプ**: `単バンド疑似カラー`
3. **カラーランプ**:
   - タイプ: 勾配
   - 最小値: 273K (0°C) → 青
   - 最大値: 320K (47°C) → 赤
4. **補間**: 線形

#### NDVI データ

1. **レンダータイプ**: `単バンド疑似カラー`
2. **カラーランプ**:
   - 最小値: 0 → 茶色
   - 中間値: 0.5 → 黄色
   - 最大値: 1.0 → 濃緑

### レイヤの重ね合わせ順序

```
(上から)
1. satellite_observations (観測ポイント)
2. nanaka_farm_fields (農園ポイント)
3. GeoTIFF ラスタ (温度/NDVI)
4. OpenStreetMap (ベースマップ)
(下へ)
```

### 透過度の調整

1. ラスタレイヤのプロパティ
2. **透過性** タブ
3. **全体の不透明度**: 70%

---

## 高度な可視化

### ヒートマップ表示

#### 観測密度のヒートマップ

1. `satellite_observations` レイヤを複製
2. **シンボロジー** → **ヒートマップ**
3. **設定**:
   - 半径: 30mm
   - カラーランプ: YlOrRd (黄→オレンジ→赤)
   - 最大値: 10

### ラベル表示

#### 農園名の表示

1. `nanaka_farm_fields` レイヤのプロパティ
2. **ラベル** タブ → **単一ラベル**
3. **値**: `name`
4. **テキスト**: フォントサイズ 12pt、太字
5. **背景**: 白、不透明度 70%

#### NDVI値の表示

1. `satellite_observations` レイヤ
2. **ラベル**: `ndvi`
3. **フォーマット**: 小数点以下3桁
4. **配置**: ポイント上部

### タイムスライダー（時系列アニメーション）

1. **メニュー**: `表示` → `パネル` → `時系列コントローラ`
2. レイヤのプロパティ → **時系列**
3. **設定**:
   - 単一フィールド: `observation_date`
   - フォーマット: `yyyy-MM-dd`
4. タイムスライダーで時系列を再生

### 統計情報の表示

#### 属性テーブル

1. レイヤを右クリック
2. **属性テーブルを開く**
3. フィールド計算機でNDVI統計を計算

#### 統計要約

1. **メニュー**: `ベクタ` → `解析ツール` → `基本統計`
2. **入力レイヤ**: `satellite_observations`
3. **フィールド**: `ndvi`
4. **実行**

---

## エクスポートと共有

### 地図画像のエクスポート

1. **メニュー**: `プロジェクト` → `インポート/エクスポート` → `地図を画像にエクスポート`
2. **設定**:
   - 解像度: 300 DPI
   - フォーマット: PNG/PDF
3. **保存**

### Webマップの作成

1. **プラグイン**: `qgis2web` をインストール
2. **メニュー**: `Web` → `qgis2web` → `Create web map`
3. **設定**:
   - Leaflet または OpenLayers
   - データエクスポート
4. **Export** → HTML/JavaScript生成

### プロジェクトの保存

1. **メニュー**: `プロジェクト` → `名前を付けて保存`
2. ファイル名: `nanaka_farm_visualization.qgz`
3. すべてのレイヤとスタイルが保存される

---

## トラブルシューティング

### GeoJSONが表示されない

**問題**: レイヤが追加されても地図に表示されない

**解決方法**:
1. レイヤを右クリック → **レイヤの範囲にズーム**
2. 座標系を確認: プロジェクトのCRSが EPSG:4326 (WGS84) か確認
3. プロパティ → **ソース** タブで座標系を確認

### 座標がずれている

**問題**: ポイントの位置がおかしい

**解決方法**:
1. レイヤのプロパティ → **ソース**
2. **レイヤCRS**: EPSG:4326 に設定
3. **プロジェクトCRS**: EPSG:3857 (Web Mercator) に設定

### GeoTIFFが読み込めない

**問題**: ラスタレイヤがエラーになる

**解決方法**:
1. HDF5ファイルの場合、GDALドライバが必要
2. QGISの設定 → **GDAL** → **HDF5ドライバを有効化**
3. または、事前にGeoTIFFに変換

### パフォーマンスが遅い

**問題**: 大量のポイントで動作が遅い

**解決方法**:
1. 観測データの数を制限: `--observations-limit 50`
2. シンプルなシンボルを使用
3. レイヤのキャッシュを有効化

---

## 便利なプラグイン

### 推奨プラグイン

1. **QuickMapServices**
   - 様々なベースマップ追加
   - Google Maps、Bing Maps等

2. **TimeManager**
   - 時系列データのアニメーション
   - スライダーで時間軸操作

3. **qgis2web**
   - Webマップの生成
   - Leaflet/OpenLayers出力

4. **Data Plotly**
   - グラフとチャートの作成
   - NDVI時系列グラフ等

### インストール方法

1. **メニュー**: `プラグイン` → `プラグインの管理とインストール`
2. プラグイン名を検索
3. **プラグインをインストール**

---

## サンプルワークフロー

### 完全な可視化プロセス

#### 1. データ準備
```bash
# Neo4jデータをエクスポート
python scripts/export_geojson.py --observations-limit 100
```

#### 2. QGISプロジェクト作成
1. QGISを起動
2. OpenStreetMapを追加
3. GeoJSONレイヤを追加

#### 3. スタイル設定
1. 農園ポイント: NDVI値で色分け
2. 観測ポイント: 日付で色分け
3. ヒートマップレイヤ追加

#### 4. GeoTIFF重ね合わせ
1. LST/NDVIラスタを追加
2. 透過度70%に設定
3. カラーランプ適用

#### 5. 時系列アニメーション
1. タイムスライダー設定
2. アニメーション再生
3. ビデオエクスポート

#### 6. レポート作成
1. レイアウトマネージャで地図作成
2. 凡例、スケールバー、ノースアロー追加
3. PDF/PNG出力

---

## 参考資料

- [QGIS公式ドキュメント](https://docs.qgis.org/)
- [QGIS Training Manual](https://docs.qgis.org/latest/en/docs/training_manual/)
- [GeoJSON仕様](https://geojson.org/)
- [OGC標準](https://www.ogc.org/)

---

## 更新履歴

- 2026-01-09: 初版作成
  - GeoJSONエクスポート機能
  - QGIS基本表示手順
  - スタイル設定例
  - GeoTIFF重ね合わせ
