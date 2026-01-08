# Hello Farm コマンド

Nanaka Farm の情報を表示します。

Pythonスクリプトを実行して農園情報を取得し、表示してください。

```bash
python scripts/farm_info.py --lat 32.8032 --lon 130.7075
```

このスクリプトは:
- Neo4jデータベースに接続して農園情報を取得
- 接続できない場合はダミーデータ（Nanaka Farm）を表示
- JSON形式で農園名、座標、タイムスタンプを出力
