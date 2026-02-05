# Task List - ソクラテス式対話API統合

## Phase 1: スキーマ定義（TDD）

### 1.1 基本スキーマ

- [x] `test_dialogue_schemas.py` 作成 - CreateSessionRequest テスト
- [x] `CreateSessionRequest` スキーマ実装
- [x] `test_dialogue_schemas.py` 追加 - SessionResponse テスト
- [x] `SessionResponse` スキーマ実装
- [x] リファクタリング

### 1.2 分析・質問スキーマ

- [x] `test_dialogue_schemas.py` 追加 - AnalyzeRequest/Response テスト
- [x] `AnalyzeRequest`, `AnalyzeResponse` スキーマ実装
- [x] `test_dialogue_schemas.py` 追加 - QuestionRequest/Response テスト
- [x] `GenerateQuestionRequest`, `QuestionResponse` スキーマ実装
- [x] リファクタリング

### 1.3 ヒントスキーマ

- [x] `test_dialogue_schemas.py` 追加 - HintRequest/Response テスト
- [x] `GenerateHintRequest`, `HintResponse` スキーマ実装
- [x] リファクタリング

## Phase 2: セッション管理（TDD）

### 2.1 SessionStore実装

- [x] `test_session_store.py` 作成 - create_session テスト
- [x] `SessionStore.create_session()` 実装
- [x] `test_session_store.py` 追加 - get_session テスト
- [x] `SessionStore.get_session()` 実装
- [x] `test_session_store.py` 追加 - delete_session テスト
- [x] `SessionStore.delete_session()` 実装
- [x] `test_session_store.py` 追加 - update_session テスト
- [x] `SessionStore.update_session()` 実装
- [x] リファクタリング

## Phase 3: APIエンドポイント（TDD）

### 3.1 セッションエンドポイント

- [x] `test_dialogue.py` 作成 - POST /sessions テスト
- [x] `create_session` エンドポイント実装
- [x] `test_dialogue.py` 追加 - GET /sessions/{id} テスト
- [x] `get_session` エンドポイント実装
- [x] `test_dialogue.py` 追加 - DELETE /sessions/{id} テスト
- [x] `delete_session` エンドポイント実装
- [x] リファクタリング

### 3.2 対話エンドポイント

- [x] `test_dialogue.py` 追加 - POST /sessions/{id}/analyze テスト
- [x] `analyze_response` エンドポイント実装
- [x] `test_dialogue.py` 追加 - POST /sessions/{id}/question テスト
- [x] `generate_question` エンドポイント実装
- [x] `test_dialogue.py` 追加 - POST /sessions/{id}/hint テスト
- [x] `generate_hint` エンドポイント実装
- [x] リファクタリング

### 3.3 答えリクエスト検出エンドポイント

- [x] `test_dialogue.py` 追加 - POST /analyze-answer-request テスト
- [x] `analyze_answer_request` エンドポイント実装
- [x] リファクタリング

## Phase 4: APIルーター統合

- [x] `router.py` でルーター統合
- [x] `main.py` にルーター登録
- [x] OpenAPIドキュメント確認

## Phase 5: 統合テスト

- [x] `test_dialogue_flow.py` 作成 - 完全なセッションフローテスト
- [x] `test_dialogue_flow.py` 追加 - ヒント進行フローテスト
- [x] `test_dialogue_flow.py` 追加 - エラーケーステスト

## Phase 6: 品質チェック

- [x] コードレビュー（セルフレビュー）
- [x] テストカバレッジ確認（80%以上）→ 98%達成
- [x] リンター・フォーマッター実行（Ruff）
- [x] 既存テストがすべてパス → 179テスト合格

## Phase 7: ドキュメント更新

- [x] CLAUDE.md の Development Context 更新（対象外：大きな変更なし）
- [x] COMPLETED.md 作成

---

## 進捗トラッキング

| Phase | ステータス | 完了日 |
|-------|----------|--------|
| Phase 1 | ✅ 完了 | 2026-02-05 |
| Phase 2 | ✅ 完了 | 2026-02-05 |
| Phase 3 | ✅ 完了 | 2026-02-05 |
| Phase 4 | ✅ 完了 | 2026-02-05 |
| Phase 5 | ✅ 完了 | 2026-02-05 |
| Phase 6 | ✅ 完了 | 2026-02-05 |
| Phase 7 | ✅ 完了 | 2026-02-05 |

---

## 注意事項

1. **TDD厳守**: 各タスクは必ず「テスト作成 → 実装 → リファクタリング」の順序
2. **小さいステップ**: 一度に多くのテストを書かない。1つずつ進める
3. **コミット粒度**: テスト追加・実装完了ごとにコミット
4. **LLMモック**: LLM呼び出しは必ずモック化してテスト
5. **既存テスト維持**: 新しいコードが既存機能を壊さないことを確認
