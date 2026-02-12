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
  - `google-adk>=1.18.0` → 既存の >=1.23.0 で満たされている
- [x] `backend/scripts/deploy_agent_engine.py` を更新
  - L79-82: requirements を更新（PR #109）
  - L121-125: requirements を更新（PR #109）
- [x] `backend/scripts/serialize_agent.py` を修正
  - Runner API変更対応（session_service, memory_service 追加）
  - 遅延初期化パターン実装（認証エラー回避）

## Phase 3: 動作確認

- [x] 変更内容の確認（git diff）
- [x] コミット・プッシュ
  - PR #109: 依存関係バージョン更新
  - PR #111: serialize_agent.py 修正

## Phase 4: 品質チェック

- [x] コードレビュー（セルフレビュー）
- [x] ドキュメント更新
  - [x] `CLAUDE.md` の Development Context 更新
  - [x] `docs/implementation-status.md` の更新

## Phase 5: PR作成

- [x] PR #109 作成・マージ（依存関係更新）
- [x] PR #111 作成（serialize_agent.py 修正）
- [x] Issue #108 にリンク
- [x] Issue #110 作成（GCS権限問題）
