# Task List - Fix Agent Engine Dependencies and Enable Dashboard/Tracing

## Phase 1: 環境セットアップ

- [x] ステアリングディレクトリの作成
- [x] requirements.md の作成
- [x] design.md の作成
- [x] tasklist.md の作成

## Phase 2: 依存関係のバージョン更新

- [x] `backend/agent_engine_requirements.txt` を更新
  - `google-cloud-aiplatform[agent_engines,adk]>=1.126.1`
  - `google-adk>=1.23.0`
- [x] `backend/scripts/deploy_agent_engine.py` を更新
  - L80-82: requirements を更新
  - L121-124: requirements を更新
- [x] `serialize_agent.py` の修正
  - `session_service` と `memory_service` を lazy initialization に変更

## Phase 3: 動作確認

- [x] 変更内容の確認（git diff）
- [ ] コミット・プッシュ（PR 作成中）

## Phase 4: 品質チェック

- [x] コードレビュー（セルフレビュー）
- [ ] ドキュメント更新
  - [ ] Issue #108 にコメント追加（PR マージ後）

## Phase 5: PR作成

- [x] PR #109 作成・マージ（依存関係更新）
- [ ] PR 作成（serialize_agent.py 修正）
- [ ] Issue #108 にリンク

## Phase 6: 追加の問題対応

- [x] serialize_agent.py の Runner API 変更対応
- [x] lazy initialization 実装
- [x] GCS 権限問題を Issue #110 として切り出し
