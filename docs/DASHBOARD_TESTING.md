# Nanaka Farm Dashboard テスト手順

Flask REST API + React Dashboardの動作確認ガイド

---

## 📋 テスト前の準備

### 1. 必要な環境

- ✅ Python 3.11以上
- ✅ Neo4j Desktop（起動済み）
- ✅ Flask / flask-cors インストール済み
- ✅ モダンブラウザ（Chrome, Firefox, Edge等）

### 2. 依存関係の確認

```bash
# プロジェクトディレクトリに移動
cd C:\Users\Koga Hiroaki\Desktop\hiroaki_\workingFolder\nanaka-farm-automation

# 必要なパッケージがインストールされているか確認
pip list | grep -i flask
# flask                    3.1.2
# flask-cors               6.0.2
```

### 3. Neo4jの起動確認

```bash
# Neo4jブラウザでアクセス可能か確認
# http://localhost:7474

# または、Pythonでテスト
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password')); print('Neo4j接続OK')"
```

---

## 🚀 テスト手順

### ステップ1: Flask APIサーバー起動

#### 1-1. ターミナルを開く

```bash
cd C:\Users\Koga Hiroaki\Desktop\hiroaki_\workingFolder\nanaka-farm-automation
```

#### 1-2. APIサーバーを起動

```bash
python scripts/api_server.py
```

#### 期待される出力:

```
============================================================
🚀 Nanaka Farm API Server Starting...
============================================================
📡 API Server: http://localhost:5000
🗄️  Neo4j URI: bolt://localhost:7687
👤 Neo4j User: neo4j
------------------------------------------------------------
📍 Available Endpoints:
  GET /api/health          - ヘルスチェック
  GET /api/summary         - サマリー情報
  GET /api/ndvi-trend      - NDVI時系列データ
  GET /api/work-hours      - 圃場別作業時間
  GET /api/fields          - 圃場位置情報
------------------------------------------------------------
💡 Usage:
  curl http://localhost:5000/api/health
  curl http://localhost:5000/api/summary
============================================================
 * Serving Flask app 'api_server'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
Press CTRL+C to quit
```

> ⚠️ **重要**: このターミナルは閉じないでください。APIサーバーが起動したまま次のステップに進みます。

---

### ステップ2: API動作確認（別のターミナル）

新しいターミナルを開いて、以下のコマンドでAPIをテストします。

#### 2-1. ヘルスチェック

```bash
curl http://localhost:5000/api/health
```

**期待される応答:**
```json
{
  "status": "healthy",
  "neo4j": "connected",
  "timestamp": "2026-01-09T15:30:00.123456"
}
```

#### 2-2. サマリー情報

```bash
curl http://localhost:5000/api/summary
```

**期待される応答:**
```json
{
  "totalFields": 1,
  "totalArea": 10000,
  "monthlyWorkHours": 120,
  "avgNDVI": 0.7521
}
```

#### 2-3. NDVI時系列データ

```bash
curl http://localhost:5000/api/ndvi-trend?days=7
```

**期待される応答:**
```json
[
  {"date": "01/02", "ndvi": 0.7123},
  {"date": "01/03", "ndvi": 0.7345},
  {"date": "01/04", "ndvi": 0.7456},
  ...
]
```

#### 2-4. 圃場別作業時間

```bash
curl http://localhost:5000/api/work-hours
```

**期待される応答:**
```json
[
  {"field": "Nanaka Farm", "hours": 35},
  {"field": "圃場B", "hours": 30},
  ...
]
```

#### 2-5. 圃場位置情報

```bash
curl http://localhost:5000/api/fields
```

**期待される応答:**
```json
[
  {
    "id": 123,
    "name": "Nanaka Farm",
    "lat": 32.8032,
    "lon": 130.7075,
    "area": 10000,
    "ndvi": 0.7521,
    "status": "healthy"
  }
]
```

---

### ステップ3: Dashboardをブラウザで開く

#### 3-1. HTMLファイルを開く

**方法1: ダブルクリック**
```
C:\Users\Koga Hiroaki\Desktop\hiroaki_\workingFolder\nanaka-farm-automation\dashboard\index.html
```
をダブルクリックしてブラウザで開く

**方法2: コマンドライン**
```bash
start dashboard\index.html
```

#### 3-2. ブラウザの開発者ツールを開く

- **Chrome/Edge**: `F12` または `Ctrl+Shift+I`
- **Firefox**: `F12`

**Consoleタブを確認:**
- エラーがないか確認
- ネットワークリクエストが成功しているか確認

---

### ステップ4: Dashboard動作確認

#### 4-1. ローディング確認

ページを開くと、最初に以下が表示されます:
```
⏳ データを読み込み中...
```

#### 4-2. データ表示確認

**サマリーカード（4つ）:**
- 🏡 総圃場数: `1 圃場`
- 📏 総面積: `1.0 ha`
- ⏰ 今月の作業時間: `120 時間`
- 🌿 平均NDVI: `0.752`

**NDVI時系列グラフ:**
- 緑色の折れ線グラフが表示される
- X軸: 日付（01/01, 01/02, ...）
- Y軸: NDVI値（0-1の範囲）

**圃場別作業時間グラフ:**
- 紫色の棒グラフが表示される
- X軸: 圃場名
- Y軸: 作業時間（時間）

**地図（Leaflet）:**
- OpenStreetMapの地図が表示される
- Nanaka Farm（熊本県）の位置にマーカーが表示される
- マーカーをクリックするとポップアップが表示される
  - 農園名
  - 面積
  - NDVI値
  - 状態（健康/普通/注意）

#### 4-3. 更新機能の確認

ヘッダーの「🔄 更新」ボタンをクリック:
- データが再取得される
- 最終更新時刻が更新される

#### 4-4. 自動更新の確認

- 1分後に自動的にデータが更新される
- ブラウザのConsoleで以下のようなログが表示される:
  ```
  Fetching data from API...
  Data updated successfully
  ```

---

## ✅ 確認チェックリスト

### APIサーバー
- [ ] Flask APIサーバーが起動している
- [ ] Neo4jに接続できている
- [ ] `/api/health` エンドポイントが正常に応答
- [ ] `/api/summary` エンドポイントがデータを返す
- [ ] `/api/ndvi-trend` エンドポイントがデータを返す
- [ ] `/api/work-hours` エンドポイントがデータを返す
- [ ] `/api/fields` エンドポイントがデータを返す
- [ ] CORSエラーが発生していない

### Dashboard
- [ ] ページがロードされる
- [ ] 「データを読み込み中...」が表示される
- [ ] サマリーカード（4つ）が表示される
- [ ] NDVI時系列グラフが表示される
- [ ] 作業時間棒グラフが表示される
- [ ] 地図が表示される（OpenStreetMap）
- [ ] 圃場マーカーが地図上に表示される
- [ ] マーカーをクリックするとポップアップが開く
- [ ] 「🔄 更新」ボタンが動作する
- [ ] ブラウザのConsoleにエラーがない

---

## 🐛 トラブルシューティング

### 問題1: Neo4j接続エラー

**エラーメッセージ:**
```
ServiceUnavailable: Unable to connect to bolt://localhost:7687
```

**解決方法:**
1. Neo4j Desktopを起動
2. データベースが起動しているか確認
3. `.env`ファイルのNeo4j認証情報を確認

```bash
# .envファイルを確認
cat .env
# NEO4J_URI=bolt://localhost:7687
# NEO4J_USER=neo4j
# NEO4J_PASSWORD=password
```

---

### 問題2: CORS エラー

**ブラウザのConsoleに表示されるエラー:**
```
Access to fetch at 'http://localhost:5000/api/summary' from origin 'null' has been blocked by CORS policy
```

**原因:**
- Flask-CORSが正しくインストールされていない

**解決方法:**
```bash
pip install flask-cors
```

APIサーバーを再起動:
```bash
python scripts/api_server.py
```

---

### 問題3: データが表示されない

**ダッシュボードに「データがありません」と表示される**

**原因:**
- Neo4jにデータが存在しない
- APIエンドポイントがエラーを返している

**解決方法:**

1. **Neo4jにデータがあるか確認:**
```cypher
MATCH (f:Farm) RETURN f LIMIT 5;
MATCH (s:SatelliteData) RETURN s LIMIT 5;
```

2. **サンプルデータを投入:**
```bash
python scripts/store_neo4j.py --farm-info
```

3. **APIレスポンスを確認:**
```bash
curl http://localhost:5000/api/summary
curl http://localhost:5000/api/fields
```

---

### 問題4: 地図が表示されない

**症状:**
- 地図エリアが空白
- Consoleに `L is not defined` エラー

**解決方法:**
1. インターネット接続を確認（LeafletはCDNから読み込まれる）
2. ブラウザのキャッシュをクリア
3. ページをリロード（Ctrl+F5）

---

### 問題5: グラフが表示されない

**症状:**
- グラフエリアが空白
- Consoleに `Recharts is not defined` エラー

**解決方法:**
1. インターネット接続を確認（RechartsはCDNから読み込まれる）
2. ブラウザのキャッシュをクリア
3. ページをリロード（Ctrl+F5）

---

## 🔧 デバッグ方法

### APIサーバーのデバッグ

```bash
# デバッグモードで起動（既にデフォルトでON）
python scripts/api_server.py
```

各APIリクエストがターミナルに表示される:
```
127.0.0.1 - - [09/Jan/2026 15:30:00] "GET /api/summary HTTP/1.1" 200 -
127.0.0.1 - - [09/Jan/2026 15:30:01] "GET /api/ndvi-trend?days=7 HTTP/1.1" 200 -
```

### ブラウザのデバッグ

**Chrome/Edge DevTools:**
1. `F12`で開発者ツールを開く
2. **Console** タブ: JavaScriptエラーを確認
3. **Network** タブ: APIリクエストを確認
   - `/api/summary` の Status が 200 OK か確認
   - Response タブでレスポンス内容を確認
4. **Application** タブ: ページリソースを確認

---

## 📊 期待される動作

### 正常動作の確認ポイント

1. **APIサーバー:**
   - すべてのエンドポイントがHTTP 200を返す
   - JSONレスポンスが正しいフォーマット
   - Neo4jから実データを取得している

2. **Dashboard:**
   - ローディング → データ表示の流れがスムーズ
   - 全てのコンポーネントが正しく表示される
   - リアルタイムでNeo4jのデータが反映される
   - 更新ボタンで即座にデータが更新される

3. **データフロー:**
```
Neo4j Database
    ↓
Flask API Server (localhost:5000)
    ↓ (JSON over HTTP)
React Dashboard (browser)
    ↓
Charts & Map Display
```

---

## 🎯 次のステップ

### テスト完了後のタスク

1. **本番環境への移行:**
   - Gunicorn等のWSGIサーバーを使用
   - Nginxでリバースプロキシ設定
   - HTTPS対応

2. **機能追加:**
   - ユーザー認証
   - データのフィルタリング機能
   - PDFレポート生成
   - アラート通知

3. **パフォーマンス最適化:**
   - APIレスポンスのキャッシュ
   - Neo4jクエリの最適化
   - フロントエンドのバンドル最適化

---

## 📝 テスト完了報告

テストが完了したら、以下の情報を記録してください:

```markdown
## テスト結果

- 実施日時: 2026-01-09
- テスト実施者: Hiroaki Koga
- 環境:
  - OS: Windows 11
  - Python: 3.11
  - Flask: 3.1.2
  - Neo4j: 5.x
  - ブラウザ: Chrome 120

### 結果

- [ ] APIサーバー起動: ✅ / ❌
- [ ] Neo4j接続: ✅ / ❌
- [ ] 全エンドポイント動作: ✅ / ❌
- [ ] Dashboard表示: ✅ / ❌
- [ ] データ更新機能: ✅ / ❌

### 備考

- 特記事項があれば記載
```

---

## 📚 参考資料

- [Flask公式ドキュメント](https://flask.palletsprojects.com/)
- [Flask-CORS](https://flask-cors.readthedocs.io/)
- [React公式ドキュメント](https://react.dev/)
- [Recharts](https://recharts.org/)
- [Leaflet](https://leafletjs.com/)
- [Neo4j Python Driver](https://neo4j.com/docs/python-manual/current/)

---

## 更新履歴

- 2026-01-09: 初版作成
  - Flask REST API実装
  - React Dashboard実装
  - テスト手順整備
