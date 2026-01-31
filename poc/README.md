# Gemini Live API PoC

宿題コーチロボットの技術検証用プロジェクト。Google ADK + Gemini Live APIを使用したリアルタイム音声対話のPoCです。

## 前提条件

- Python 3.11+
- uv (パッケージマネージャー)
- Google AI Studio APIキー

## セットアップ

### 1. 環境変数の設定

```bash
cd poc/server
cp .env.example .env
```

`.env` ファイルを編集して、Google AI Studio APIキーを設定:

```
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your-actual-api-key-here
```

### 2. 仮想環境のアクティベート

```bash
cd poc/server
source .venv/bin/activate
```

### 3. サーバーの起動

```bash
cd poc/server
export SSL_CERT_FILE=$(python -m certifi)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. ブラウザでテスト

`poc/client/index.html` をブラウザで開く:

```bash
open poc/client/index.html
```

または、ブラウザで直接ファイルを開いてください。

## 使い方

1. 「接続」ボタンをクリック
2. マイクへのアクセスを許可
3. マイクボタンを押しながら話す
4. ボタンを離すと、エージェントが応答

## トラブルシューティング

### SSL証明書エラー

```bash
export SSL_CERT_FILE=$(python -m certifi)
```

### WebSocket接続エラー

- サーバーが起動しているか確認
- ポート8000が使用されていないか確認
- APIキーが正しく設定されているか確認

### マイクが使えない

- ブラウザのマイク許可を確認
- HTTPS接続が必要な場合あり（localhostは例外）

## 技術仕様

- **音声入力**: PCM 16kHz, 16bit, mono
- **音声出力**: PCM 24kHz, 16bit, mono
- **モデル**: gemini-live-2.5-flash-preview-native-audio
- **言語**: 日本語 (ja-JP)
- **音声**: Puck (遊び心のある声)

## ディレクトリ構成

```
poc/
├── server/
│   ├── tutor_agent/
│   │   ├── __init__.py
│   │   ├── agent.py      # エージェント定義
│   │   └── prompts.py    # システムプロンプト
│   ├── main.py           # FastAPI WebSocketサーバー
│   ├── .env              # 環境変数
│   ├── .env.example
│   └── pyproject.toml
├── client/
│   └── index.html        # テストページ
└── README.md
```
