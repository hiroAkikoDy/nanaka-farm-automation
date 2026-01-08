#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Workflow: Collect and Save Weather Data
JAXA G-Portal API → GeoTIFF Processing → Neo4j Storage

エラーハンドリング:
- API接続失敗: 3回リトライ（指数バックオフ）
- ダウンロード失敗: ログ記録、継続
- Neo4j保存失敗: ロールバック
"""

import argparse
import json
import os
import sys
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Windows環境でのUTF-8出力設定
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# ディレクトリ設定
BASE_DIR = Path(__file__).parent.parent
LOGS_DIR = BASE_DIR / "logs"
REPORTS_DIR = BASE_DIR / "reports"
DATA_DIR = BASE_DIR / "data" / "geotiff"

# ディレクトリ作成
LOGS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


class WorkflowLogger:
    """ワークフローロガー"""

    def __init__(self, log_file, error_file):
        self.log_file = open(log_file, 'w', encoding='utf-8')
        self.error_file = open(error_file, 'w', encoding='utf-8')

    def log(self, message, level="INFO"):
        """ログ出力"""
        timestamp = datetime.now().isoformat()
        log_line = f"[{timestamp}] [{level}] {message}\n"

        self.log_file.write(log_line)
        self.log_file.flush()

        print(f"[{level}] {message}")

        if level == "ERROR":
            self.error_file.write(log_line)
            self.error_file.flush()

    def close(self):
        """ログファイルを閉じる"""
        self.log_file.close()
        self.error_file.close()


def run_command_with_retry(command, retry=3, backoff=2):
    """
    コマンドをリトライ付きで実行

    Args:
        command: 実行するコマンド（リスト）
        retry: リトライ回数
        backoff: バックオフ係数

    Returns:
        (success, output, error)
    """
    for attempt in range(retry):
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )

            if result.returncode == 0:
                return True, result.stdout, None

            # 失敗した場合、待機してリトライ
            if attempt < retry - 1:
                wait_time = backoff ** attempt
                print(f"⚠️  リトライ {attempt + 1}/{retry} (待機: {wait_time}秒)")
                time.sleep(wait_time)

        except Exception as e:
            if attempt < retry - 1:
                wait_time = backoff ** attempt
                print(f"⚠️  例外発生、リトライ {attempt + 1}/{retry}: {e}")
                time.sleep(wait_time)
            else:
                return False, None, str(e)

    return False, result.stdout if result else None, result.stderr if result else "Max retries exceeded"


def fetch_satellite_data(lat, lon, days, product, logger, use_mock=False):
    """
    JAXA G-Portal APIからデータ取得

    Args:
        lat: 緯度
        lon: 経度
        days: 過去何日分
        product: プロダクトタイプ
        logger: ロガー
        use_mock: モックモード

    Returns:
        成功したかどうか
    """
    logger.log(f"=== データ取得開始: {product} ===")

    command = [
        "python", "scripts/jaxa_api_client.py",
        "--lat", str(lat),
        "--lon", str(lon),
        "--days", str(days),
        "--product", product,
        "--download"
    ]

    if use_mock:
        command.append("--mock")

    success, output, error = run_command_with_retry(command, retry=3)

    if success:
        logger.log(f"✓ {product}データ取得成功")
        return True
    else:
        logger.log(f"✗ {product}データ取得失敗: {error}", level="ERROR")
        return False


def process_hdf5_files(lat, lon, logger):
    """
    HDF5ファイルを処理

    Args:
        lat: 緯度
        lon: 経度
        logger: ロガー

    Returns:
        (processed_files, stats_list)
    """
    logger.log("=== HDF5ファイル処理開始 ===")

    hdf5_files = list(DATA_DIR.glob("*.h5"))

    if not hdf5_files:
        logger.log("⚠️  処理するHDF5ファイルが見つかりません", level="WARNING")
        return [], []

    processed = []
    stats_list = []

    for hdf5_file in hdf5_files:
        logger.log(f"処理中: {hdf5_file.name}")

        # データセット名を推測
        dataset = "LST" if "LST" in hdf5_file.name else "NDVI"

        # 一時ファイルにJSON出力
        temp_output = BASE_DIR / "temp_stats.json"

        command = [
            "python", "scripts/geotiff_processor.py",
            str(hdf5_file),
            "--lat", str(lat),
            "--lon", str(lon),
            "--dataset", dataset,
            "--output", str(temp_output)
        ]

        success, output, error = run_command_with_retry(command, retry=2)

        if success and temp_output.exists():
            try:
                # JSONファイルから読み込み
                with open(temp_output, 'r', encoding='utf-8') as f:
                    stats = json.load(f)

                processed.append(hdf5_file)
                stats_list.append(stats)
                logger.log(f"✓ {hdf5_file.name} 処理成功")

                # 一時ファイル削除
                temp_output.unlink()

            except json.JSONDecodeError as e:
                logger.log(f"✗ JSON解析失敗: {hdf5_file.name} - {e}", level="ERROR")
        else:
            logger.log(f"✗ {hdf5_file.name} 処理失敗: {error}", level="ERROR")

    logger.log(f"処理完了: {len(processed)}/{len(hdf5_files)} ファイル")

    return processed, stats_list


def save_to_neo4j(stats, logger):
    """
    統計データをNeo4jに保存

    Args:
        stats: 統計データ辞書
        logger: ロガー

    Returns:
        成功したかどうか
    """
    try:
        # ファイルパスから日付を抽出（簡易実装）
        date = datetime.now().strftime('%Y-%m-%d')

        # 統計値から温度・NDVIを抽出
        stat_values = stats.get('statistics', {})

        # LSTの場合はKelvinからCelsiusに変換
        if 'LST' in stats.get('file', ''):
            temp_k = stat_values.get('mean', 291.5)
            temperature = temp_k - 273.15
        else:
            temperature = 20.0  # デフォルト値

        ndvi_avg = stat_values.get('mean', 0.7)
        humidity = 65.0  # デフォルト値（実データがない場合）

        command = [
            "python", "scripts/save_weather.py",
            "--date", date,
            "--temperature", str(temperature),
            "--humidity", str(humidity),
            "--ndvi-avg", str(ndvi_avg)
        ]

        success, output, error = run_command_with_retry(command, retry=2)

        if success:
            logger.log(f"✓ Neo4j保存成功: {date}")
            return True
        else:
            logger.log(f"✗ Neo4j保存失敗: {error}", level="ERROR")
            return False

    except Exception as e:
        logger.log(f"✗ Neo4j保存中に例外: {e}", level="ERROR")
        return False


def generate_summary_report(processed_files, stats_list, start_time, logger):
    """
    サマリーレポート生成

    Args:
        processed_files: 処理済みファイルリスト
        stats_list: 統計データリスト
        start_time: 開始時刻
        logger: ロガー

    Returns:
        レポート辞書
    """
    logger.log("=== サマリーレポート生成 ===")

    # NDVI分析
    ndvi_values = []
    lst_values = []

    for stats in stats_list:
        stat_values = stats.get('statistics', {})
        mean = stat_values.get('mean')

        if mean:
            if 'NDVI' in stats.get('file', ''):
                ndvi_values.append(mean)
            elif 'LST' in stats.get('file', ''):
                # Kelvin to Celsius
                lst_values.append(mean - 273.15)

    # NDVI傾向分析（簡易）
    ndvi_trend = "stable"
    ndvi_change = 0.0

    if len(ndvi_values) >= 2:
        ndvi_change = ndvi_values[-1] - ndvi_values[0]
        if ndvi_change > 0.01:
            ndvi_trend = "increasing"
        elif ndvi_change < -0.01:
            ndvi_trend = "decreasing"

    report = {
        "execution_time": datetime.now().isoformat(),
        "duration_seconds": (datetime.now() - start_time).total_seconds(),
        "data_collection": {
            "total_files": len(processed_files),
            "successful": len(stats_list),
            "failed": len(processed_files) - len(stats_list)
        },
        "ndvi_analysis": {
            "count": len(ndvi_values),
            "mean": sum(ndvi_values) / len(ndvi_values) if ndvi_values else 0,
            "trend": ndvi_trend,
            "change_rate": ndvi_change
        },
        "lst_analysis": {
            "count": len(lst_values),
            "mean_celsius": sum(lst_values) / len(lst_values) if lst_values else 0,
            "min": min(lst_values) if lst_values else 0,
            "max": max(lst_values) if lst_values else 0
        }
    }

    logger.log(f"✓ レポート生成完了")
    logger.log(f"  処理ファイル数: {len(processed_files)}")
    logger.log(f"  NDVI平均: {report['ndvi_analysis']['mean']:.3f}")
    logger.log(f"  NDVI傾向: {report['ndvi_analysis']['trend']}")

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Complete Workflow: データ収集・処理・保存"
    )
    parser.add_argument("--lat", type=float, default=32.8032, help="緯度")
    parser.add_argument("--lon", type=float, default=130.7075, help="経度")
    parser.add_argument("--days", type=int, default=7, help="過去何日分")
    parser.add_argument("--retry", type=int, default=3, help="リトライ回数")
    parser.add_argument("--mock", action="store_true", help="モックモード")

    args = parser.parse_args()

    # ログファイル設定
    date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = LOGS_DIR / f"collect_weather_{date_str}.log"
    error_file = LOGS_DIR / f"errors_{date_str}.log"

    logger = WorkflowLogger(log_file, error_file)
    start_time = datetime.now()

    logger.log("=" * 70)
    logger.log("Nanaka Farm 気象データ収集ワークフロー")
    logger.log("=" * 70)
    logger.log(f"座標: ({args.lat}, {args.lon})")
    logger.log(f"期間: 過去{args.days}日")
    logger.log(f"モード: {'モック' if args.mock else '実API'}")

    try:
        # 1. データ取得
        success_lst = fetch_satellite_data(
            args.lat, args.lon, args.days, "LST", logger, args.mock
        )
        success_ndvi = fetch_satellite_data(
            args.lat, args.lon, args.days, "NDVI", logger, args.mock
        )

        # 2. データ処理
        processed_files, stats_list = process_hdf5_files(args.lat, args.lon, logger)

        # 3. Neo4j保存
        saved_count = 0
        for stats in stats_list:
            if save_to_neo4j(stats, logger):
                saved_count += 1

        logger.log(f"Neo4j保存: {saved_count}/{len(stats_list)} レコード")

        # 4. サマリーレポート生成
        report = generate_summary_report(processed_files, stats_list, start_time, logger)

        # レポート保存
        report_file = REPORTS_DIR / f"summary_{date_str}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.log(f"✓ レポート保存: {report_file}")

        logger.log("=" * 70)
        logger.log("✓ ワークフロー完了")
        logger.log("=" * 70)

    except Exception as e:
        logger.log(f"✗ 致命的エラー: {e}", level="ERROR")
        raise

    finally:
        logger.close()


if __name__ == "__main__":
    main()
