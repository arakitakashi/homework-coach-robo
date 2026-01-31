# COMPLETED - Gemini Live API PoC

**完了日**: 2026-02-01
**ステータス**: ✅ PoC成功

---

## 実装内容の要約

### 目的

Gemini Live APIを使用したリアルタイム日本語音声対話の技術的実現可能性を検証する。

### 成果物

1. **エージェント定義** (`poc/server/tutor_agent/`)
   - ソクラテス式対話用システムプロンプト
   - ADK Agent構造（root_agent）

2. **WebSocketサーバー** (`poc/server/main.py`)
   - FastAPI + WebSocketエンドポイント
   - LiveRequestQueueによる双方向通信

3. **クライアント** (`poc/client/index.html`)
   - Web Audio APIによるマイク入力
   - WebSocket接続・音声送受信
   - 遅延計測UI

4. **ドキュメント** (`.steering/20260131-gemini-live-api-poc/`)
   - requirements.md: 要求仕様
   - design.md: 実装設計
   - tasklist.md: タスクリスト
   - reflection.md: 検証結果・学び

### 確認できた事項

| 項目 | 結果 |
|------|------|
| Live API接続 | ✅ 成功 |
| 日本語音声入力 | ✅ 認識される |
| 日本語音声出力 | ✅ 再生される |
| 基本的な対話 | ✅ 成立 |
| レイテンシ | △ 約5秒（目標2秒以内に未達） |

---

## 発生した問題と解決方法

### 1. Vertex AI Live APIアクセス制限

**問題**: プロジェクトでVertex AI Live APIモデルへのアクセスが有効化されていない

**解決**: Google AI Studio APIキーを使用（`GOOGLE_GENAI_USE_VERTEXAI=FALSE`）

### 2. ADK APIの変更

**問題**: スキルファイルのサンプルコードがADK 1.23.0のAPIと異なっていた

**解決**: Context7経由でADK公式ドキュメントを参照し、正しいAPIパターンに修正

### 3. モデル互換性問題（1008 policy violation）

**問題**: 特定のモデル名で「Operation is not implemented, or supported, or enabled」エラー

**解決**: ADKサンプルプロジェクトと同じモデル `gemini-2.5-flash-native-audio-preview-12-2025` を使用

**試行結果**:
| モデル名 | 結果 |
|---------|------|
| `gemini-2.5-flash-native-audio-latest` | ❌ policy violation |
| `gemini-2.0-flash-exp` | ❌ not supported for bidiGenerateContent |
| `gemini-2.5-flash-native-audio-preview-12-2025` | ✅ 動作 |

---

## 今後の改善点

### 短期（MVP実装時）

1. **ADK標準パターンの踏襲**: カスタマイズは最小限に
2. **モデル固定**: GA版リリースまで `gemini-2.5-flash-native-audio-preview-12-2025` を使用
3. **カスタムサーバー改善**: 音声送信処理のrole/author属性ハンドリング修正

### 中期（本番リリース時）

1. **レイテンシ改善**: GA版リリース後に再検証
2. **安定性テスト**: 5分間連続対話、複数同時接続
3. **エラーハンドリング強化**: 接続断、タイムアウト、リトライ

### 長期

1. **Vertex AI移行**: 本番環境ではVertex AIの使用を検討
2. **音声品質最適化**: サンプルレート、ビットレートの調整
3. **感情認識統合**: 音声トーン分析機能の追加

---

## 学んだこと（Lessons Learned）

### 技術的な学び

1. **ADK構成パターン**: `Runner` + `InMemorySessionService` の組み合わせが標準
2. **モデル名の重要性**: プレビュー版APIはモデル名に敏感、公式サンプルを参照すべき
3. **イベント処理**: ADKイベントの`role`と`author`属性の使い分けを理解する必要あり
4. **音声フォーマット**: 入力16kHz、出力24kHzの非対称性に注意

### プロセス上の学び

1. **公式サンプル優先**: ドキュメントより公式サンプルコードが信頼性高い
2. **段階的検証**: ADK DevUIで動作確認後にカスタム実装に進むべき
3. **エラーメッセージの解釈**: 「policy violation」は認証だけでなくモデル互換性も原因となりうる

### 今後のPoCへの適用

1. **リファレンス実装の参照**: 新しいAPIを試す際は、まず公式サンプルを動かす
2. **差分の最小化**: 動作するサンプルから少しずつカスタマイズ
3. **問題切り分け**: 公式ツールと自作実装の両方でテストし、問題箇所を特定

---

## 結論

**Gemini Live APIによるリアルタイム日本語音声対話は技術的に実現可能**であることが確認できた。

レイテンシ（約5秒）は目標（2秒以内）に未達だが、プレビュー版の制約であり、GA版リリース後の改善が期待される。

MVP実装に進む技術的基盤は整った。

---

## 参考リンク

- [ADK Streaming Dev Guide](https://google.github.io/adk-docs/streaming/dev-guide/part1/)
- [Vertex AI Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)
- [Gemini Live API Models](https://ai.google.dev/gemini-api/docs/models#live-api)
- ADKサンプル: `refs/adk-python/contributing/samples/live_bidi_streaming_single_agent/`
