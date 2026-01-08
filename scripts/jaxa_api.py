#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JAXA Earth API Data Retrieval Script
JAXA Earth APIから衛星データを取得してGeoTIFFとして保存

JAXA Earth API: https://data.earth.jaxa.jp/
使用可能なデータセット: https://data.earth.jaxa.jp/en/datasets/

このスクリプトはモック実装です。実際のAPIアクセスには
JAXA Earth API Pythonライブラリまたはpystac-clientが必要です。
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Windows環境でのUTF-8出力設定
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# データ保存先ディレクトリ
DATA_DIR = Path(__file__).parent.parent / "data" / "geotiff"
METADATA_DIR = Path(__file__).parent.parent / "data" / "metadata"


def ensure_directories():
    """必要なディレクトリを作成"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)


def search_jaxa_data(lat, lon, start_date, end_date, dataset="GCOM-C"):
    """
    JAXA Earth APIでデータを検索（モック実装）

    Args:
        lat: 緯度
        lon: 経度
        start_date: 開始日
        end_date: 終了日
        dataset: データセット名（GCOM-C, ALOS-3, GPM等）

    Returns:
        検索結果のメタデータリスト
    """
    print(f"\n🔍 JAXA Earth API データ検索:")
    print(f"   データセット: {dataset}")
    print(f"   座標: ({lat}, {lon})")
    print(f"   期間: {start_date} ～ {end_date}")

    # モック実装: 実際のAPIコールの代わりにダミーデータを生成
    # 実際の実装では pystac-client を使用:
    # from pystac_client import Client
    # catalog = Client.open("https://data.earth.jaxa.jp/stac")
    # search = catalog.search(
    #     bbox=[lon-0.1, lat-0.1, lon+0.1, lat+0.1],
    #     datetime=f"{start_date}/{end_date}",
    #     collections=[dataset]
    # )

    # ダミーデータ生成
    mock_results = [
        {
            "id": f"{dataset}_20260108_nanaka_farm",
            "collection": dataset,
            "datetime": "2026-01-08T02:30:00Z",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [lon - 0.1, lat - 0.1],
                    [lon + 0.1, lat - 0.1],
                    [lon + 0.1, lat + 0.1],
                    [lon - 0.1, lat + 0.1],
                    [lon - 0.1, lat - 0.1]
                ]]
            },
            "properties": {
                "temperature": 18.5,
                "humidity": 68.0,
                "ndvi_mean": 0.75,
                "cloud_coverage": 5.2
            },
            "assets": {
                "geotiff": {
                    "href": f"https://data.earth.jaxa.jp/mock/{dataset}/20260108/nanaka_farm.tif",
                    "type": "image/tiff; application=geotiff",
                    "title": "GeoTIFF Data"
                }
            }
        }
    ]

    print(f"✓ {len(mock_results)} 件のデータが見つかりました")
    return mock_results


def download_geotiff(item_metadata, output_dir):
    """
    GeoTIFFデータをダウンロード（モック実装）

    Args:
        item_metadata: アイテムのメタデータ
        output_dir: 出力ディレクトリ

    Returns:
        ダウンロードしたファイルのパス
    """
    item_id = item_metadata["id"]
    geotiff_url = item_metadata["assets"]["geotiff"]["href"]

    print(f"\n📥 GeoTIFFダウンロード:")
    print(f"   ID: {item_id}")
    print(f"   URL: {geotiff_url}")

    # モック実装: 実際のダウンロードの代わりにダミーファイルを作成
    # 実際の実装では requests や urllib を使用してダウンロード:
    # import requests
    # response = requests.get(geotiff_url)
    # with open(output_path, 'wb') as f:
    #     f.write(response.content)

    output_path = output_dir / f"{item_id}.tif"

    # ダミーGeoTIFFファイル作成（実際のGeoTIFFヘッダー付き）
    with open(output_path, 'wb') as f:
        # GeoTIFFマジックナンバー（リトルエンディアン）
        f.write(b'II*\x00')
        # ダミーデータ
        f.write(b'\x00' * 1000)

    print(f"✓ ダウンロード完了: {output_path}")
    return output_path


def save_metadata(item_metadata, metadata_dir):
    """
    メタデータをJSON形式で保存

    Args:
        item_metadata: アイテムのメタデータ
        metadata_dir: メタデータ保存ディレクトリ

    Returns:
        保存したメタデータファイルのパス
    """
    item_id = item_metadata["id"]
    metadata_path = metadata_dir / f"{item_id}_metadata.json"

    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(item_metadata, f, indent=2, ensure_ascii=False)

    print(f"✓ メタデータ保存: {metadata_path}")
    return metadata_path


def extract_observation_data(item_metadata):
    """
    メタデータから観測データを抽出

    Args:
        item_metadata: アイテムのメタデータ

    Returns:
        観測データ辞書
    """
    props = item_metadata["properties"]
    datetime_str = item_metadata["datetime"]

    # ISO形式の日時を日付のみに変換
    date_obj = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
    date_str = date_obj.strftime('%Y-%m-%d')

    return {
        "date": date_str,
        "temperature": props.get("temperature", 20.0),
        "humidity": props.get("humidity", 65.0),
        "ndvi_avg": props.get("ndvi_mean", 0.7),
        "cloud_coverage": props.get("cloud_coverage", 0.0)
    }


def main():
    parser = argparse.ArgumentParser(
        description="JAXA Earth APIから衛星データを取得"
    )
    parser.add_argument("--lat", type=float, required=True, help="緯度")
    parser.add_argument("--lon", type=float, required=True, help="経度")
    parser.add_argument("--days", type=int, default=7,
                       help="過去何日分のデータを取得するか（デフォルト: 7日）")
    parser.add_argument("--dataset", type=str, default="GCOM-C",
                       help="データセット名（デフォルト: GCOM-C）")
    parser.add_argument("--download", action="store_true",
                       help="GeoTIFFをダウンロードする")

    args = parser.parse_args()

    # ディレクトリ作成
    ensure_directories()

    # 検索期間の設定
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=args.days)

    print("\n" + "=" * 70)
    print("JAXA Earth API データ取得")
    print("=" * 70)

    # データ検索
    results = search_jaxa_data(
        args.lat,
        args.lon,
        start_date.isoformat(),
        end_date.isoformat(),
        args.dataset
    )

    if not results:
        print("\n⚠️  データが見つかりませんでした")
        sys.exit(0)

    # 結果を処理
    print(f"\n📊 取得結果:")
    print("=" * 70)

    for i, item in enumerate(results, 1):
        print(f"\nアイテム #{i}:")
        print(f"  ID: {item['id']}")
        print(f"  日時: {item['datetime']}")

        # メタデータ保存
        save_metadata(item, METADATA_DIR)

        # 観測データ抽出
        obs_data = extract_observation_data(item)
        print(f"  観測データ:")
        print(f"    日付: {obs_data['date']}")
        print(f"    温度: {obs_data['temperature']}℃")
        print(f"    湿度: {obs_data['humidity']}%")
        print(f"    NDVI平均: {obs_data['ndvi_avg']}")

        # GeoTIFFダウンロード（オプション）
        if args.download:
            geotiff_path = download_geotiff(item, DATA_DIR)

        # 観測データをJSONで出力（後続処理で使用可能）
        output_data = {
            "item_id": item["id"],
            "geotiff_downloaded": args.download,
            "observation": obs_data
        }

        # 標準出力にJSON出力（パイプで次のスクリプトに渡せる）
        print(f"\n📄 観測データJSON:")
        print(json.dumps(output_data, indent=2, ensure_ascii=False))

    print("\n" + "=" * 70)
    print("✓ 処理完了")
    print("=" * 70)


if __name__ == "__main__":
    main()
