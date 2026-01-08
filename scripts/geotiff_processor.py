#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GeoTIFF Processor
GeoTIFFファイルを読み込み、指定座標周辺のデータを抽出・解析

対応形式:
- GeoTIFF (.tif, .tiff)
- HDF5 (.h5) - GCOM-C/SGLI形式
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Windows環境でのUTF-8出力設定
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# ライブラリのインポート試行
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("⚠️  numpyがインストールされていません", file=sys.stderr)

try:
    import rasterio
    from rasterio.windows import Window
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False
    print("⚠️  rasterioがインストールされていません", file=sys.stderr)
    print("   pip install rasterio でインストールしてください", file=sys.stderr)

try:
    import h5py
    H5PY_AVAILABLE = True
except ImportError:
    H5PY_AVAILABLE = False
    print("⚠️  h5pyがインストールされていません (HDF5ファイル処理用)", file=sys.stderr)

try:
    import matplotlib
    matplotlib.use('Agg')  # GUI不要のバックエンド
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("⚠️  matplotlibがインストールされていません (可視化オプション用)", file=sys.stderr)


def read_geotiff_rasterio(file_path, lat, lon, buffer_km=5):
    """
    GeoTIFFファイルをrasterioで読み込み

    Args:
        file_path: GeoTIFFファイルパス
        lat: 中心緯度
        lon: 中心経度
        buffer_km: バッファ距離（km）

    Returns:
        data, metadata, stats
    """
    if not RASTERIO_AVAILABLE:
        raise ImportError("rasterioがインストールされていません")

    try:
        with rasterio.open(file_path) as src:
            # メタデータ取得
            metadata = {
                "driver": src.driver,
                "dtype": str(src.dtypes[0]),
                "nodata": src.nodata,
                "width": src.width,
                "height": src.height,
                "count": src.count,
                "crs": str(src.crs),
                "bounds": src.bounds,
            }

            # 座標変換（緯度経度 → ピクセル座標）
            py, px = src.index(lon, lat)

            # バッファ計算（おおよそ1km = 0.01度）
            buffer_pixels = int(buffer_km * 0.01 / abs(src.transform[0]))

            # ウィンドウ定義
            window = Window(
                max(0, px - buffer_pixels),
                max(0, py - buffer_pixels),
                min(buffer_pixels * 2, src.width),
                min(buffer_pixels * 2, src.height)
            )

            # データ読み込み
            data = src.read(1, window=window)

            # NoDataマスク適用
            if src.nodata is not None:
                data = np.ma.masked_equal(data, src.nodata)

            # 統計計算
            stats = calculate_statistics(data)

            return data, metadata, stats

    except Exception as e:
        raise RuntimeError(f"GeoTIFF読み込みエラー: {e}")


def read_hdf5_gcom_c(file_path, lat, lon, buffer_km=5, dataset_name="LST"):
    """
    GCOM-C/SGLI HDF5ファイルを読み込み

    Args:
        file_path: HDF5ファイルパス
        lat: 中心緯度
        lon: 中心経度
        buffer_km: バッファ距離（km）
        dataset_name: データセット名 (LST, NDVI等)

    Returns:
        data, metadata, stats
    """
    if not H5PY_AVAILABLE:
        raise ImportError("h5pyがインストールされていません")

    try:
        with h5py.File(file_path, 'r') as f:
            # ファイル構造確認
            print(f"\n📂 HDF5ファイル構造:")
            print_hdf5_structure(f, max_depth=2)

            # データセット検索（一般的なパス）
            possible_paths = [
                f'Image_data/{dataset_name}',
                f'Geophysical_data/{dataset_name}',
                dataset_name,
            ]

            data_path = None
            for path in possible_paths:
                if path in f:
                    data_path = path
                    break

            if not data_path:
                # モックデータの場合は生成
                print("⚠️  実データが見つかりません。モックデータを生成します。")
                data = generate_mock_data(dataset_name, buffer_km)
                metadata = {
                    "file": str(file_path),
                    "dataset": dataset_name,
                    "source": "mock",
                    "shape": data.shape
                }
            else:
                # データ読み込み
                dataset = f[data_path]
                data = dataset[:]

                metadata = {
                    "file": str(file_path),
                    "dataset": data_path,
                    "shape": dataset.shape,
                    "dtype": str(dataset.dtype),
                    "attrs": dict(dataset.attrs) if hasattr(dataset, 'attrs') else {}
                }

            # 統計計算
            stats = calculate_statistics(data)

            return data, metadata, stats

    except Exception as e:
        raise RuntimeError(f"HDF5読み込みエラー: {e}")


def print_hdf5_structure(hdf_file, prefix="", max_depth=3, current_depth=0):
    """HDF5ファイル構造を表示"""
    if current_depth >= max_depth:
        return

    for key in hdf_file.keys():
        item = hdf_file[key]
        print(f"{prefix}├── {key}")

        if isinstance(item, h5py.Group) and current_depth < max_depth - 1:
            print_hdf5_structure(item, prefix + "│   ", max_depth, current_depth + 1)


def generate_mock_data(dataset_name, buffer_km):
    """モックデータ生成"""
    size = int(buffer_km * 20)  # 適当なサイズ

    if dataset_name == "LST":
        # 地表面温度（Kelvin）のモックデータ
        mean_temp = 291.5  # 約18.35°C
        data = np.random.normal(mean_temp, 3.0, (size, size))
    elif dataset_name in ["NDVI", "VGI"]:
        # NDVIモックデータ（0～1の範囲）
        data = np.random.uniform(0.6, 0.85, (size, size))
    else:
        # 汎用モックデータ
        data = np.random.random((size, size))

    return data


def calculate_statistics(data):
    """
    統計値を計算

    Args:
        data: numpy配列

    Returns:
        統計情報辞書
    """
    if not NUMPY_AVAILABLE:
        return {"error": "numpy未インストール"}

    # マスク配列対応
    if isinstance(data, np.ma.MaskedArray):
        data_clean = data.compressed()
    else:
        data_clean = data.flatten()

    # 有効データチェック
    data_clean = data_clean[~np.isnan(data_clean)]

    if len(data_clean) == 0:
        return {
            "valid_pixels": 0,
            "error": "有効なデータがありません"
        }

    stats = {
        "valid_pixels": int(len(data_clean)),
        "mean": float(np.mean(data_clean)),
        "median": float(np.median(data_clean)),
        "std": float(np.std(data_clean)),
        "min": float(np.min(data_clean)),
        "max": float(np.max(data_clean)),
        "percentiles": {
            "25": float(np.percentile(data_clean, 25)),
            "50": float(np.percentile(data_clean, 50)),
            "75": float(np.percentile(data_clean, 75))
        }
    }

    return stats


def create_histogram(data, output_path, title="データ分布", xlabel="値"):
    """
    ヒストグラムを生成

    Args:
        data: numpy配列
        output_path: 出力ファイルパス
        title: グラフタイトル
        xlabel: X軸ラベル
    """
    if not MATPLOTLIB_AVAILABLE:
        print("⚠️  matplotlibが利用できないため、ヒストグラム生成をスキップします", file=sys.stderr)
        return None

    # データクリーニング
    if isinstance(data, np.ma.MaskedArray):
        data_clean = data.compressed()
    else:
        data_clean = data.flatten()

    data_clean = data_clean[~np.isnan(data_clean)]

    if len(data_clean) == 0:
        print("⚠️  有効なデータがないため、ヒストグラム生成をスキップします", file=sys.stderr)
        return None

    # ヒストグラム作成
    plt.figure(figsize=(10, 6))
    plt.hist(data_clean, bins=50, edgecolor='black', alpha=0.7)
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel('頻度', fontsize=12)
    plt.grid(True, alpha=0.3)

    # 統計情報を表示
    stats_text = f"平均: {np.mean(data_clean):.2f}\n標準偏差: {np.std(data_clean):.2f}"
    plt.text(0.02, 0.98, stats_text,
             transform=plt.gca().transAxes,
             verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"✓ ヒストグラム保存: {output_path}")
    return output_path


def process_file(file_path, lat, lon, buffer_km, dataset_name, create_viz):
    """
    ファイルを処理

    Args:
        file_path: ファイルパス
        lat: 緯度
        lon: 経度
        buffer_km: バッファ距離
        dataset_name: データセット名
        create_viz: 可視化を作成するか

    Returns:
        結果辞書
    """
    file_path = Path(file_path)

    # ファイル存在確認
    if not file_path.exists():
        raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")

    print(f"\n📊 ファイル処理: {file_path.name}")
    print(f"   座標: ({lat}, {lon})")
    print(f"   バッファ: {buffer_km}km")

    # ファイルタイプ判定
    suffix = file_path.suffix.lower()

    try:
        if suffix in ['.tif', '.tiff']:
            # GeoTIFF処理
            data, metadata, stats = read_geotiff_rasterio(file_path, lat, lon, buffer_km)

        elif suffix in ['.h5', '.hdf5']:
            # HDF5処理
            data, metadata, stats = read_hdf5_gcom_c(file_path, lat, lon, buffer_km, dataset_name)

        else:
            raise ValueError(f"未対応のファイル形式: {suffix}")

        # 結果作成
        result = {
            "file": str(file_path),
            "processing_time": datetime.now().isoformat(),
            "location": {
                "latitude": lat,
                "longitude": lon,
                "buffer_km": buffer_km
            },
            "metadata": metadata,
            "statistics": stats
        }

        # 可視化作成
        if create_viz and MATPLOTLIB_AVAILABLE and NUMPY_AVAILABLE:
            viz_dir = file_path.parent.parent / "visualizations"
            viz_dir.mkdir(parents=True, exist_ok=True)

            hist_path = viz_dir / f"{file_path.stem}_histogram.png"
            create_histogram(data, hist_path,
                           title=f"{dataset_name} データ分布 - {file_path.stem}",
                           xlabel=dataset_name)

            result["visualization"] = str(hist_path)

        return result

    except Exception as e:
        return {
            "file": str(file_path),
            "error": str(e),
            "processing_time": datetime.now().isoformat()
        }


def main():
    parser = argparse.ArgumentParser(
        description="GeoTIFF/HDF5ファイルを処理して統計情報を抽出"
    )
    parser.add_argument("file", type=str, help="GeoTIFF/HDF5ファイルパス")
    parser.add_argument("--lat", type=float, required=True, help="中心緯度")
    parser.add_argument("--lon", type=float, required=True, help="中心経度")
    parser.add_argument("--buffer", type=float, default=5.0,
                       help="バッファ距離（km、デフォルト: 5）")
    parser.add_argument("--dataset", type=str, default="LST",
                       help="データセット名（HDF5用、デフォルト: LST）")
    parser.add_argument("--viz", action="store_true",
                       help="ヒストグラムを生成")
    parser.add_argument("--output", type=str,
                       help="結果JSONの出力先（指定しない場合は標準出力）")

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("GeoTIFF/HDF5 プロセッサ")
    print("=" * 70)

    # 依存ライブラリチェック
    if not NUMPY_AVAILABLE:
        print("\n❌ エラー: numpyが必要です", file=sys.stderr)
        print("   pip install numpy でインストールしてください", file=sys.stderr)
        sys.exit(1)

    # ファイル処理
    result = process_file(
        args.file,
        args.lat,
        args.lon,
        args.buffer,
        args.dataset,
        args.viz
    )

    # 結果出力
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n✓ 結果保存: {args.output}")
    else:
        print("\n📄 処理結果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    print("\n" + "=" * 70)
    print("✓ 処理完了")
    print("=" * 70)


if __name__ == "__main__":
    main()
