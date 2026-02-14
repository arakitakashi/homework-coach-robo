# Task List - 音声入力が応答しない問題の修正

## Phase 1: Terraform修正（genai環境変数追加）

- [ ] `modules/cloud_run/variables.tf` に `vertex_ai_location` 変数を追加
- [ ] `modules/cloud_run/main.tf` にgenai環境変数3つを追加
- [ ] `environments/dev/main.tf` で `vertex_ai_location` を渡す
- [ ] `terraform init -backend=false && terraform validate` で検証

## Phase 2: バックエンドエラーハンドリング改善（TDD）

- [ ] `voice_stream.py` の `_agent_to_client()` でエラーをクライアントに送信
- [ ] テスト追加

## Phase 3: 品質チェック

- [ ] Terraform validate 通過
- [ ] Backend pytest 通過
- [ ] コミット・プッシュ・PR作成
