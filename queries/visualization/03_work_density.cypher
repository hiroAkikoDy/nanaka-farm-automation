// =====================================================================
// 03. データ密度ヒートマップ
// =====================================================================
//
// 【目的】
// 観測データの密度と頻度を分析
// 高頻度観測エリア、データギャップの検出
//
// 【実行方法】
// Neo4jブラウザで実行後、テーブルビューまたはグラフビューで確認
//
// 【期待される出力】
// - 日次/週次/月次のデータ密度
// - 観測頻度のヒートマップデータ
// - データ欠損期間の特定
//
// =====================================================================

// クエリ1: 日次観測密度
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
WITH s.date AS 日付, COUNT(s) AS 観測数
RETURN 日付,
       観測数,
       CASE
         WHEN 観測数 >= 3 THEN '高密度'
         WHEN 観測数 >= 2 THEN '中密度'
         ELSE '低密度'
       END AS 密度レベル
ORDER BY 日付 DESC;

// ---------------------------------------------------------------------

// クエリ2: 曜日別観測パターン
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
WITH s.date.dayOfWeek AS 曜日, s
RETURN 曜日,
       CASE 曜日
         WHEN 1 THEN '月曜'
         WHEN 2 THEN '火曜'
         WHEN 3 THEN '水曜'
         WHEN 4 THEN '木曜'
         WHEN 5 THEN '金曜'
         WHEN 6 THEN '土曜'
         WHEN 7 THEN '日曜'
       END AS 曜日名,
       COUNT(s) AS 観測数,
       AVG(s.ndvi_avg) AS NDVI平均
ORDER BY 曜日;

// ---------------------------------------------------------------------

// クエリ3: 週次データ密度マトリックス
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
WITH s.date.year AS 年,
     s.date.week AS 週,
     COUNT(s) AS 観測数,
     AVG(s.ndvi_avg) AS ndvi平均
RETURN 年,
       週,
       観測数,
       round(ndvi平均 * 1000) / 1000 AS NDVI平均,
       CASE
         WHEN 観測数 >= 5 THEN '⬛⬛⬛⬛⬛' // 非常に高密度
         WHEN 観測数 >= 4 THEN '⬛⬛⬛⬛'  // 高密度
         WHEN 観測数 >= 3 THEN '⬛⬛⬛'   // 中密度
         WHEN 観測数 >= 2 THEN '⬛⬛'    // 低密度
         ELSE '⬛'                      // 非常に低密度
       END AS ヒートマップ
ORDER BY 年 DESC, 週 DESC
LIMIT 20;

// ---------------------------------------------------------------------

// クエリ4: データギャップの検出（7日以上間隔が空いている期間）
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
WITH s
ORDER BY s.date
WITH collect(s) AS observations
UNWIND range(1, size(observations)-1) AS idx
WITH observations[idx] AS current,
     observations[idx-1] AS previous
WITH current.date AS 現在日,
     previous.date AS 前回日,
     duration.between(previous.date, current.date).days AS 間隔日数
WHERE 間隔日数 > 7
RETURN 前回日,
       現在日,
       間隔日数,
       '⚠️ データギャップ' AS 警告
ORDER BY 間隔日数 DESC;

// ---------------------------------------------------------------------

// クエリ5: 月次ヒートマップ（観測数とNDVI）
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
WITH s.date.year AS 年,
     s.date.month AS 月,
     COUNT(s) AS 観測数,
     AVG(s.ndvi_avg) AS ndvi平均,
     AVG(s.temperature) AS 温度平均
RETURN 年,
       月,
       観測数,
       round(ndvi平均 * 1000) / 1000 AS NDVI,
       round(温度平均 * 10) / 10 AS 温度,
       CASE
         WHEN 観測数 >= 20 THEN '🟩🟩🟩'
         WHEN 観測数 >= 10 THEN '🟩🟩'
         WHEN 観測数 >= 5 THEN '🟩'
         ELSE '⬜'
       END AS 密度表示
ORDER BY 年 DESC, 月 DESC;

// ---------------------------------------------------------------------

// クエリ6: 時間帯別分布（時刻データがある場合）
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
WHERE s.created_at IS NOT NULL
WITH s.created_at.hour AS 時間帯, s
RETURN 時間帯,
       COUNT(s) AS 観測数,
       AVG(s.ndvi_avg) AS NDVI平均
ORDER BY 時間帯;

// =====================================================================
// 【パラメータ説明】
// - s.date.dayOfWeek: 曜日（1=月曜, 7=日曜）
// - s.date.week: ISO週番号
// - duration.between(): 日付間の期間計算
//
// 【可視化のヒント】
// Neo4jブラウザでの表示:
// 1. テーブルビューでヒートマップ列を確認
// 2. 観測数でノードサイズを調整
// 3. NDVI値でカラーグラデーション適用
//
// 【カスタマイズ例】
// データギャップの閾値変更:
// WHERE 間隔日数 > 14  // 14日以上の間隔を検出
//
// 高密度の定義変更:
// WHEN 観測数 >= 10 THEN '高密度'  // 閾値を10に変更
// =====================================================================
