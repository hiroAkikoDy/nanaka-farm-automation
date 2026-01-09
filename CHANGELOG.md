# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Prometheus metrics エクスポート機能
- Grafana ダッシュボードテンプレート
- 複数農園の同時管理機能
- 機械学習による収穫量予測

---

## [1.0.0] - 2026-01-09

### Added

#### Phase 10: Dashboard & REST API
- **Flask REST API サーバー** (scripts/api_server.py)
  - 5つのエンドポイント: `/health`, `/summary`, `/ndvi-trend`, `/work-hours`, `/fields`
  - CORS対応
  - Neo4jデータベース統合
- **Chart.js Dashboard** (dashboard/index.html - 575行)
  - NDVIトレンドグラフ（折れ線グラフ）
  - 圃場別作業時間（棒グラフ）
  - Leaflet.js地図表示
  - インテリジェントフォールバック（API障害時にモックデータ使用）
  - 60秒自動更新機能

#### Phase 9: Neo4j可視化クエリ
- **5種類のCypherクエリファイル** (queries/visualization/)
  - `01_farm_overview.cypher` - 農園全体構造の可視化
  - `02_temporal_data.cypher` - 時系列データ分析
  - `03_work_density.cypher` - データ密度ヒートマップ
  - `04_seasonal_pattern.cypher` - 季節パターン分析
  - `05_anomaly_detection.cypher` - Z-scoreベース異常検出

#### Phase 8: GeoJSON/QGIS連携
- **GeoJSONエクスポート機能** (scripts/export_geojson.py - 315行)
  - RFC 7946準拠のGeoJSON出力
  - 農園フィーチャーと観測データの2ファイル生成
  - NDVI状態に基づく自動分類
- **QGIS可視化ガイド** (docs/QGIS_VISUALIZATION.md)
  - レイヤースタイル設定手順
  - GeoTIFFオーバーレイ方法

#### 自動化・スケジューリング
- **週次自動実行スケジューラー** (scripts/scheduler.py)
  - 毎週月曜 8:00 自動実行
  - エラー時のメール通知機能
  - バックグラウンド実行対応

#### JAXA衛星データ統合
- **JAXA G-Portal API クライアント** (scripts/jaxa_api_client.py)
  - GCOM-C/SGLI データ取得（LST, NDVI）
  - HDF5ファイル自動ダウンロード
  - メタデータJSON出力
- **GeoTIFF/HDF5 プロセッサー** (scripts/geotiff_processor.py)
  - 統計情報抽出（平均、中央値、標準偏差）
  - ヒストグラム生成
  - 座標ベースのデータ抽出

#### ドキュメント
- **包括的ドキュメント作成**
  - `QUICKSTART.md` - 3ステップ起動ガイド
  - `TEST_REPORT.md` - Phase 8-10統合テストレポート (6/6合格)
  - `docs/DASHBOARD_TESTING.md` - ダッシュボード完全テストガイド
  - `docs/GPORTAL_REAL_API_SETUP.md` - JAXA API設定ガイド
  - `docs/SCHEDULER.md` - スケジューラー詳細仕様

#### インフラ・設定
- **環境変数管理** (.env)
  - JAXA G-Portal認証情報
  - Neo4j接続設定
  - SMTPメール通知設定
- **.gitignore** - 機密情報の除外設定

### Changed
- Neo4jデータモデルの標準化
  - `Farm` ノード: name, latitude, longitude, area
  - `SatelliteData` ノード: date, temperature, humidity, ndvi_avg
  - `HAS_OBSERVATION` リレーション

### Fixed
- Windows環境でのUTF-8出力エンコーディング問題
- Neo4j接続エラー時のフォールバック処理
- HDF5ファイル読み込み時のデータセット検出

### Security
- .envファイルの.gitignore追加
- 認証情報のハードコーディング削除
- 環境変数による設定管理

---

## [0.2.0] - 2026-01-07

### Added
- **完全自動化ワークフロー** (scripts/collect_and_save_workflow.py)
  - JAXA API → データ処理 → Neo4j保存の一括実行
  - モックモード/実APIモード切替
- **Claude Codeカスタムコマンド**
  - `/collect-weather-data` - 気象データ収集自動化

### Changed
- HDF5データ処理の高速化
- エラーハンドリングの改善

---

## [0.1.0] - 2026-01-06

### Added
- **基礎システム実装**
  - Neo4jデータベーススキーマ
  - 農園情報管理 (scripts/farm_info.py)
  - 衛星観測データ保存 (scripts/save_weather.py)
  - データクエリ機能 (scripts/query_data.py)
- **Cypherクエリサンプル** (queries/test.cypher)
- **Claude Code フック**
  - afterCodeChange.ts - Cypher構文チェック

### Infrastructure
- プロジェクト構造の確立
- Git リポジトリ初期化
- 基本ドキュメント (README.md)

---

## リリースタイプ

- **Major (X.0.0)**: 破壊的変更
- **Minor (0.X.0)**: 後方互換性のある新機能
- **Patch (0.0.X)**: 後方互換性のあるバグ修正

---

## リンク

- [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
- [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
- [GitHub Releases](https://github.com/hiroAkikoDy/nanaka-farm-automation/releases)

---

<p align="center">
  Generated with <a href="https://claude.com/claude-code">Claude Code</a>
</p>
