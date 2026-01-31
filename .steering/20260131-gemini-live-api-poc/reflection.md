# Reflection - Gemini Live API PoC

**日付**: 2026-01-31
**ステータス**: ✅ 基本動作確認完了

---

## 実施内容

### 完了したタスク

1. **環境セットアップ**
   - Python 3.11 + uv による仮想環境構築
   - google-adk 1.23.0、FastAPI、uvicorn等のインストール
   - Vertex AI認証設定（ADC）

2. **エージェント実装**
   - `tutor_agent/` ディレクトリ構造作成
   - ソクラテス式対話用システムプロンプト作成
   - ADK Agent定義（root_agent）

3. **WebSocketサーバー実装**
   - FastAPI + WebSocketエンドポイント
   - LiveRequestQueue による双方向通信
   - 音声データの送受信処理

4. **クライアント実装**
   - Web Audio APIによるマイク入力（PCM 16kHz）
   - WebSocket接続・音声送信
   - 音声再生機能（PCM 24kHz）

### 未完了タスク

- Vertex AI Live APIへの接続確認
- 日本語音声対話のテスト
- 遅延計測・安定性確認

---

## 発見した課題

### 1. Vertex AI Live APIへのアクセス制限

**問題**:
Vertex AI Live APIモデル（`gemini-live-2.5-flash-native-audio`）へのアクセスがプロジェクトで有効化されていない。

**エラーメッセージ**:
```
Publisher Model `projects/homework-coach-robo/locations/us-central1/publishers/google/models/gemini-live-2.5-flash-native-audio` not found
```

**原因**:
- Vertex AI Live APIはプレビュー段階
- プロジェクトで明示的なアクセス許可が必要な可能性

**対策**:
1. Vertex AI Model GardenでLive APIモデルを有効化
2. または、Google AI Studio APIキーを使用（すぐ動作可能）

### 2. ADK APIの変更

**問題**:
スキルファイル（`.claude/skills/google-adk-live/SKILL.md`）のサンプルコードが、ADK 1.23.0のAPIと異なっていた。

**変更点**:
- `InMemoryRunner` → `Runner` + `InMemorySessionService`
- `runner.run_live(session, queue, config)` → `runner.run_live(user_id, session_id, live_request_queue, run_config)`

**対策**:
- ADK公式ドキュメント（Context7経由）を参照して修正
- スキルファイルの更新が必要

### 3. テキストモードでの動作確認

**発見**:
- Vertex AI自体は正常に動作（テキストモードで確認済み）
- 問題はLive API特有のアクセス制限

---

## 技術的な学び

### 1. ADK構成パターン

```python
# 正しいパターン（ADK 1.23.0）
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

session_service = InMemorySessionService()
runner = Runner(
    app_name="app_name",
    agent=root_agent,
    session_service=session_service,
)

# run_liveの呼び出し
async for event in runner.run_live(
    user_id=user_id,
    session_id=session_id,
    live_request_queue=live_request_queue,
    run_config=run_config,
):
    # イベント処理
```

### 2. RunConfigの設定

```python
from google.adk.agents.run_config import RunConfig, StreamingMode

run_config = RunConfig(
    streaming_mode=StreamingMode.BIDI,
    response_modalities=["AUDIO"],
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Puck"
            )
        ),
        language_code="ja-JP",
    ),
    input_audio_transcription=types.AudioTranscriptionConfig(),
    output_audio_transcription=types.AudioTranscriptionConfig(),
)
```

### 3. Vertex AI Live APIモデル名

- 一般利用可能: `gemini-live-2.5-flash-native-audio`
- プレビュー版: `gemini-live-2.5-flash-preview-native-audio-09-2025`

### 4. 必要なGCP API

- `aiplatform.googleapis.com` (Vertex AI API)
- `generativelanguage.googleapis.com` (Generative Language API)

### 5. モデル名の違い

ADKサンプル（bidi-demo）の調査結果:

| プラットフォーム | モデル名 |
|-----------------|---------|
| Vertex AI (GA版) | `gemini-live-2.5-flash-native-audio` |
| Gemini Live API | `gemini-2.5-flash-native-audio-preview-12-2025` |

### 6. RunConfig設定

ネイティブオーディオモデルでは`speech_config`は不要。参考実装通りの設定:

```python
run_config = RunConfig(
    streaming_mode=StreamingMode.BIDI,
    response_modalities=["AUDIO"],
    input_audio_transcription=types.AudioTranscriptionConfig(),
    output_audio_transcription=types.AudioTranscriptionConfig(),
    session_resumption=types.SessionResumptionConfig(),
)
```

### 7. 音声mime_type

正しい形式: `audio/pcm;rate=16000` (サンプルレート付き)

---

## 次のアクション

### 2026-01-31 16:38 更新: 問題解決進捗

#### 完了した修正

1. **モデル名を最新版に修正**
   - 旧: `gemini-2.5-flash-native-audio-preview-12-2025`
   - 新: `gemini-2.5-flash-native-audio-latest` (AI Studio用)
   - 参照: `refs/adk-python/contributing/samples/live_bidi_streaming_single_agent/agent.py`

2. **Live API直接接続テスト成功**
   - `test_connection.py`で確認
   - 音声データ（PCM 24kHz）を正常に受信
   - 日本語テキスト入力→音声応答が機能

3. **RunConfigの簡略化**
   - ADK Web Server (`adk_web_server.py`) と同じシンプルな設定に変更
   - `StreamingMode.BIDI`等の明示的指定を削除

4. **ADK DevUI起動確認**
   - `adk web tutor_agent` で正常起動

#### 未完了（ブラウザ手動テスト必要）

1. ADK DevUIでの音声ストリーミングテスト
2. カスタムサーバーでのWebSocket+音声テスト

### テスト手順

#### 方法1: ADK DevUI（推奨）
```bash
cd poc/server
source .venv/bin/activate
adk web tutor_agent
```
- ブラウザで http://127.0.0.1:8000 にアクセス
- 左上で `tutor_agent` を選択
- Token Streamingトグルを有効化
- マイクボタンをクリックして音声送信

#### 方法2: カスタムサーバー
```bash
cd poc/server
source .venv/bin/activate
python main.py
```
- ブラウザで http://127.0.0.1:8000 にアクセス
- 「接続」ボタンをクリック
- マイクボタンを長押しして音声送信

### 後続タスク

1. 上記テストで音声対話の成功を確認
2. 遅延計測（目標: 2秒以内）
3. 5分間連続対話の安定性確認
4. 検証結果のドキュメント化

---

## スキルファイル更新提案

`.claude/skills/google-adk-live/SKILL.md` を以下の点で更新すべき:

1. ADK 1.23.0対応のAPIパターンに更新
2. `Runner` + `InMemorySessionService` パターンを記載
3. `run_live()` の新しいシグネチャを記載
4. Vertex AI Live APIのアクセス有効化手順を追加

---

## 参考リンク

- [ADK Streaming Dev Guide](https://google.github.io/adk-docs/streaming/dev-guide/part1/)
- [Vertex AI Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)
- [Gemini Live API Models](https://ai.google.dev/gemini-api/docs/models#live-api)

---

## 2026-01-31 最終結果

### ✅ 音声ストリーミング動作確認成功

**テスト方法**: ADK DevUI (`adk web .`)

**確認事項**:
1. **Live API接続**: ✅ 成功
2. **日本語音声入力**: ✅ 認識される
3. **日本語音声出力**: ✅ 再生される
4. **基本的な対話**: ✅ 成立

**注意点**:
- ブラウザのマイク権限を許可する必要あり
- `adk web .` コマンドの引数はエージェントの親ディレクトリ（`poc/server`から実行）
- Token Streamingモードを有効化して使用

### 観測された課題

1. **レイテンシ**
   - 体感でやや遅延あり
   - 定量的な計測は未実施
   - 目標: 2秒以内

2. **未テスト項目**
   - 5分間連続対話の安定性
   - カスタムWebSocketサーバー（main.py）での動作

### 結論

**Gemini Live APIによるリアルタイム音声対話は技術的に実現可能**であることが確認できた。

Google AI Studio APIキーを使用することで、Vertex AIのアクセス制限問題を回避できた。

### 次のステップ（オプション）

1. 遅延の定量計測
2. 5分間連続対話テスト
3. カスタムサーバー（main.py + index.html）でのE2Eテスト
4. 本番環境向けのセキュリティ・パフォーマンス最適化

---

## 2026-02-01 追加検証・最終結論

### モデル互換性問題の発見と解決

カスタムサーバー（main.py）およびADK DevUIで「1008 policy violation」エラーが発生。

**エラーメッセージ**:
```
Operation is not implemented, or supported, or enabled.
```

**試行したモデル**:

| モデル名 | 結果 |
|---------|------|
| `gemini-2.5-flash-native-audio-latest` | ❌ policy violation |
| `gemini-2.0-flash-exp` | ❌ not supported for bidiGenerateContent |
| `gemini-2.5-flash-native-audio-preview-12-2025` | ✅ 動作 |

**解決策**:
ADKサンプルプロジェクト（`refs/adk-python/contributing/samples/live_bidi_streaming_single_agent/agent.py`）と同じモデル名 `gemini-2.5-flash-native-audio-preview-12-2025` を使用。

### レイテンシ観測結果

**観測結果**: 約5秒（体感）

**目標値との比較**:
- 目標: 2秒以内
- 実測: 約5秒
- **目標未達成**

**考察**:
- Gemini Live APIのプレビュー版であるため、GA版ではレイテンシが改善される可能性あり
- ネットワーク環境や同時接続数によっても変動
- 本番環境では許容可能なレベルか再評価が必要

### カスタムサーバー（main.py）の状態

**状態**: 音声応答の送信に課題あり（ADK DevUIでは動作確認済み）

**原因分析**:
- ADK内部のイベント処理とカスタム実装の間でのrole/author属性の扱いに差異
- `event.content.role` が `None` の場合があり、音声データが送信されない場合がある

**対応方針**:
- PoCとしてはADK DevUIでの動作確認をもって成功とする
- カスタムサーバーは今後の改善課題として記録

### 最終結論

#### ✅ PoC成功

**Gemini Live APIによるリアルタイム日本語音声対話は技術的に実現可能**であることが確認できた。

#### 確認できた事項

1. **Live API接続**: Google AI Studio APIキーで動作
2. **日本語音声入出力**: 認識・合成ともに動作
3. **ソクラテス式対話**: システムプロンプトに従った対話が成立
4. **ADK統合**: ADK 1.23.0で正常動作

#### 残課題

1. **レイテンシ**: 約5秒（目標2秒以内に未達）
2. **5分間安定性テスト**: 未実施
3. **カスタムサーバー**: 音声送信処理の改善が必要

#### 推奨事項

1. **MVP実装時**: ADK標準パターンを踏襲し、カスタマイズは最小限に
2. **モデル選択**: `gemini-2.5-flash-native-audio-preview-12-2025` を使用（GA版リリースまで）
3. **レイテンシ改善**: GA版リリース後に再検証、または音声処理のストリーミング最適化を検討
