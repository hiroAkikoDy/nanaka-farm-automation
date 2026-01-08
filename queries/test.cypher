// Test Cypher Query
// Nanaka Farmの観測データを取得

MATCH (f:Farm {name: 'Nanaka Farm'})-[:HAS_OBSERVATION]->(s:SatelliteData)
RETURN f.name as farm_name,
       f.latitude as lat,
       f.longitude as lon,
       s.date as observation_date,
       s.temperature as temp,
       s.humidity as humidity,
       s.ndvi_avg as ndvi
ORDER BY s.date DESC
LIMIT 5;

// 最新の観測データのみ取得
MATCH (f:Farm {name: 'Nanaka Farm'})-[:HAS_OBSERVATION]->(s:SatelliteData)
RETURN s
ORDER BY s.date DESC
LIMIT 1;
