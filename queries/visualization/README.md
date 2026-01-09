# Neo4j可視化クエリ集

Nanaka Farm気象データ自動化システム用のCypherクエリセット

## 📁 ファイル一覧

### 01_farm_overview.cypher
**農園全体の構造可視化**

- 農園とSatelliteDataのリレーション表示
- 農園基本情報の取得
- 観測データ数の集計
- 詳細データ表示

**使用例:**
```cypher
MATCH (f:Farm)-[r:HAS_OBSERVATION]->(s:SatelliteData)
RETURN f, r, s
LIMIT 100;
```

**適用シーン:**
- システム全体の構造把握
- データベース健全性チェック
- 初期セットアップ確認

---

### 02_temporal_data.cypher
**時系列データの可視化**

- NDVI時系列データ（最新30日）
- NDVI変化率の計算
- 週次/月次NDVI平均
- 温度とNDVIの相関分析

**使用例:**
```cypher
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
WHERE s.date >= date() - duration({days: 30})
RETURN s.date, s.ndvi_avg, s.temperature
ORDER BY s.date ASC;
```

**適用シーン:**
- トレンド分析
- 成長パターンの把握
- 異常期間の特定

---

### 03_work_density.cypher
**データ密度ヒートマップ**

- 日次観測密度
- 曜日別観測パターン
- 週次データ密度マトリックス
- データギャップの検出

**使用例:**
```cypher
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
WITH s.date AS 日付, COUNT(s) AS 観測数
RETURN 日付, 観測数
ORDER BY 日付 DESC;
```

**適用シーン:**
- データ収集頻度の確認
- 欠損期間の特定
- 収集スケジュールの最適化

---

### 04_seasonal_pattern.cypher
**季節パターンの分析**

- 季節別統計サマリー
- 月次NDVIトレンド
- 年次比較
- 成長サイクルの特定
- 温度とNDVIの季節相関

**使用例:**
```cypher
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
WITH s.date.month AS 月, AVG(s.ndvi_avg) AS NDVI
RETURN 月, NDVI
ORDER BY 月;
```

**適用シーン:**
- 年間成長パターンの理解
- 作付計画の立案
- 過去年との比較

---

### 05_anomaly_detection.cypher
**異常値検出**

- NDVI異常値の検出（Zスコアベース）
- 急激なNDVI変化の検出
- 温度異常の検出
- データ品質チェック
- 連続異常期間の検出
- 季節外れの値の検出
- 複合異常（NDVI + 温度）

**使用例:**
```cypher
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
WITH AVG(s.ndvi_avg) AS 平均, stdev(s.ndvi_avg) AS 偏差
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
WITH s, abs(s.ndvi_avg - 平均) / 偏差 AS Zスコア
WHERE Zスコア > 2.0
RETURN s.date, s.ndvi_avg, Zスコア
ORDER BY Zスコア DESC;
```

**適用シーン:**
- 問題の早期発見
- データ品質管理
- アラート生成

---

## 🚀 クイックスタート

### 1. Neo4jブラウザを開く
```
http://localhost:7474
```

### 2. 認証情報でログイン
- ユーザー名: `neo4j`
- パスワード: `nAnAkA0629` (または環境変数 NEO4J_PASSWORD)

### 3. クエリファイルを開く
```bash
cat queries/visualization/01_farm_overview.cypher
```

### 4. クエリをコピー&ペーストして実行

### 5. グラフビューで結果を確認

---

## 📊 可視化のベストプラクティス

### グラフビュー設定

1. **ノードサイズ**
   - NDVIの値に比例させる
   - 設定: `Node size` → `Property` → `ndvi_avg`

2. **ノードカラー**
   - 温度でグラデーション
   - 設定: `Node color` → `Property` → `temperature`

3. **リレーション表示**
   - 時系列順に配置
   - 設定: `Layout` → `Hierarchical`

### テーブルビュー設定

1. **列の並び替え**
   - 日付で降順ソート
   - 重要な指標を左側に配置

2. **データフォーマット**
   - 小数点以下3桁で表示
   - パーセンテージ表記

3. **エクスポート**
   - CSV形式でダウンロード
   - Excel等で詳細分析

---

## 🔧 カスタマイズ

### 期間の変更
```cypher
WHERE s.date >= date('2026-01-01') AND s.date <= date('2026-12-31')
```

### 閾値の調整
```cypher
WHERE Zスコア > 3.0  -- より厳格な異常検出
```

### 集計単位の変更
```cypher
WITH s.date.week AS 週  -- 週次集計
WITH s.date.month AS 月  -- 月次集計
WITH s.date.year AS 年   -- 年次集計
```

---

## 📈 分析ワークフロー例

### 基本分析フロー

1. **01_farm_overview.cypher** - データ全体を把握
2. **02_temporal_data.cypher** - 時系列トレンドを確認
3. **04_seasonal_pattern.cypher** - 季節パターンを理解
4. **05_anomaly_detection.cypher** - 異常値を検出

### 問題調査フロー

1. **05_anomaly_detection.cypher** - 異常を検出
2. **02_temporal_data.cypher** - 前後の推移を確認
3. **03_work_density.cypher** - データギャップをチェック
4. **01_farm_overview.cypher** - 全体への影響を評価

---

## 💡 ヒント

### パフォーマンス最適化

1. **LIMIT句の使用**
   ```cypher
   RETURN f, r, s
   LIMIT 100;  -- 大量データ時は必須
   ```

2. **インデックスの作成**
   ```cypher
   CREATE INDEX FOR (s:SatelliteData) ON (s.date);
   CREATE INDEX FOR (s:SatelliteData) ON (s.ndvi_avg);
   ```

3. **WHERE句での絞り込み**
   ```cypher
   WHERE s.date >= date('2026-01-01')  -- 期間を限定
   ```

### デバッグ

1. **COUNT()で件数確認**
   ```cypher
   MATCH (s:SatelliteData)
   RETURN COUNT(s) AS データ数;
   ```

2. **EXPLAIN句でプラン確認**
   ```cypher
   EXPLAIN
   MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
   RETURN f, s;
   ```

3. **PROFILE句でパフォーマンス計測**
   ```cypher
   PROFILE
   MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
   RETURN COUNT(s);
   ```

---

## 📚 参考資料

- [Neo4j Cypher Manual](https://neo4j.com/docs/cypher-manual/)
- [Neo4j Browser Guide](https://neo4j.com/docs/browser-manual/)
- [Nanaka Farm README](../../README.md)
- [データモデル](../../README.md#データモデル)

---

## 🆘 トラブルシューティング

### クエリが遅い
- LIMIT句を追加
- WHERE句で期間を絞る
- インデックスを作成

### データが表示されない
- データが存在するか確認: `MATCH (s:SatelliteData) RETURN COUNT(s);`
- リレーションを確認: `MATCH ()-[r:HAS_OBSERVATION]->() RETURN COUNT(r);`

### グラフが複雑すぎる
- LIMIT値を減らす
- 特定期間に絞る
- サブグラフのみ表示

---

## ✨ 更新履歴

- 2026-01-09: 初版作成
  - 5つの可視化クエリセット
  - 農園概要、時系列、密度、季節、異常検出
