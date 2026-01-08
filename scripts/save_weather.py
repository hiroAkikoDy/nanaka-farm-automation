#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weather Data Saver Script
衛星データをNeo4jに保存するスクリプト
"""

import argparse
import os
import sys
from datetime import datetime

# Windows環境でのUTF-8出力設定
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    print("Warning: neo4j package is not installed", file=sys.stderr)


def save_satellite_data_to_neo4j(date, temperature, humidity, ndvi_avg, uri, user, password):
    """
    Neo4jに衛星データを保存

    Args:
        date: 観測日 (YYYY-MM-DD形式)
        temperature: 温度 (℃)
        humidity: 湿度 (%)
        ndvi_avg: NDVI平均値
        uri: Neo4j接続URI
        user: Neo4jユーザー名
        password: Neo4jパスワード

    Returns:
        bool: 成功したかどうか
    """
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))

        with driver.session() as session:
            # Farmノードを取得または作成し、SatelliteDataノードを作成してリレーションを設定
            result = session.run(
                """
                MERGE (f:Farm {name: 'Nanaka Farm'})
                ON CREATE SET f.latitude = 32.8032, f.longitude = 130.7075

                CREATE (s:SatelliteData {
                    date: date($date),
                    temperature: $temperature,
                    humidity: $humidity,
                    ndvi_avg: $ndvi_avg,
                    created_at: datetime()
                })

                CREATE (f)-[r:HAS_OBSERVATION]->(s)

                RETURN s.date as date, s.temperature as temp,
                       s.humidity as hum, s.ndvi_avg as ndvi
                """,
                date=date,
                temperature=temperature,
                humidity=humidity,
                ndvi_avg=ndvi_avg
            )

            record = result.single()

            if record:
                print(f"✓ データ保存成功:")
                print(f"  日付: {record['date']}")
                print(f"  温度: {record['temp']}℃")
                print(f"  湿度: {record['hum']}%")
                print(f"  NDVI平均: {record['ndvi']}")
                driver.close()
                return True

        driver.close()

    except Exception as e:
        print(f"✗ Neo4j保存エラー: {e}", file=sys.stderr)
        return False

    return False


def main():
    parser = argparse.ArgumentParser(description="衛星データをNeo4jに保存します")
    parser.add_argument("--date", type=str, required=True,
                       help="観測日 (YYYY-MM-DD形式)")
    parser.add_argument("--temperature", type=float, required=True,
                       help="温度 (℃)")
    parser.add_argument("--humidity", type=float, required=True,
                       help="湿度 (%%)")
    parser.add_argument("--ndvi-avg", type=float, required=True,
                       help="NDVI平均値")

    args = parser.parse_args()

    # Neo4j接続情報
    neo4j_uri = "bolt://localhost:7687"
    neo4j_user = "neo4j"
    neo4j_password = os.environ.get("NEO4J_PASSWORD", "nAnAkA0629")

    if not NEO4J_AVAILABLE:
        print("✗ エラー: neo4jパッケージがインストールされていません", file=sys.stderr)
        print("  pip install neo4j を実行してください", file=sys.stderr)
        sys.exit(1)

    if not neo4j_password:
        print("✗ エラー: NEO4J_PASSWORD環境変数が設定されていません", file=sys.stderr)
        sys.exit(1)

    # 日付形式のバリデーション
    try:
        datetime.strptime(args.date, "%Y-%m-%d")
    except ValueError:
        print(f"✗ エラー: 日付形式が正しくありません: {args.date}", file=sys.stderr)
        print("  YYYY-MM-DD形式で指定してください", file=sys.stderr)
        sys.exit(1)

    # データ保存
    success = save_satellite_data_to_neo4j(
        args.date,
        args.temperature,
        args.humidity,
        args.ndvi_avg,
        neo4j_uri,
        neo4j_user,
        neo4j_password
    )

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
