# Design - Gemini Live API PoC

## アーキテクチャ概要

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser                                  │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐   │
│  │   Microphone  │───▶│   WebSocket   │◀──▶│    Speaker    │   │
│  │   (PCM 16kHz) │    │    Client     │    │   (PCM 24kHz) │   │
│  └───────────────┘    └───────────────┘    └───────────────┘   │
└───────────────────────────────────────────────────────────────────┘
                              │ WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                               │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐   │
│  │   WebSocket   │───▶│ LiveRequest   │───▶│   ADK Agent   │   │
│  │   Endpoint    │    │    Queue      │    │   (Tutor)     │   │
│  └───────────────┘    └───────────────┘    └───────────────┘   │
│         ▲                                          │            │
│         │              Live Events                 │            │
│         └──────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────────┐
                              │ gRPC/HTTP
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              Gemini Live API                                     │
│              (gemini-live-2.5-flash-preview-native-audio)       │
└─────────────────────────────────────────────────────────────────┘
```

## 技術選定

### バックエンド

| 技術 | 選定理由 |
|------|----------|
| Python 3.11+ | ADK推奨バージョン |
| uv | 高速なパッケージ管理、ADK推奨 |
| FastAPI | 非同期WebSocketサポート、シンプル |
| google-adk | Google公式Agent Development Kit |
| google-genai | Gemini API クライアント |

### フロントエンド（PoC用簡易版）

| 技術 | 選定理由 |
|------|----------|
| HTML/JavaScript | 最小構成、依存なし |
| Web Audio API | ブラウザ標準の音声処理 |
| WebSocket API | リアルタイム双方向通信 |

## プロジェクト構成

```
poc/
├── server/
│   ├── tutor_agent/
│   │   ├── __init__.py          # from . import agent
│   │   ├── agent.py             # root_agent定義
│   │   └── prompts.py           # システムプロンプト
│   ├── main.py                  # FastAPI + WebSocket
│   ├── .env                     # 環境変数
│   └── pyproject.toml           # Python設定
├── client/
│   └── index.html               # テスト用Webページ
└── README.md                    # セットアップ手順
```

## エージェント設計

### tutor_agent

```python
# tutor_agent/agent.py
from google.adk.agents import Agent
from .prompts import SYSTEM_INSTRUCTION

root_agent = Agent(
    name="homework_tutor",
    model="gemini-live-2.5-flash-preview-native-audio",
    description="小学生向け宿題サポートエージェント",
    instruction=SYSTEM_INSTRUCTION,
)
```

### システムプロンプト

```python
# tutor_agent/prompts.py
SYSTEM_INSTRUCTION = """
あなたは小学校低学年（1〜3年生）の子供の宿題をサポートする優しいロボットです。

## 基本方針
- 答えを直接教えずに、質問で子供を導きます
- 子供が自分で考え、気づくプロセスを大切にします
- 平易な日本語で、短く分かりやすく話します
- 一緒に考える仲間として振る舞います

## 対話スタイル
- 「〜かな？」「〜だと思う？」という問いかけを使う
- 子供の回答を否定せず、「なるほど」「いいね」と受け止める
- 間違いに気づかせるヒントを段階的に出す

## 制約
- 長い説明は避ける（一度に1〜2文程度）
- 難しい言葉は使わない
- 計算の答えを直接言わない
"""
```

## API設計

### WebSocket Endpoint

**URL**: `ws://localhost:8000/ws/{user_id}`

**クライアント→サーバー（音声送信）**:
```json
{
  "mime_type": "audio/pcm",
  "data": "<base64エンコードされた音声データ>"
}
```

**クライアント→サーバー（テキスト送信）**:
```json
{
  "mime_type": "text/plain",
  "data": "こんにちは"
}
```

**サーバー→クライアント（応答）**:
```json
{
  "author": "agent",
  "is_partial": false,
  "turn_complete": false,
  "parts": [
    {"type": "audio/pcm", "data": "<base64>"},
    {"type": "text", "data": "こんにちは！"}
  ],
  "input_transcription": {"text": "こんにちは", "is_final": true},
  "output_transcription": {"text": "こんにちは！", "is_final": true}
}
```

## 音声仕様

### 入力音声（マイク）
- フォーマット: PCM (LINEAR16)
- サンプルレート: 16kHz
- チャンネル: モノラル
- ビット深度: 16bit

### 出力音声（スピーカー）
- フォーマット: PCM
- サンプルレート: 24kHz（Gemini Live API標準）
- チャンネル: モノラル

## RunConfig設定

```python
run_config = RunConfig(
    streaming_mode="bidi",
    session_resumption=types.SessionResumptionConfig(transparent=True),
    realtime_input_config=types.RealtimeInputConfig(
        automatic_activity_detection=types.AutomaticActivityDetection(
            start_of_speech_sensitivity=types.StartSensitivity.START_SENSITIVITY_LOW,
            end_of_speech_sensitivity=types.EndSensitivity.END_SENSITIVITY_HIGH,
        )
    ),
    response_modalities=["AUDIO"],
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Puck"  # 遊び心のある声（子供向け）
            )
        ),
        language_code="ja-JP",  # 日本語
    ),
    output_audio_transcription={},
    input_audio_transcription={},
)
```

## エラーハンドリング

### 接続エラー
- WebSocket切断時: 再接続を試みる（クライアント側）
- API接続エラー: エラーメッセージを返却

### 音声処理エラー
- 無効な音声データ: スキップして継続
- 音声認識失敗: 「もう一度言ってね」と応答

## セキュリティ考慮事項

### PoC段階での対応
- APIキーは `.env` で管理（gitignore対象）
- ローカル環境のみで実行

### 将来の対応（本格実装時）
- Secret Manager使用
- 認証・認可の実装
- レート制限

## パフォーマンス考慮事項

### 遅延最小化
- `response_modalities=["AUDIO"]` でテキスト生成をスキップ
- システムプロンプトは簡潔に
- WebSocket接続を維持（都度接続しない）

### 安定性
- ハートビート実装（30秒間隔）
- タスクの適切なクリーンアップ

## 代替案と採用理由

### 音声API選択

| 選択肢 | 利点 | 欠点 | 採否 |
|--------|------|------|------|
| Gemini Live API | 低遅延、双方向 | 新しいAPI | ✅ 採用 |
| Cloud Speech + TTS | 安定性 | 遅延大 | ❌ |
| OpenAI Realtime API | 高品質 | コスト高 | ❌ |

**採用理由**: プロジェクト要件のリアルタイム性を満たすため、Gemini Live APIを採用。

### 音声キャプチャ方式

| 選択肢 | 利点 | 欠点 | 採否 |
|--------|------|------|------|
| Web Audio API | ブラウザ標準 | 複雑 | ✅ 採用 |
| MediaRecorder API | シンプル | フォーマット制限 | ❌ |

**採用理由**: PCM形式での出力が必要なため、Web Audio APIを採用。
