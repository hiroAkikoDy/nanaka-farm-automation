#!/usr/bin/env python3
"""
Nanaka Farm API Server
Flask REST APIサーバー - Neo4jデータをダッシュボードに提供
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from neo4j import GraphDatabase
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

app = Flask(__name__)
CORS(app)  # CORS対応（開発用）

# Neo4j接続設定
NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'password')

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def get_neo4j_session():
    """Neo4jセッションを取得"""
    return driver.session()


@app.route('/api/summary', methods=['GET'])
def get_summary():
    """
    サマリー情報を取得

    Returns:
        {
            "totalFields": int,
            "totalArea": float,
            "monthlyWorkHours": int,
            "avgNDVI": float
        }
    """
    try:
        with get_neo4j_session() as session:
            # 総圃場数と総面積
            farm_query = """
            MATCH (f:Farm)
            RETURN COUNT(f) AS totalFields,
                   SUM(f.area) AS totalArea
            """
            farm_result = session.run(farm_query).single()

            # 今月の作業時間（モックデータ - 実際のWorkLogノードがあれば置き換え）
            monthly_hours = 120

            # 平均NDVI（直近7日間）
            ndvi_query = """
            MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
            WHERE s.date >= date() - duration('P7D')
            RETURN AVG(s.ndvi_avg) AS avgNDVI
            """
            ndvi_result = session.run(ndvi_query).single()

            return jsonify({
                'totalFields': farm_result['totalFields'] or 0,
                'totalArea': farm_result['totalArea'] or 0,
                'monthlyWorkHours': monthly_hours,
                'avgNDVI': round(ndvi_result['avgNDVI'] or 0, 4)
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ndvi-trend', methods=['GET'])
def get_ndvi_trend():
    """
    NDVI時系列データを取得

    Query Parameters:
        days: 取得日数（デフォルト: 7日）

    Returns:
        [
            {"date": "2026-01-01", "ndvi": 0.75},
            ...
        ]
    """
    try:
        days = request.args.get('days', default=7, type=int)

        with get_neo4j_session() as session:
            query = """
            MATCH (f:Farm)-[:HAS_OBSERVATION]->(s:SatelliteData)
            WHERE s.date >= date() - duration('P' + $days + 'D')
            WITH s.date AS date, AVG(s.ndvi_avg) AS avgNdvi
            RETURN date, avgNdvi
            ORDER BY date ASC
            """

            result = session.run(query, days=days)

            data = []
            for record in result:
                # Neo4j Dateオブジェクトを文字列に変換
                date_obj = record['date']
                if hasattr(date_obj, 'to_native'):
                    date_str = date_obj.to_native().strftime('%m/%d')
                else:
                    date_str = str(date_obj)

                data.append({
                    'date': date_str,
                    'ndvi': round(record['avgNdvi'], 4)
                })

            # データがない場合はモックデータを返す
            if not data:
                today = datetime.now()
                data = [
                    {
                        'date': (today - timedelta(days=i)).strftime('%m/%d'),
                        'ndvi': round(0.70 + (i * 0.01), 2)
                    }
                    for i in range(days-1, -1, -1)
                ]

            return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/work-hours', methods=['GET'])
def get_work_hours():
    """
    圃場別作業時間を取得

    Returns:
        [
            {"field": "圃場A", "hours": 35},
            ...
        ]
    """
    try:
        with get_neo4j_session() as session:
            # 実際のWorkLogノードがある場合はそちらを使用
            # ここではモックデータを返す
            query = """
            MATCH (f:Farm)
            RETURN f.name AS farmName
            ORDER BY f.name
            LIMIT 5
            """

            result = session.run(query)
            farms = [record['farmName'] for record in result]

            # 実データがない場合のモックデータ
            if not farms:
                farms = ['圃場A', '圃場B', '圃場C', '圃場D', '圃場E']

            # 各圃場にモック作業時間を割り当て
            data = []
            base_hours = 35
            for i, farm_name in enumerate(farms):
                data.append({
                    'field': farm_name,
                    'hours': base_hours - (i * 5)
                })

            return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/fields', methods=['GET'])
def get_fields():
    """
    圃場の位置情報とNDVI状態を取得

    Returns:
        [
            {
                "id": 1,
                "name": "Nanaka Farm",
                "lat": 32.8032,
                "lon": 130.7075,
                "area": 10000,
                "ndvi": 0.752,
                "status": "healthy"
            }
        ]
    """
    try:
        with get_neo4j_session() as session:
            query = """
            MATCH (f:Farm)
            OPTIONAL MATCH (f)-[:HAS_OBSERVATION]->(s:SatelliteData)
            WHERE s.date >= date() - duration('P7D')
            WITH f, AVG(s.ndvi_avg) AS avgNdvi
            RETURN
                id(f) AS id,
                f.name AS name,
                f.latitude AS lat,
                f.longitude AS lon,
                f.area AS area,
                avgNdvi AS ndvi,
                CASE
                    WHEN avgNdvi > 0.7 THEN 'healthy'
                    WHEN avgNdvi > 0.5 THEN 'moderate'
                    WHEN avgNdvi > 0.3 THEN 'poor'
                    ELSE 'very_poor'
                END AS status
            ORDER BY f.name
            """

            result = session.run(query)

            data = []
            for record in result:
                data.append({
                    'id': record['id'],
                    'name': record['name'],
                    'lat': record['lat'],
                    'lon': record['lon'],
                    'area': record['area'],
                    'ndvi': round(record['ndvi'] or 0, 4),
                    'status': record['status'] or 'unknown'
                })

            return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """ヘルスチェックエンドポイント"""
    try:
        with get_neo4j_session() as session:
            session.run("RETURN 1")
        return jsonify({
            'status': 'healthy',
            'neo4j': 'connected',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'neo4j': 'disconnected',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.teardown_appcontext
def close_driver(error):
    """アプリケーション終了時にNeo4jドライバをクローズ"""
    if error:
        print(f"Error during teardown: {error}")


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Nanaka Farm API Server Starting...")
    print("=" * 60)
    print(f"📡 API Server: http://localhost:5000")
    print(f"🗄️  Neo4j URI: {NEO4J_URI}")
    print(f"👤 Neo4j User: {NEO4J_USER}")
    print("-" * 60)
    print("📍 Available Endpoints:")
    print("  GET /api/health          - ヘルスチェック")
    print("  GET /api/summary         - サマリー情報")
    print("  GET /api/ndvi-trend      - NDVI時系列データ")
    print("  GET /api/work-hours      - 圃場別作業時間")
    print("  GET /api/fields          - 圃場位置情報")
    print("-" * 60)
    print("💡 Usage:")
    print("  curl http://localhost:5000/api/health")
    print("  curl http://localhost:5000/api/summary")
    print("=" * 60)

    # デバッグモードで起動（本番環境では False に設定）
    app.run(host='0.0.0.0', port=5000, debug=True)
