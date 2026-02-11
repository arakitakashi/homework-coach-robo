# Task List - Fix Agent Engine Dependencies and Enable Dashboard/Tracing

## Phase 1: 環境セットアップ

- [x] ステアリングディレクトリの作成
- [x] requirements.md の作成
- [x] design.md の作成
- [x] tasklist.md の作成

## Phase 2: 依存関係のバージョン更新

- [ ] `backend/agent_engine_requirements.txt` を更新
  - `google-cloud-aiplatform[agent_engines,adk]>=1.126.1`
  - `google-adk>=1.18.0`
- [ ] `backend/scripts/deploy_agent_engine.py` を更新
  - L80-82: requirements を更新
  - L121-124: requirements を更新

## Phase 3: 動作確認

- [ ] 変更内容の確認（git diff）
- [ ] コミット・プッシュ

## Phase 4: 品質チェック

- [ ] コードレビュー（セルフレビュー）
- [ ] ドキュメント更新
  - [ ] `CLAUDE.md` の Development Context 更新
  - [ ] `docs/implementation-status.md` の更新

## Phase 5: PR作成

- [ ] PR作成
- [ ] Issue #108 にリンク
