// =====================================================================
// 05. 異常値検出
// =====================================================================
//
// 【目的】
// データの異常値、外れ値、急激な変化を検出
// 問題の早期発見とアラート生成
//
// 【実行方法】
// Neo4jブラウザで実行し、異常値ノードを赤色でハイライト
//
// 【期待される出力】
// - 統計的外れ値の検出
// - 急激な変化の特定
// - データ品質問題の発見
//
// =====================================================================

// クエリ1: NDVI異常値の検出（標準偏差ベース）
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
WITH AVG(s.ndvi_avg) AS ndvi平均,
     stdev(s.ndvi_avg) AS ndvi標準偏差
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
WITH s,
     ndvi平均,
     ndvi標準偏差,
     abs(s.ndvi_avg - ndvi平均) / ndvi標準偏差 AS Zスコア
WHERE Zスコア > 2.0  // 2標準偏差以上を異常値とする
RETURN s.date AS 日付,
       round(s.ndvi_avg * 1000) / 1000 AS NDVI,
       round(ndvi平均 * 1000) / 1000 AS 平均NDVI,
       round(Zスコア * 100) / 100 AS Zスコア,
       CASE
         WHEN Zスコア > 3.0 THEN '🔴 重度異常'
         WHEN Zスコア > 2.5 THEN '🟠 中度異常'
         ELSE '🟡 軽度異常'
       END AS 異常レベル
ORDER BY Zスコア DESC;

// ---------------------------------------------------------------------

// クエリ2: 急激なNDVI変化の検出
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
WITH s
ORDER BY s.date
WITH collect(s) AS observations
UNWIND range(1, size(observations)-1) AS idx
WITH observations[idx] AS current,
     observations[idx-1] AS previous
WITH current.date AS 日付,
     current.ndvi_avg AS 現在NDVI,
     previous.ndvi_avg AS 前回NDVI,
     abs(current.ndvi_avg - previous.ndvi_avg) AS 変化量,
     ((current.ndvi_avg - previous.ndvi_avg) / previous.ndvi_avg * 100) AS 変化率
WHERE abs(変化率) > 15  // 15%以上の変化を異常とする
RETURN 日付,
       round(現在NDVI * 1000) / 1000 AS NDVI,
       round(前回NDVI * 1000) / 1000 AS 前回NDVI,
       round(変化量 * 1000) / 1000 AS 変化量,
       round(変化率 * 10) / 10 AS 変化率パーセント,
       CASE
         WHEN 変化率 > 20 THEN '⚠️ 急増'
         WHEN 変化率 < -20 THEN '⚠️ 急減'
         ELSE '⚠️ 大幅変化'
       END AS アラート
ORDER BY abs(変化率) DESC
LIMIT 20;

// ---------------------------------------------------------------------

// クエリ3: 温度異常の検出
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
WHERE s.temperature IS NOT NULL
WITH AVG(s.temperature) AS 温度平均,
     stdev(s.temperature) AS 温度標準偏差
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
WHERE s.temperature IS NOT NULL
WITH s,
     温度平均,
     温度標準偏差,
     abs(s.temperature - 温度平均) / 温度標準偏差 AS Zスコア
WHERE Zスコア > 2.0
RETURN s.date AS 日付,
       round(s.temperature * 10) / 10 AS 温度,
       round(温度平均 * 10) / 10 AS 平均温度,
       round(Zスコア * 100) / 100 AS Zスコア,
       CASE
         WHEN s.temperature > 温度平均 + 2 * 温度標準偏差 THEN '🔥 異常高温'
         WHEN s.temperature < 温度平均 - 2 * 温度標準偏差 THEN '❄️ 異常低温'
         ELSE '⚠️ 温度異常'
       END AS 状態
ORDER BY Zスコア DESC;

// ---------------------------------------------------------------------

// クエリ4: データ品質チェック
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
WITH s,
     CASE
       WHEN s.ndvi_avg IS NULL THEN 'NDVI欠損'
       WHEN s.temperature IS NULL THEN '温度欠損'
       WHEN s.humidity IS NULL THEN '湿度欠損'
       WHEN s.ndvi_avg < 0 OR s.ndvi_avg > 1 THEN 'NDVI範囲外'
       WHEN s.temperature < -50 OR s.temperature > 60 THEN '温度範囲外'
       ELSE 'OK'
     END AS 品質状態
WHERE 品質状態 <> 'OK'
RETURN s.date AS 日付,
       品質状態,
       s.ndvi_avg AS NDVI,
       s.temperature AS 温度,
       s.humidity AS 湿度,
       '🔍 要確認' AS アクション
ORDER BY s.date DESC;

// ---------------------------------------------------------------------

// クエリ5: 連続異常期間の検出
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
WITH s
ORDER BY s.date
WITH collect(s) AS observations
UNWIND range(0, size(observations)-1) AS idx
WITH observations[idx] AS obs, idx
WHERE obs.ndvi_avg < 0.4 OR obs.ndvi_avg > 0.9
WITH obs.date AS 日付,
     obs.ndvi_avg AS NDVI,
     idx
ORDER BY idx
WITH collect({日付: 日付, NDVI: NDVI}) AS 異常データ,
     count(*) AS 異常数
WHERE 異常数 >= 3  // 3回以上連続する異常
RETURN 異常データ,
       異常数,
       '⚠️ 連続異常検出' AS 警告;

// ---------------------------------------------------------------------

// クエリ6: 季節外れの値の検出
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
WITH s.date.month AS 月,
     AVG(s.ndvi_avg) AS 月平均NDVI,
     stdev(s.ndvi_avg) AS 月標準偏差
MATCH (f2:Farm)-[:HAS_OBSERVATION]->(s2:SatelliteData)
WHERE s2.date.month = 月
WITH s2,
     月,
     月平均NDVI,
     月標準偏差,
     abs(s2.ndvi_avg - 月平均NDVI) / 月標準偏差 AS Zスコア
WHERE Zスコア > 2.0
RETURN s2.date AS 日付,
       月,
       round(s2.ndvi_avg * 1000) / 1000 AS NDVI,
       round(月平均NDVI * 1000) / 1000 AS 月平均,
       round(Zスコア * 100) / 100 AS Zスコア,
       '📅 季節外れ' AS 分類
ORDER BY Zスコア DESC
LIMIT 20;

// ---------------------------------------------------------------------

// クエリ7: 複合異常（NDVI + 温度）
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
WHERE s.temperature IS NOT NULL
WITH AVG(s.ndvi_avg) AS ndvi平均,
     AVG(s.temperature) AS 温度平均,
     stdev(s.ndvi_avg) AS ndvi偏差,
     stdev(s.temperature) AS 温度偏差
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
WHERE s.temperature IS NOT NULL
WITH s,
     abs(s.ndvi_avg - ndvi平均) / ndvi偏差 AS NDVIスコア,
     abs(s.temperature - 温度平均) / 温度偏差 AS 温度スコア
WHERE NDVIスコア > 1.5 AND 温度スコア > 1.5  // 両方が異常
RETURN s.date AS 日付,
       round(s.ndvi_avg * 1000) / 1000 AS NDVI,
       round(s.temperature * 10) / 10 AS 温度,
       round(NDVIスコア * 100) / 100 AS NDVIスコア,
       round(温度スコア * 100) / 100 AS 温度スコア,
       '🚨 複合異常' AS 警告レベル
ORDER BY (NDVIスコア + 温度スコア) DESC
LIMIT 15;

// =====================================================================
// 【パラメータ説明】
// - Zスコア: (値 - 平均) / 標準偏差
// - 閾値: Zスコア > 2.0 (約95%信頼区間外)
// - NDVI正常範囲: 0.0 ～ 1.0
// - 温度正常範囲: -50℃ ～ 60℃
//
// 【異常レベル】
// - 🔴 重度異常: Zスコア > 3.0 (99.7%区間外)
// - 🟠 中度異常: Zスコア > 2.5
// - 🟡 軽度異常: Zスコア > 2.0
//
// 【可視化のヒント】
// Neo4jブラウザ設定:
// 1. 異常値ノードを赤色でハイライト
// 2. Zスコアでノードサイズを調整
// 3. タイムラインで異常発生時期を確認
//
// 【カスタマイズ例】
// 閾値の調整:
// WHERE Zスコア > 1.5  // より厳格な検出
// WHERE abs(変化率) > 10  // より小さな変化も検出
//
// 連続異常の定義変更:
// WHERE 異常数 >= 5  // 5回以上連続
// =====================================================================
