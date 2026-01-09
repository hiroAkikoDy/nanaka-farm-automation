// =====================================================================
// 02. 時系列データの可視化
// =====================================================================
//
// 【目的】
// SatelliteDataの時系列変化を追跡
// NDVIの推移、温度変化、季節パターンを分析
//
// 【実行方法】
// Neo4jブラウザで以下のクエリを実行
// グラフビューで時間軸に沿ってノードが配置される
//
// 【期待される出力】
// - 時系列でソートされたSatelliteDataノード
// - NDVI、温度、湿度の変化トレンド
//
// =====================================================================

// クエリ1: NDVI時系列データ（最新30日）
MATCH (f:Farm {name: 'Nanaka Farm'})-[:HAS_OBSERVATION]->(s:SatelliteData)
WHERE s.date >= date() - duration({days: 30})
RETURN s.date AS 観測日,
       s.ndvi_avg AS NDVI,
       s.temperature AS 温度,
       s.humidity AS 湿度
ORDER BY s.date ASC;

// ---------------------------------------------------------------------

// クエリ2: NDVI変化率の計算
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
WITH s
ORDER BY s.date
WITH collect(s) AS observations
UNWIND range(1, size(observations)-1) AS idx
WITH observations[idx] AS current,
     observations[idx-1] AS previous
RETURN current.date AS 日付,
       current.ndvi_avg AS 現在NDVI,
       previous.ndvi_avg AS 前回NDVI,
       round((current.ndvi_avg - previous.ndvi_avg) * 100) / 100 AS NDVI変化,
       round(((current.ndvi_avg - previous.ndvi_avg) / previous.ndvi_avg * 100) * 100) / 100 AS 変化率パーセント
ORDER BY current.date DESC
LIMIT 20;

// ---------------------------------------------------------------------

// クエリ3: 週次NDVI平均
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
WITH s.date AS date, s.ndvi_avg AS ndvi
WITH date.year AS 年, date.week AS 週, ndvi
RETURN 年,
       週,
       AVG(ndvi) AS NDVI平均,
       COUNT(*) AS データ数,
       MIN(ndvi) AS NDVI最小,
       MAX(ndvi) AS NDVI最大
ORDER BY 年 DESC, 週 DESC
LIMIT 12;

// ---------------------------------------------------------------------

// クエリ4: 月次統計サマリー
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
WITH s.date.year AS 年,
     s.date.month AS 月,
     s.ndvi_avg AS ndvi,
     s.temperature AS temp
RETURN 年,
       月,
       round(AVG(ndvi) * 1000) / 1000 AS NDVI平均,
       round(AVG(temp) * 10) / 10 AS 温度平均,
       COUNT(*) AS 観測回数
ORDER BY 年 DESC, 月 DESC;

// ---------------------------------------------------------------------

// クエリ5: 温度とNDVIの相関（グラフビュー用）
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
WHERE s.temperature IS NOT NULL AND s.ndvi_avg IS NOT NULL
RETURN s.date AS 日付,
       s.temperature AS 温度,
       s.ndvi_avg AS NDVI,
       CASE
         WHEN s.ndvi_avg > 0.7 THEN '健康'
         WHEN s.ndvi_avg > 0.5 THEN '普通'
         ELSE '注意'
       END AS 植生状態
ORDER BY s.date DESC
LIMIT 50;

// =====================================================================
// 【パラメータ説明】
// - duration({days: 30}): 過去30日分のデータを取得
// - date(): 現在の日付
// - s.date.year, s.date.month, s.date.week: 年月週の抽出
//
// 【可視化のヒント】
// Neo4jブラウザの設定:
// 1. グラフビューでノードサイズをNDVI値に比例させる
// 2. カラースキームを温度に応じて変更（寒色→暖色）
// 3. タイムライン表示を有効化
//
// 【カスタマイズ例】
// 特定期間のデータ:
// WHERE s.date >= date('2026-01-01') AND s.date <= date('2026-12-31')
// =====================================================================
