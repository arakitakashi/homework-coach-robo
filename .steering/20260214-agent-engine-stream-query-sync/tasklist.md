# Task List - Agent Engine stream_query 同期ジェネレータ対応

## Phase 1: 環境セットアップ

- [x] ブランチ作成（`fix/agent-engine-stream-query-sync`）
- [x] ステアリングディレクトリ作成

## Phase 2: テスト実装（TDD）

**注意**: この修正は既存コードのバグ修正であり、新規機能ではないため、既存のテストを活用する。

- [ ] 既存テストの確認（`tests/unit/services/adk/runner/test_agent_engine_client.py`）
- [ ] 必要に応じてテストを追加

## Phase 3: 実装

- [ ] `agent_engine_client.py` の `stream_query` メソッド修正（`async for` → `for`）
- [ ] `agent_engine_client.py` の `create_session` メソッド確認（`await` が必要か確認）
- [ ] 型ヒントの確認

## Phase 4: 統合テスト

- [ ] ローカルでバックエンド起動確認
- [ ] フロントエンドでメッセージ送信テスト（手動）

## Phase 5: 品質チェック

- [ ] `/quality-check` スキルでサブエージェント実行（mypy/ruff/pytest）
- [ ] エラーがあれば修正
- [ ] `/update-docs` スキルでドキュメント更新

## Phase 6: PR作成

- [ ] コミット（Conventional Commits形式）
- [ ] プッシュ
- [ ] `/create-pr` スキルでPR作成
- [ ] Issue #133 をクローズ
