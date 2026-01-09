# コントリビューションガイド

Nanaka Farm Automation Systemへのコントリビューションに興味を持っていただき、ありがとうございます！

このガイドでは、プロジェクトへの貢献方法を説明します。

---

## 📋 目次

- [はじめに](#はじめに)
- [開発環境のセットアップ](#開発環境のセットアップ)
- [コーディング規約](#コーディング規約)
- [テスト](#テスト)
- [Pull Requestプロセス](#pull-requestプロセス)
- [Issue報告](#issue報告)
- [コミットメッセージ規約](#コミットメッセージ規約)

---

## はじめに

プロジェクトへのコントリビューションは、バグ報告、機能要望、ドキュメント改善、コードの寄贈など、さまざまな形で行うことができます。

### 行動規範

このプロジェクトは、すべての参加者が互いに尊重し合い、包括的なコミュニティを作ることを目指しています。参加する際は、以下の基本原則を守ってください：

- 建設的で思いやりのあるコミュニケーション
- 異なる視点や経験の尊重
- 建設的な批評の受け入れ
- コミュニティの利益を最優先

---

## 開発環境のセットアップ

### 1. リポジトリのForkとクローン

```bash
# GitHubでリポジトリをFork
# https://github.com/hiroAkikoDy/nanaka-farm-automation

# Forkしたリポジトリをクローン
git clone https://github.com/YOUR_USERNAME/nanaka-farm-automation.git
cd nanaka-farm-automation

# オリジナルリポジトリをupstreamとして追加
git remote add upstream https://github.com/hiroAkikoDy/nanaka-farm-automation.git
```

### 2. Python環境のセットアップ

```bash
# Python 3.11+ を確認
python --version

# 仮想環境の作成
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 依存パッケージのインストール
pip install -r requirements.txt

# 開発用パッケージのインストール
pip install pytest pytest-cov black flake8 mypy
```

### 3. Neo4jのセットアップ

- [Neo4j Desktop](https://neo4j.com/download/) をインストール
- 開発用データベースを作成
- `.env` ファイルを設定

```bash
cp .env.example .env
# .env を編集して認証情報を設定
```

### 4. ブランチ命名規則

機能開発やバグ修正を行う際は、以下の命名規則に従ってブランチを作成してください：

```bash
# 新機能
git checkout -b feature/short-description

# バグ修正
git checkout -b fix/short-description

# ドキュメント
git checkout -b docs/short-description

# リファクタリング
git checkout -b refactor/short-description
```

例:
```bash
git checkout -b feature/add-weather-forecast
git checkout -b fix/ndvi-calculation-error
git checkout -b docs/improve-api-documentation
```

---

## コーディング規約

### Python スタイルガイド

このプロジェクトは [PEP 8](https://pep8-ja.readthedocs.io/ja/latest/) に準拠します。

#### 必須ツール

- **Black**: コードフォーマッター
- **Flake8**: リンター
- **mypy**: 型チェック（オプション）

```bash
# コードフォーマット
black scripts/

# リント実行
flake8 scripts/

# 型チェック（オプション）
mypy scripts/
```

#### コーディング標準

1. **インポート順序**
   ```python
   # 標準ライブラリ
   import os
   import sys
   from datetime import datetime

   # サードパーティ
   import neo4j
   from flask import Flask

   # ローカル
   from scripts import farm_info
   ```

2. **Docstring（必須）**

   Google形式のdocstringを使用してください：

   ```python
   def calculate_ndvi(red: float, nir: float) -> float:
       """
       NDVIを計算します。

       Args:
           red: 赤色バンドの反射率（0-1）
           nir: 近赤外バンドの反射率（0-1）

       Returns:
           計算されたNDVI値（-1から1の範囲）

       Raises:
           ValueError: red + nir が0の場合

       Examples:
           >>> calculate_ndvi(0.1, 0.5)
           0.6666666666666666
       """
       if red + nir == 0:
           raise ValueError("red + nir cannot be zero")
       return (nir - red) / (nir + red)
   ```

3. **型ヒント（推奨）**

   ```python
   from typing import List, Dict, Optional

   def get_farms(limit: int = 10) -> List[Dict[str, any]]:
       """農園データを取得"""
       pass
   ```

4. **命名規則**
   - 関数・変数: `snake_case`
   - クラス: `PascalCase`
   - 定数: `UPPER_SNAKE_CASE`
   - プライベート: `_leading_underscore`

5. **行の長さ**
   - 最大127文字（Blackのデフォルト）
   - 可読性のために適宜改行

---

## テスト

### テストの実行

```bash
# 全テスト実行
pytest tests/ -v

# カバレッジ測定
pytest tests/ --cov=scripts --cov-report=html --cov-report=term

# 特定のテストのみ
pytest tests/test_api.py -k "test_health_check"
```

### テスト作成のガイドライン

1. **テストファイルの配置**
   ```
   tests/
   ├── __init__.py
   ├── test_api.py
   ├── test_data_processing.py
   └── test_geotiff_processor.py
   ```

2. **テスト関数の命名**
   ```python
   def test_function_name_expected_behavior():
       """テストの説明"""
       pass
   ```

3. **テストカバレッジ**
   - 最低80%のカバレッジを維持
   - 重要な機能は100%を目指す

4. **モックの使用**
   ```python
   from unittest.mock import Mock, patch

   @patch('neo4j.GraphDatabase.driver')
   def test_database_connection(mock_driver):
       """データベース接続のテスト"""
       pass
   ```

---

## Pull Requestプロセス

### 1. 最新のコードを取得

```bash
git fetch upstream
git checkout main
git merge upstream/main
```

### 2. 変更を実装

```bash
# 新しいブランチを作成
git checkout -b feature/your-feature

# 変更を実装
# ...

# テスト実行
pytest tests/ -v

# コードフォーマット
black scripts/
flake8 scripts/
```

### 3. コミット

```bash
git add .
git commit -m "feat: Add your feature description"
```

詳細は [コミットメッセージ規約](#コミットメッセージ規約) を参照してください。

### 4. プッシュ

```bash
git push origin feature/your-feature
```

### 5. Pull Request作成

1. GitHubでForkしたリポジトリを開く
2. "Compare & pull request" をクリック
3. 以下のテンプレートに従って記述:

```markdown
## 変更内容

<!-- 何を変更したか簡潔に説明 -->

## 変更理由

<!-- なぜこの変更が必要か -->

## テスト方法

<!-- この変更をどうテストしたか -->

## チェックリスト

- [ ] コードがPEP 8に準拠している
- [ ] docstringを追加した
- [ ] テストを追加/更新した
- [ ] テストが全て通過する
- [ ] ドキュメントを更新した（必要な場合）
```

### 6. レビュー対応

- レビュアーのコメントに対応
- 追加のコミットでプッシュ
- 承認されたらマージ

---

## Issue報告

### バグ報告

バグを見つけた場合は、以下のテンプレートを使用してIssueを作成してください：

```markdown
## バグの概要

<!-- バグの簡潔な説明 -->

## 再現手順

1. ...
2. ...
3. ...

## 期待される動作

<!-- 本来どうあるべきか -->

## 実際の動作

<!-- 実際に何が起こったか -->

## 環境

- OS: [Windows 11 / macOS Sonoma / Ubuntu 22.04]
- Python: [3.11.x]
- Neo4j: [5.x]
- ブラウザ: [Chrome 120]

## スクリーンショット

<!-- あれば追加 -->

## 追加情報

<!-- その他関連する情報 -->
```

### 機能要望

新機能の提案は大歓迎です：

```markdown
## 機能の概要

<!-- 提案する機能の説明 -->

## 動機

<!-- なぜこの機能が必要か -->

## 提案する実装方法

<!-- どのように実装できるか（オプション） -->

## 代替案

<!-- 他の実装方法（オプション） -->

## 追加情報

<!-- その他関連する情報 -->
```

---

## コミットメッセージ規約

### Conventional Commits

このプロジェクトは [Conventional Commits](https://www.conventionalcommits.org/) に準拠します。

### フォーマット

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type

- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメントのみの変更
- `style`: コードの意味に影響しない変更（フォーマット、セミコロンなど）
- `refactor`: バグ修正でも新機能でもないコード変更
- `perf`: パフォーマンス改善
- `test`: テストの追加・修正
- `chore`: ビルドプロセスやツールの変更

### Scope（オプション）

- `api`: APIサーバー関連
- `dashboard`: ダッシュボード関連
- `data`: データ処理関連
- `db`: データベース関連
- `docs`: ドキュメント

### 例

```bash
feat(api): NDVI異常検出エンドポイントを追加

Z-scoreベースの異常検出アルゴリズムを実装し、
/api/anomalies エンドポイントで公開

Closes #42
```

```bash
fix(dashboard): NDVI chart rendering issue on Safari

Chart.jsのバージョンを4.4.0にアップデートして
Safari 17での描画問題を修正

Fixes #38
```

```bash
docs: README.mdにQuickstartセクションを追加
```

---

## レビュープロセス

### レビュー基準

Pull Requestは以下の基準で評価されます：

1. **機能性**: コードが意図した通りに動作するか
2. **テスト**: 適切なテストが含まれているか
3. **コード品質**: コーディング規約に準拠しているか
4. **ドキュメント**: 変更が適切に文書化されているか
5. **CI/CD**: GitHub Actionsが全て通過するか

### レビュータイムライン

- 初回レビュー: 通常3営業日以内
- フォローアップ: 1-2営業日以内

---

## 質問・サポート

質問やサポートが必要な場合:

1. [GitHub Discussions](https://github.com/hiroAkikoDy/nanaka-farm-automation/discussions) で質問
2. [GitHub Issues](https://github.com/hiroAkikoDy/nanaka-farm-automation/issues) でバグ報告・機能要望
3. プロジェクトメンテナーに直接連絡

---

## ライセンス

このプロジェクトに貢献することにより、あなたの貢献がプロジェクトと同じMITライセンスの下でライセンスされることに同意したものとみなされます。

---

## 🙏 謝辞

プロジェクトへのコントリビューションに感謝します！あなたの貢献がNanaka Farm Automation Systemをより良くします。

---

<p align="center">
  Generated with <a href="https://claude.com/claude-code">Claude Code</a>
</p>
