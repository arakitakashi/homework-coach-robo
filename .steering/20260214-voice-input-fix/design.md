# Design - 音声入力が応答しない問題の修正

## 根本原因分析

### 原因1: genai環境変数の不足（Critical）

Cloud Run バックエンドに以下の環境変数が設定されていない：

| 必要な環境変数 | 目的 | 現状 |
|---|---|---|
| `GOOGLE_GENAI_USE_VERTEXAI` | genaiライブラリにVertex AI使用を指示 | **未設定** |
| `GOOGLE_CLOUD_PROJECT` | genaiライブラリのプロジェクト指定 | **未設定**（`GCP_PROJECT_ID`は別名） |
| `GOOGLE_CLOUD_LOCATION` | genaiライブラリのリージョン指定 | **未設定**（`GCP_REGION`は別名、且つasia-northeast1） |

ADK `Runner.run_live()` は内部で `genai.Client()` を使用し、
これらの環境変数を参照する。未設定の場合、Vertex AI Gemini APIに接続できずエラーになる。

### 原因2: WebSocketエラーハンドリングの不備（High）

`voice_stream.py` の `_agent_to_client()` 関数でエラーが発生しても、
フロントエンドにエラーが通知されない（ログ出力のみ）。

## 修正方針

### Fix 1: Terraform でgenai環境変数を追加

`infrastructure/terraform/modules/cloud_run/main.tf` に以下を追加：

```hcl
env {
  name  = "GOOGLE_GENAI_USE_VERTEXAI"
  value = "TRUE"
}
env {
  name  = "GOOGLE_CLOUD_PROJECT"
  value = var.project_id
}
env {
  name  = "GOOGLE_CLOUD_LOCATION"
  value = var.vertex_ai_location
}
```

`vertex_ai_location` はGeminiモデルが利用可能なリージョン（デフォルト: `us-central1`）。
Cloud Run のデプロイリージョン（`asia-northeast1`）とは異なる。

### Fix 2: WebSocketエラーハンドリング改善

`voice_stream.py` の `_agent_to_client()` で例外発生時に
WebSocketでエラーメッセージをクライアントに送信する。

## ファイル構成

変更対象：
1. `infrastructure/terraform/modules/cloud_run/main.tf` - genai環境変数追加
2. `infrastructure/terraform/modules/cloud_run/variables.tf` - vertex_ai_location変数追加
3. `infrastructure/terraform/environments/dev/main.tf` - vertex_ai_location値渡し
4. `backend/app/api/v1/voice_stream.py` - エラーハンドリング改善
5. `backend/tests/unit/api/v1/test_voice_stream.py` - テスト追加（TDD）
