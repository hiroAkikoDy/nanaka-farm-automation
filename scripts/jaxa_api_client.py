#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JAXA G-Portal API Client
JAXA G-Portalから衛星データ（GCOM-C/SGLI）を取得

参考資料:
- G-Portal: https://gportal.jaxa.jp/gpr/?lang=en
- gportal-python: https://gportal.readthedocs.io/
- GCOM-C Data Users Handbook: https://gportal.jaxa.jp/gpr/assets/mng_upload/GCOM-C/GCOM-C_SHIKISAI_Data_Users_Handbook_en.pdf
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

# gportal-python のインポート試行
try:
    import gportal
    GPORTAL_AVAILABLE = True
except ImportError:
    GPORTAL_AVAILABLE = False
    print("⚠️  gportal-pythonがインストールされていません", file=sys.stderr)
    print("   pip install gportal でインストールしてください", file=sys.stderr)

# データ保存先ディレクトリ
DATA_DIR = Path(__file__).parent.parent / "data" / "geotiff"
METADATA_DIR = Path(__file__).parent.parent / "data" / "metadata"


def ensure_directories():
    """必要なディレクトリを作成"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)


def get_gportal_credentials():
    """
    G-Portal認証情報を取得

    環境変数から取得:
    - GPORTAL_USERNAME: G-Portalユーザー名
    - GPORTAL_PASSWORD: G-Portalパスワード

    Returns:
        tuple: (username, password)
    """
    username = os.environ.get("GPORTAL_USERNAME", "")
    password = os.environ.get("GPORTAL_PASSWORD", "")

    if not username or not password:
        print("\n⚠️  G-Portal認証情報が設定されていません", file=sys.stderr)
        print("   環境変数 GPORTAL_USERNAME と GPORTAL_PASSWORD を設定してください", file=sys.stderr)
        print("   G-Portalユーザー登録: https://gportal.jaxa.jp/gpr/auth", file=sys.stderr)
        return None, None

    return username, password


def search_gcom_c_data_real(lat, lon, start_date, end_date, product_type="LST"):
    """
    GCOM-C/SGLIデータを実際のG-Portal APIで検索

    Args:
        lat: 緯度
        lon: 経度
        start_date: 開始日 (YYYY-MM-DD)
        end_date: 終了日 (YYYY-MM-DD)
        product_type: プロダクトタイプ ("LST", "NDVI", "VGI" 等)

    Returns:
        検索結果のプロダクトリスト
    """
    if not GPORTAL_AVAILABLE:
        return None

    try:
        # データセット辞書を取得
        datasets = gportal.datasets()

        # プロダクトタイプに応じたデータセットID取得
        dataset_mapping = {
            "LST": datasets["GCOM-C/SGLI"]["LEVEL2"]["Land area"]["L2-LST"],
            "NDVI": datasets["GCOM-C/SGLI"]["LEVEL2"]["Land area"]["L2-VGI"],  # VGIにNDVI含む
            "VGI": datasets["GCOM-C/SGLI"]["LEVEL2"]["Land area"]["L2-VGI"],
        }

        dataset_id = dataset_mapping.get(product_type)

        if not dataset_id:
            print(f"⚠️  未対応のプロダクトタイプ: {product_type}", file=sys.stderr)
            return None

        # バウンディングボックス設定（座標周辺 ±0.5度）
        bbox = [lon - 0.5, lat - 0.5, lon + 0.5, lat + 0.5]

        print(f"\n🔍 G-Portal検索:")
        print(f"   プロダクト: GCOM-C/SGLI {product_type}")
        print(f"   期間: {start_date} ～ {end_date}")
        print(f"   範囲: {bbox}")

        # データ検索
        res = gportal.search(
            dataset_ids=dataset_id,
            start_time=f"{start_date}T00:00:00",
            end_time=f"{end_date}T23:59:59",
            bbox=bbox,
            params={}
        )

        products = res.products()
        print(f"✓ {len(products)} 件のプロダクトが見つかりました")

        return products

    except Exception as e:
        print(f"✗ G-Portal検索エラー: {e}", file=sys.stderr)
        return None


def search_gcom_c_data_mock(lat, lon, start_date, end_date, product_type="LST"):
    """
    GCOM-C/SGLIデータ検索のモック実装

    Args:
        lat: 緯度
        lon: 経度
        start_date: 開始日
        end_date: 終了日
        product_type: プロダクトタイプ

    Returns:
        モックプロダクトリスト
    """
    print(f"\n🔍 G-Portal検索 (モックモード):")
    print(f"   プロダクト: GCOM-C/SGLI {product_type}")
    print(f"   期間: {start_date} ～ {end_date}")
    print(f"   座標: ({lat}, {lon})")

    # モックデータ生成
    mock_products = [
        {
            "product_id": f"GC1SG1_{start_date.replace('-', '')}01D01D_{product_type}.h5",
            "dataset": f"GCOM-C/SGLI/L2-{product_type}",
            "observation_date": start_date,
            "bbox": [lon - 0.5, lat - 0.5, lon + 0.5, lat + 0.5],
            "parameters": {
                "LST": 291.5,  # Kelvin → 18.35°C
                "NDVI": 0.75,
                "quality_flag": "good"
            },
            "file_size_mb": 245.8,
            "download_url": f"https://gportal.jaxa.jp/mock/GCOM-C/{product_type}/{start_date}.h5"
        }
    ]

    print(f"✓ {len(mock_products)} 件のプロダクトが見つかりました (モック)")

    return mock_products


def download_product_real(product, output_dir, username, password):
    """
    実際のG-Portal APIでプロダクトをダウンロード

    Args:
        product: プロダクトオブジェクト
        output_dir: 出力ディレクトリ
        username: G-Portalユーザー名
        password: G-Portalパスワード

    Returns:
        ダウンロードしたファイルパス
    """
    if not GPORTAL_AVAILABLE:
        return None

    try:
        # 認証情報設定
        gportal.username = username
        gportal.password = password

        print(f"\n📥 ダウンロード中: {product.product_name}")

        # ダウンロード実行
        downloaded_files = gportal.download([product], local_dir=str(output_dir))

        if downloaded_files:
            print(f"✓ ダウンロード完了: {downloaded_files[0]}")
            return Path(downloaded_files[0])

        return None

    except Exception as e:
        print(f"✗ ダウンロードエラー: {e}", file=sys.stderr)
        return None


def download_product_mock(product, output_dir):
    """
    プロダクトダウンロードのモック実装

    Args:
        product: モックプロダクトデータ
        output_dir: 出力ディレクトリ

    Returns:
        ダウンロードしたファイルパス（モック）
    """
    product_id = product["product_id"]
    output_path = output_dir / product_id

    print(f"\n📥 ダウンロード中 (モック): {product_id}")
    print(f"   URL: {product['download_url']}")
    print(f"   サイズ: {product['file_size_mb']} MB")

    # ダミーファイル作成（HDF5ヘッダー）
    with open(output_path, 'wb') as f:
        # HDF5マジックナンバー
        f.write(b'\x89HDF\r\n\x1a\n')
        # ダミーデータ
        f.write(b'\x00' * 10000)

    print(f"✓ ダウンロード完了 (モック): {output_path}")

    return output_path


def extract_metadata(product, file_path, is_mock=False):
    """
    プロダクトからメタデータを抽出

    Args:
        product: プロダクトオブジェクト or モックデータ
        file_path: ダウンロードファイルパス
        is_mock: モックモードかどうか

    Returns:
        メタデータ辞書
    """
    if is_mock:
        metadata = {
            "product_id": product["product_id"],
            "dataset": product["dataset"],
            "observation_date": product["observation_date"],
            "bbox": product["bbox"],
            "parameters": product["parameters"],
            "file_path": str(file_path),
            "file_size_mb": product["file_size_mb"],
            "download_time": datetime.now().isoformat(),
            "source": "mock"
        }
    else:
        # 実際のプロダクトからメタデータ抽出
        metadata = {
            "product_id": getattr(product, 'product_name', 'unknown'),
            "dataset": getattr(product, 'dataset_id', 'GCOM-C/SGLI'),
            "observation_date": getattr(product, 'start_time', datetime.now().isoformat()),
            "file_path": str(file_path),
            "download_time": datetime.now().isoformat(),
            "source": "gportal"
        }

    return metadata


def save_metadata_json(metadata, metadata_dir):
    """
    メタデータをJSON形式で保存

    Args:
        metadata: メタデータ辞書
        metadata_dir: メタデータ保存ディレクトリ

    Returns:
        保存したJSONファイルパス
    """
    product_id = metadata["product_id"].replace(".h5", "")
    json_path = metadata_dir / f"{product_id}_metadata.json"

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"✓ メタデータ保存: {json_path}")

    return json_path


def main():
    parser = argparse.ArgumentParser(
        description="JAXA G-PortalからGCOM-C/SGLIデータを取得"
    )
    parser.add_argument("--lat", type=float, required=True, help="緯度")
    parser.add_argument("--lon", type=float, required=True, help="経度")
    parser.add_argument("--days", type=int, default=7,
                       help="過去何日分のデータを取得するか（デフォルト: 7日）")
    parser.add_argument("--product", type=str, default="LST",
                       choices=["LST", "NDVI", "VGI"],
                       help="プロダクトタイプ（デフォルト: LST）")
    parser.add_argument("--mock", action="store_true",
                       help="モックモードで実行（API未登録時のテスト用）")
    parser.add_argument("--download", action="store_true",
                       help="データをダウンロードする")

    args = parser.parse_args()

    # ディレクトリ作成
    ensure_directories()

    # 検索期間の設定
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=args.days)

    print("\n" + "=" * 70)
    print("JAXA G-Portal データ取得")
    print("=" * 70)

    # モックモードまたは実APIモード
    if args.mock or not GPORTAL_AVAILABLE:
        if not args.mock:
            print("\n⚠️  gportal-pythonが利用できないため、モックモードで実行します")

        # モック検索
        products = search_gcom_c_data_mock(
            args.lat, args.lon,
            start_date.isoformat(), end_date.isoformat(),
            args.product
        )

        if products and args.download:
            for product in products:
                # モックダウンロード
                file_path = download_product_mock(product, DATA_DIR)

                # メタデータ抽出・保存
                metadata = extract_metadata(product, file_path, is_mock=True)
                save_metadata_json(metadata, METADATA_DIR)

                # 結果出力
                print(f"\n📄 取得データ:")
                print(json.dumps(metadata, indent=2, ensure_ascii=False))

    else:
        # 認証情報取得
        username, password = get_gportal_credentials()

        if not username or not password:
            print("\n❌ 認証情報が不足しています", file=sys.stderr)
            sys.exit(1)

        # 実API検索
        products = search_gcom_c_data_real(
            args.lat, args.lon,
            start_date.isoformat(), end_date.isoformat(),
            args.product
        )

        if products and args.download:
            for product in products[:3]:  # 最大3件まで
                # 実ダウンロード
                file_path = download_product_real(product, DATA_DIR, username, password)

                if file_path:
                    # メタデータ抽出・保存
                    metadata = extract_metadata(product, file_path, is_mock=False)
                    save_metadata_json(metadata, METADATA_DIR)

                    # 結果出力
                    print(f"\n📄 取得データ:")
                    print(json.dumps(metadata, indent=2, ensure_ascii=False))

    print("\n" + "=" * 70)
    print("✓ 処理完了")
    print("=" * 70)


if __name__ == "__main__":
    main()
