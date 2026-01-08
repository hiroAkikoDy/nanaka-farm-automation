#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
テスト用HDF5ファイル生成スクリプト
GCOM-C/SGLI形式のダミーデータを作成
"""

import h5py
import numpy as np
import sys
from pathlib import Path

# Windows環境でのUTF-8出力設定
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def create_test_hdf5(output_path, dataset_name="LST", size=100):
    """
    テスト用HDF5ファイルを作成

    Args:
        output_path: 出力ファイルパス
        dataset_name: データセット名
        size: データサイズ
    """
    with h5py.File(output_path, 'w') as f:
        # グループ作成
        image_data = f.create_group('Image_data')
        geometry_data = f.create_group('Geometry_data')

        # LSTデータ（地表面温度、Kelvin）
        if dataset_name == "LST":
            lst = np.random.normal(291.5, 3.0, (size, size))
            dset = image_data.create_dataset('LST', data=lst)
            dset.attrs['units'] = 'Kelvin'
            dset.attrs['description'] = 'Land Surface Temperature'

        # NDVIデータ
        elif dataset_name == "NDVI":
            ndvi = np.random.uniform(0.6, 0.85, (size, size))
            dset = image_data.create_dataset('NDVI', data=ndvi)
            dset.attrs['units'] = 'dimensionless'
            dset.attrs['description'] = 'Normalized Difference Vegetation Index'

        # 緯度経度データ
        lat_center = 32.8032
        lon_center = 130.7075

        lat = np.linspace(lat_center - 0.5, lat_center + 0.5, size)
        lon = np.linspace(lon_center - 0.5, lon_center + 0.5, size)

        lat_grid, lon_grid = np.meshgrid(lat, lon)

        geometry_data.create_dataset('Latitude', data=lat_grid)
        geometry_data.create_dataset('Longitude', data=lon_grid)

        # メタデータ
        f.attrs['product'] = 'GCOM-C/SGLI'
        f.attrs['observation_date'] = '2026-01-07'
        f.attrs['created_by'] = 'test script'

    print(f"✓ テストHDF5ファイル作成: {output_path}")

if __name__ == "__main__":
    data_dir = Path(__file__).parent.parent / "data" / "geotiff"
    data_dir.mkdir(parents=True, exist_ok=True)

    # LSTテストデータ
    create_test_hdf5(data_dir / "test_LST.h5", "LST")

    # NDVIテストデータ
    create_test_hdf5(data_dir / "test_NDVI.h5", "NDVI")
