#!/usr/bin/env python3
"""
Farm Information Script
農園情報を取得して表示するスクリプト
"""

import argparse
import json
import os
import sys
from datetime import datetime

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False


def get_farm_info_from_neo4j(lat, lon, uri, user, password):
    """Neo4jから農園情報を取得"""
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            result = session.run(
                """
                MATCH (f:Farm)
                WHERE abs(f.latitude - $lat) < 0.01 AND abs(f.longitude - $lon) < 0.01
                RETURN f.name as name, f.latitude as lat, f.longitude as lon
                LIMIT 1
                """,
                lat=lat,
                lon=lon
            )
            record = result.single()
            if record:
                driver.close()
                return {
                    "name": record["name"],
                    "latitude": record["lat"],
                    "longitude": record["lon"],
                    "source": "neo4j"
                }
        driver.close()
    except Exception as e:
        print(f"Neo4j connection error: {e}", file=sys.stderr)

    return None


def get_dummy_farm_info(lat, lon):
    """ダミーの農園情報を返す"""
    return {
        "name": "Nanaka Farm",
        "latitude": lat,
        "longitude": lon,
        "source": "dummy"
    }


def main():
    parser = argparse.ArgumentParser(description="農園情報を取得します")
    parser.add_argument("--lat", type=float, required=True, help="緯度")
    parser.add_argument("--lon", type=float, required=True, help="経度")

    args = parser.parse_args()

    # Neo4j接続情報
    neo4j_uri = "bolt://localhost:7687"
    neo4j_user = "neo4j"
    neo4j_password = os.environ.get("nAnAkA0629", "")

    farm_info = None

    # Neo4jが利用可能で、パスワードが設定されている場合は接続を試みる
    if NEO4J_AVAILABLE and neo4j_password:
        farm_info = get_farm_info_from_neo4j(
            args.lat, args.lon, neo4j_uri, neo4j_user, neo4j_password
        )

    # Neo4jから取得できなかった場合はダミーデータを使用
    if farm_info is None:
        farm_info = get_dummy_farm_info(args.lat, args.lon)

    # 現在時刻を追加
    farm_info["timestamp"] = datetime.now().isoformat()

    # JSON形式で出力
    print(json.dumps(farm_info, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
