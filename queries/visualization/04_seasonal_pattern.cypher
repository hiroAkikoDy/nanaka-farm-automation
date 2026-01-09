// =====================================================================
// 04. 季節パターンの分析
// =====================================================================
//
// 【目的】
// 季節ごとのNDVI変化、温度パターン、植生サイクルを分析
// 作物の成長パターンと季節性の理解
//
// 【実行方法】
// Neo4jブラウザで実行し、季節ごとの比較を行う
//
// 【期待される出力】
// - 季節別のNDVI平均値
// - 月次トレンド
// - 成長期・休眠期の特定
//
// =====================================================================

// クエリ1: 季節別統計サマリー
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
WITH s.date.month AS 月,
     CASE
       WHEN s.date.month IN [3, 4, 5] THEN '春'
       WHEN s.date.month IN [6, 7, 8] THEN '夏'
       WHEN s.date.month IN [9, 10, 11] THEN '秋'
       ELSE '冬'
     END AS 季節,
     s.ndvi_avg AS ndvi,
     s.temperature AS temp
RETURN 季節,
       COUNT(*) AS 観測数,
       round(AVG(ndvi) * 1000) / 1000 AS NDVI平均,
       round(MIN(ndvi) * 1000) / 1000 AS NDVI最小,
       round(MAX(ndvi) * 1000) / 1000 AS NDVI最大,
       round(AVG(temp) * 10) / 10 AS 温度平均
ORDER BY CASE 季節
  WHEN '春' THEN 1
  WHEN '夏' THEN 2
  WHEN '秋' THEN 3
  WHEN '冬' THEN 4
END;

// ---------------------------------------------------------------------

// クエリ2: 月次NDVIトレンド（年間パターン）
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
WITH s.date.month AS 月,
     AVG(s.ndvi_avg) AS ndvi平均,
     AVG(s.temperature) AS 温度平均,
     COUNT(*) AS データ数
RETURN 月,
       CASE 月
         WHEN 1 THEN '1月' WHEN 2 THEN '2月' WHEN 3 THEN '3月'
         WHEN 4 THEN '4月' WHEN 5 THEN '5月' WHEN 6 THEN '6月'
         WHEN 7 THEN '7月' WHEN 8 THEN '8月' WHEN 9 THEN '9月'
         WHEN 10 THEN '10月' WHEN 11 THEN '11月' WHEN 12 THEN '12月'
       END AS 月名,
       round(ndvi平均 * 1000) / 1000 AS NDVI,
       round(温度平均 * 10) / 10 AS 温度,
       データ数,
       CASE
         WHEN ndvi平均 > 0.7 THEN '🟢 成長期'
         WHEN ndvi平均 > 0.5 THEN '🟡 成長中'
         ELSE '🔴 休眠期'
       END AS 成長ステージ
ORDER BY 月;

// ---------------------------------------------------------------------

// クエリ3: 年次比較（複数年のデータがある場合）
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
WITH s.date.year AS 年,
     s.date.month AS 月,
     AVG(s.ndvi_avg) AS ndvi平均
RETURN 年,
       月,
       round(ndvi平均 * 1000) / 1000 AS NDVI平均
ORDER BY 年, 月;

// ---------------------------------------------------------------------

// クエリ4: 成長サイクルの特定
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
WITH s
ORDER BY s.date
WITH collect(s) AS observations
UNWIND range(0, size(observations)-1) AS idx
WITH observations[idx] AS obs,
     idx AS 順番
WITH obs.date AS 日付,
     obs.ndvi_avg AS ndvi,
     順番
RETURN 日付,
       round(ndvi * 1000) / 1000 AS NDVI,
       CASE
         WHEN ndvi >= 0.75 THEN '🌿 ピーク期'
         WHEN ndvi >= 0.65 THEN '🌱 成長期'
         WHEN ndvi >= 0.50 THEN '🌾 発育期'
         ELSE '🍂 休眠期'
       END AS フェーズ
ORDER BY 日付 DESC
LIMIT 30;

// ---------------------------------------------------------------------

// クエリ5: 温度とNDVIの季節相関
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
WHERE s.temperature IS NOT NULL
WITH s.date.month AS 月,
     CASE
       WHEN s.date.month IN [3, 4, 5] THEN '春'
       WHEN s.date.month IN [6, 7, 8] THEN '夏'
       WHEN s.date.month IN [9, 10, 11] THEN '秋'
       ELSE '冬'
     END AS 季節,
     s.ndvi_avg AS ndvi,
     s.temperature AS temp
RETURN 季節,
       round(AVG(temp) * 10) / 10 AS 平均温度,
       round(AVG(ndvi) * 1000) / 1000 AS 平均NDVI,
       COUNT(*) AS データ数,
       CASE
         WHEN AVG(temp) > 25 AND AVG(ndvi) > 0.7 THEN '⚠️ 高温・高NDVI'
         WHEN AVG(temp) < 10 AND AVG(ndvi) < 0.5 THEN '⚠️ 低温・低NDVI'
         ELSE '✓ 正常範囲'
       END AS 状態
ORDER BY CASE 季節
  WHEN '春' THEN 1
  WHEN '夏' THEN 2
  WHEN '秋' THEN 3
  WHEN '冬' THEN 4
END;

// ---------------------------------------------------------------------

// クエリ6: 週次変化率（季節トレンドの検出）
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
WITH s
ORDER BY s.date
WITH collect(s) AS observations
UNWIND range(7, size(observations)-1, 7) AS idx
WITH observations[idx] AS current,
     observations[idx-7] AS previous
WHERE previous IS NOT NULL
WITH current.date AS 現在週,
     current.ndvi_avg AS 現在NDVI,
     previous.ndvi_avg AS 前週NDVI,
     ((current.ndvi_avg - previous.ndvi_avg) / previous.ndvi_avg * 100) AS 変化率
RETURN 現在週,
       round(現在NDVI * 1000) / 1000 AS NDVI,
       round(変化率 * 10) / 10 AS 週次変化率,
       CASE
         WHEN 変化率 > 5 THEN '📈 急増'
         WHEN 変化率 > 0 THEN '↗️ 増加'
         WHEN 変化率 > -5 THEN '↘️ 減少'
         ELSE '📉 急減'
       END AS トレンド
ORDER BY 現在週 DESC
LIMIT 20;

// =====================================================================
// 【パラメータ説明】
// - s.date.month: 月（1-12）
// - 季節の定義: 春(3-5月), 夏(6-8月), 秋(9-11月), 冬(12-2月)
// - 成長ステージ閾値: NDVI > 0.7 (成長期), > 0.5 (成長中)
//
// 【可視化のヒント】
// 1. 月次トレンドグラフを折れ線グラフで表示
// 2. 季節別の箱ひげ図で分散を確認
// 3. ヒートマップで月×年のマトリックス表示
//
// 【カスタマイズ例】
// 季節の定義を変更（南半球の場合）:
// WHEN s.date.month IN [9, 10, 11] THEN '春'
// WHEN s.date.month IN [12, 1, 2] THEN '夏'
//
// NDVI閾値の調整:
// WHEN ndvi平均 > 0.8 THEN '成長期'  // より厳格な基準
// =====================================================================
