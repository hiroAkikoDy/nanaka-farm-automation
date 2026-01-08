#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Query Data Script
Neo4jからデータを取得して表示
"""

import os
import sys

# Windows環境でのUTF-8出力設定
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

try:
    from neo4j import GraphDatabase
except ImportError:
    print("Error: neo4j package is not installed", file=sys.stderr)
    sys.exit(1)

def query_farm_data():
    """Nanaka Farmの観測データを取得"""
    neo4j_uri = "bolt://localhost:7687"
    neo4j_user = "neo4j"
    neo4j_password = os.environ.get("NEO4J_PASSWORD", "nAnAkA0629")

    try:
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

        with driver.session() as session:
            result = session.run(
                """
                MATCH (f:Farm {name: 'Nanaka Farm'})-[:HAS_OBSERVATION]->(s:SatelliteData)
                RETURN f.name as farm_name,
                       s.date as observation_date,
                       s.temperature as temp,
                       s.humidity as humidity,
                       s.ndvi_avg as ndvi
                ORDER BY s.date DESC
                LIMIT 5
                """
            )

            print("\n📊 Nanaka Farm 観測データ:")
            print("=" * 70)

            count = 0
            for record in result:
                count += 1
                print(f"\n観測 #{count}:")
                print(f"  農園名: {record['farm_name']}")
                print(f"  日付: {record['observation_date']}")
                print(f"  温度: {record['temp']}℃")
                print(f"  湿度: {record['humidity']}%")
                print(f"  NDVI平均: {record['ndvi']}")

            if count == 0:
                print("\nデータが見つかりませんでした。")
            else:
                print(f"\n合計: {count} 件のデータ")
            print("=" * 70)

        driver.close()

    except Exception as e:
        print(f"✗ Neo4jクエリエラー: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    query_farm_data()
