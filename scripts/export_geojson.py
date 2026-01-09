#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GeoJSONエクスポートツール
Neo4jデータをGeoJSON形式でエクスポートし、QGISで表示可能にする
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from neo4j import GraphDatabase

# Windows環境でのUTF-8出力設定
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Neo4j接続設定
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "nAnAkA0629")


class GeoJSONExporter:
    """GeoJSONエクスポートクラス"""

    def __init__(self, uri, user, password):
        """
        初期化

        Args:
            uri: Neo4j URI
            user: ユーザー名
            password: パスワード
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """接続を閉じる"""
        self.driver.close()

    def fetch_farm_data(self):
        """
        Neo4jから農園データを取得

        Returns:
            農園データのリスト
        """
        query = """
        MATCH (f:Farm)
        OPTIONAL MATCH (f)-[:HAS_OBSERVATION]->(s:SatelliteData)
        WITH f,
             COUNT(s) AS observation_count,
             AVG(s.ndvi_avg) AS avg_ndvi,
             AVG(s.temperature) AS avg_temperature,
             MIN(s.date) AS first_observation,
             MAX(s.date) AS last_observation
        RETURN f.name AS name,
               f.latitude AS latitude,
               f.longitude AS longitude,
               f.area AS area,
               observation_count,
               avg_ndvi,
               avg_temperature,
               first_observation,
               last_observation
        ORDER BY f.name
        """

        with self.driver.session() as session:
            result = session.run(query)
            return [dict(record) for record in result]

    def fetch_satellite_observations(self, limit=None):
        """
        Neo4jから衛星観測ポイントを取得

        Args:
            limit: 取得する最大数

        Returns:
            観測データのリスト
        """
        query = """
        MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
        RETURN f.name AS farm_name,
               f.latitude AS latitude,
               f.longitude AS longitude,
               s.date AS observation_date,
               s.ndvi_avg AS ndvi,
               s.temperature AS temperature,
               s.humidity AS humidity
        ORDER BY s.date DESC
        """

        if limit:
            query += f" LIMIT {limit}"

        with self.driver.session() as session:
            result = session.run(query)
            return [dict(record) for record in result]

    def create_farm_geojson(self, farm_data):
        """
        農園データからGeoJSONを作成

        Args:
            farm_data: 農園データのリスト

        Returns:
            GeoJSON FeatureCollection
        """
        features = []

        for farm in farm_data:
            # ポイントジオメトリ
            geometry = {
                "type": "Point",
                "coordinates": [
                    float(farm["longitude"]),
                    float(farm["latitude"])
                ]
            }

            # プロパティ
            properties = {
                "name": farm["name"],
                "area": farm.get("area"),
                "observation_count": farm.get("observation_count", 0),
                "avg_ndvi": round(farm.get("avg_ndvi", 0), 4) if farm.get("avg_ndvi") else None,
                "avg_temperature": round(farm.get("avg_temperature", 2), 2) if farm.get("avg_temperature") else None,
                "first_observation": str(farm.get("first_observation")) if farm.get("first_observation") else None,
                "last_observation": str(farm.get("last_observation")) if farm.get("last_observation") else None,
                "export_time": datetime.now().isoformat()
            }

            feature = {
                "type": "Feature",
                "geometry": geometry,
                "properties": properties
            }

            features.append(feature)

        # FeatureCollection
        geojson = {
            "type": "FeatureCollection",
            "name": "Nanaka Farm Fields",
            "crs": {
                "type": "name",
                "properties": {
                    "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
                }
            },
            "features": features
        }

        return geojson

    def create_observations_geojson(self, observations):
        """
        観測データからGeoJSONを作成

        Args:
            observations: 観測データのリスト

        Returns:
            GeoJSON FeatureCollection
        """
        features = []

        for obs in observations:
            # ポイントジオメトリ
            geometry = {
                "type": "Point",
                "coordinates": [
                    float(obs["longitude"]),
                    float(obs["latitude"])
                ]
            }

            # プロパティ
            properties = {
                "farm_name": obs["farm_name"],
                "observation_date": str(obs["observation_date"]),
                "ndvi": round(obs["ndvi"], 4) if obs["ndvi"] else None,
                "temperature": round(obs["temperature"], 2) if obs["temperature"] else None,
                "humidity": round(obs["humidity"], 2) if obs["humidity"] else None,
                "ndvi_status": self._get_ndvi_status(obs["ndvi"]),
            }

            feature = {
                "type": "Feature",
                "geometry": geometry,
                "properties": properties
            }

            features.append(feature)

        # FeatureCollection
        geojson = {
            "type": "FeatureCollection",
            "name": "Satellite Observations",
            "crs": {
                "type": "name",
                "properties": {
                    "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
                }
            },
            "features": features
        }

        return geojson

    @staticmethod
    def _get_ndvi_status(ndvi):
        """
        NDVIから植生状態を判定

        Args:
            ndvi: NDVI値

        Returns:
            植生状態文字列
        """
        if ndvi is None:
            return "unknown"
        elif ndvi > 0.7:
            return "healthy"
        elif ndvi > 0.5:
            return "moderate"
        elif ndvi > 0.3:
            return "poor"
        else:
            return "very_poor"


def main():
    parser = argparse.ArgumentParser(
        description="Neo4jデータをGeoJSON形式でエクスポート"
    )
    parser.add_argument(
        "--output-dir",
        default="exports",
        help="出力ディレクトリ（デフォルト: exports）"
    )
    parser.add_argument(
        "--farms-only",
        action="store_true",
        help="農園データのみをエクスポート"
    )
    parser.add_argument(
        "--observations-limit",
        type=int,
        default=100,
        help="観測データの最大出力数（デフォルト: 100）"
    )

    args = parser.parse_args()

    # 出力ディレクトリ作成
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("GeoJSONエクスポート")
    print("=" * 70)

    # Neo4j接続
    print(f"\nNeo4jに接続中: {NEO4J_URI}")
    exporter = GeoJSONExporter(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

    try:
        # 農園データのエクスポート
        print("\n📍 農園データを取得中...")
        farm_data = exporter.fetch_farm_data()
        print(f"✓ {len(farm_data)} 件の農園データを取得")

        if farm_data:
            farm_geojson = exporter.create_farm_geojson(farm_data)
            farm_output = output_dir / "nanaka_farm_fields.geojson"

            with open(farm_output, 'w', encoding='utf-8') as f:
                json.dump(farm_geojson, f, ensure_ascii=False, indent=2)

            print(f"✓ 農園データをエクスポート: {farm_output}")
            print(f"  - フィーチャー数: {len(farm_geojson['features'])}")
        else:
            print("⚠️  農園データが見つかりませんでした")

        # 観測データのエクスポート（オプション）
        if not args.farms_only:
            print(f"\n🛰️  観測データを取得中（最大{args.observations_limit}件）...")
            observations = exporter.fetch_satellite_observations(args.observations_limit)
            print(f"✓ {len(observations)} 件の観測データを取得")

            if observations:
                obs_geojson = exporter.create_observations_geojson(observations)
                obs_output = output_dir / "satellite_observations.geojson"

                with open(obs_output, 'w', encoding='utf-8') as f:
                    json.dump(obs_geojson, f, ensure_ascii=False, indent=2)

                print(f"✓ 観測データをエクスポート: {obs_output}")
                print(f"  - フィーチャー数: {len(obs_geojson['features'])}")
            else:
                print("⚠️  観測データが見つかりませんでした")

        print("\n" + "=" * 70)
        print("✓ エクスポート完了")
        print("=" * 70)

        # QGISでの表示手順を表示
        print("\n📊 QGISでの表示手順:")
        print("1. QGISを起動")
        print("2. メニュー: レイヤ → レイヤの追加 → ベクタレイヤの追加")
        print(f"3. ファイル選択: {farm_output.absolute()}")
        print("4. (オプション) 観測データも追加")
        print("5. レイヤスタイルで色分け表示")
        print("\n詳細は docs/QGIS_VISUALIZATION.md を参照してください")

    except Exception as e:
        print(f"\n❌ エラー: {e}", file=sys.stderr)
        return 1
    finally:
        exporter.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
