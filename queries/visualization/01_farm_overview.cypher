// =====================================================================
// 01. 農園全体の構造可視化
// =====================================================================
//
// 【目的】
// Nanaka Farm全体のデータ構造を可視化し、
// Farm → SatelliteData のリレーションを表示
//
// 【実行方法】
// Neo4jブラウザで以下のクエリをコピー&ペースト
//
// 【期待される出力】
// - Farmノード（緑）
// - SatelliteDataノード（青）
// - HAS_OBSERVATION リレーション（矢印）
//
// =====================================================================

// クエリ1: 農園と衛星データの全体像
MATCH (f:Farm)-[r:HAS_OBSERVATION]->(s:SatelliteData)
RETURN f, r, s
LIMIT 100;

// ---------------------------------------------------------------------

// クエリ2: 農園の基本情報
MATCH (f:Farm)
RETURN f.name AS 農園名,
       f.latitude AS 緯度,
       f.longitude AS 経度,
       f.area AS 面積
ORDER BY f.name;

// ---------------------------------------------------------------------

// クエリ3: 観測データ数の集計
MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
RETURN f.name AS 農園名,
       COUNT(s) AS 観測データ数,
       MIN(s.date) AS 最古データ,
       MAX(s.date) AS 最新データ
ORDER BY 観測データ数 DESC;

// ---------------------------------------------------------------------

// クエリ4: 農園とその観測データ（詳細表示）
MATCH (f:Farm {name: 'Nanaka Farm'})-[:HAS_OBSERVATION]->(s:SatelliteData)
RETURN f.name AS 農園名,
       s.date AS 観測日,
       s.ndvi_avg AS NDVI平均,
       s.temperature AS 温度,
       s.humidity AS 湿度
ORDER BY s.date DESC
LIMIT 20;

// =====================================================================
// 【パラメータ説明】
// - LIMIT: 表示する最大ノード数（デフォルト: 100）
// - f.name: 農園名でフィルタリング（例: 'Nanaka Farm'）
//
// 【カスタマイズ例】
// 特定期間のデータのみ表示:
// MATCH (f:Farm)-[r:HAS_OBSERVATION]->(s:SatelliteData)
// WHERE s.date >= date('2026-01-01') AND s.date <= date('2026-01-31')
// RETURN f, r, s;
// =====================================================================
