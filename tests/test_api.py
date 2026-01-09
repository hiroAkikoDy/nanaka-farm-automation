"""
Flask APIサーバーのテスト
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch

# scriptsディレクトリをPYTHONPATHに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))


@pytest.fixture
def mock_neo4j_session():
    """Neo4jセッションのモック"""
    with patch('neo4j.GraphDatabase.driver') as mock_driver:
        mock_session = Mock()
        mock_driver.return_value.session.return_value = mock_session
        yield mock_session


def test_health_check_endpoint(mock_neo4j_session):
    """ヘルスチェックエンドポイントのテスト"""
    # Neo4jセッションのモック設定
    mock_neo4j_session.run.return_value = Mock()

    from api_server import app

    client = app.test_client()
    response = client.get('/api/health')

    assert response.status_code == 200
    data = response.get_json()
    assert 'status' in data
    assert 'timestamp' in data


def test_summary_endpoint(mock_neo4j_session):
    """サマリーエンドポイントのテスト"""
    # モックデータの設定
    mock_result = Mock()
    mock_result.single.return_value = {
        'totalFields': 1,
        'totalArea': 10000,
        'avgNDVI': 0.752
    }
    mock_neo4j_session.run.return_value = mock_result

    from api_server import app

    client = app.test_client()
    response = client.get('/api/summary')

    assert response.status_code == 200
    data = response.get_json()
    assert 'totalFields' in data
    assert 'totalArea' in data
    assert 'avgNDVI' in data


def test_ndvi_trend_endpoint(mock_neo4j_session):
    """NDVIトレンドエンドポイントのテスト"""
    # モックデータの設定
    mock_records = [
        {'date': '2026-01-01', 'avgNdvi': 0.68},
        {'date': '2026-01-02', 'avgNdvi': 0.71}
    ]
    mock_neo4j_session.run.return_value = iter(mock_records)

    from api_server import app

    client = app.test_client()
    response = client.get('/api/ndvi-trend?days=7')

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


def test_fields_endpoint(mock_neo4j_session):
    """圃場エンドポイントのテスト"""
    # モックデータの設定
    mock_records = [
        {
            'id': 1,
            'name': 'Nanaka Farm',
            'lat': 32.8032,
            'lon': 130.7075,
            'area': 10000,
            'ndvi': 0.752,
            'status': 'healthy'
        }
    ]
    mock_neo4j_session.run.return_value = iter(mock_records)

    from api_server import app

    client = app.test_client()
    response = client.get('/api/fields')

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


def test_cors_headers():
    """CORSヘッダーのテスト"""
    from api_server import app

    client = app.test_client()
    response = client.get('/api/health')

    assert 'Access-Control-Allow-Origin' in response.headers
