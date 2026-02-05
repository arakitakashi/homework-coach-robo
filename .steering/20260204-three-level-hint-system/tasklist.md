# Task List - 3段階ヒントシステム

## Phase 1: データモデル追加（TDD）

### 1.1 HintLevel Enum

- [x] `test_models.py` 追加 - HintLevel Enumテスト
- [x] `HintLevel` Enum実装
- [x] リファクタリング

### 1.2 AnswerRequestType Enum

- [x] `test_models.py` 追加 - AnswerRequestType Enumテスト
- [x] `AnswerRequestType` Enum実装
- [x] リファクタリング

### 1.3 AnswerRequestAnalysis モデル

- [x] `test_models.py` 追加 - AnswerRequestAnalysis テスト
- [x] `AnswerRequestAnalysis` Pydanticモデル実装
- [x] リファクタリング

## Phase 2: 答えリクエスト検出（TDD）

### 2.1 キーワードマッチング

- [x] `test_manager.py` 追加 - detect_answer_request_keywords テスト（明示的）
- [x] `_detect_answer_request_keywords()` 実装（明示的キーワード）
- [x] `test_manager.py` 追加 - detect_answer_request_keywords テスト（暗示的）
- [x] `_detect_answer_request_keywords()` 実装（暗示的キーワード）
- [x] リファクタリング

### 2.2 LLM補助検出

- [x] `test_manager.py` 追加 - detect_answer_request テスト（LLM使用）
- [x] `detect_answer_request()` 実装
- [x] リファクタリング

## Phase 3: ヒントプロンプト構築（TDD）

### 3.1 ヒントレベル別プロンプト

- [x] `test_manager.py` 追加 - build_hint_prompt テスト（レベル1）
- [x] `build_hint_prompt()` 実装（レベル1）
- [x] `test_manager.py` 追加 - build_hint_prompt テスト（レベル2）
- [x] `build_hint_prompt()` 実装（レベル2）
- [x] `test_manager.py` 追加 - build_hint_prompt テスト（レベル3）
- [x] `build_hint_prompt()` 実装（レベル3）
- [x] リファクタリング

### 3.2 答えリクエスト時の励まし追加

- [x] `test_manager.py` 追加 - build_hint_prompt テスト（答えリクエストあり）
- [x] `build_hint_prompt()` 実装（励まし追加）
- [x] リファクタリング

## Phase 4: ヒントレスポンス生成（TDD）

### 4.1 ヒントレスポンス生成

- [x] `test_manager.py` 追加 - generate_hint_response テスト（レベル1）
- [x] `generate_hint_response()` 実装（基本）
- [x] `test_manager.py` 追加 - generate_hint_response テスト（レベル2, 3）
- [x] `generate_hint_response()` 実装（全レベル対応）
- [x] リファクタリング

### 4.2 答えリクエスト時のレスポンス

- [x] `test_manager.py` 追加 - generate_hint_response テスト（答えリクエスト）
- [x] `generate_hint_response()` 実装（答えリクエスト対応）
- [x] リファクタリング

## Phase 5: ヒントレベル進行（TDD）

### 5.1 レベル進行ロジック

- [x] `test_manager.py` 追加 - advance_hint_level テスト（進行しない）
- [x] `advance_hint_level()` 実装（進行しないケース）
- [x] `test_manager.py` 追加 - advance_hint_level テスト（レベル1→2）
- [x] `advance_hint_level()` 実装（レベル1→2）
- [x] `test_manager.py` 追加 - advance_hint_level テスト（レベル2→3）
- [x] `advance_hint_level()` 実装（レベル2→3）
- [x] `test_manager.py` 追加 - advance_hint_level テスト（最大レベル）
- [x] `advance_hint_level()` 実装（最大レベル制限）
- [x] リファクタリング

### 5.2 最低ターン数の保証

- [x] `test_manager.py` 追加 - advance_hint_level テスト（最低ターン数）
- [x] `advance_hint_level()` 実装（最低ターン数チェック）
- [x] リファクタリング

## Phase 6: 統合テスト

- [x] `test_hint_flow.py` 作成 - レベル1フローテスト
- [x] `test_hint_flow.py` 追加 - レベル1→2遷移テスト
- [x] `test_hint_flow.py` 追加 - レベル2→3遷移テスト
- [x] `test_hint_flow.py` 追加 - 答えリクエスト対応フローテスト
- [x] `test_hint_flow.py` 追加 - レベルスキップ禁止テスト

## Phase 7: 品質チェック

- [x] コードレビュー（セルフレビュー）
- [x] テストカバレッジ確認（97% - 目標80%超）
- [x] リンター・フォーマッター実行（Ruff）
- [x] 型チェック（TYPE_CHECKING対応済み）
- [x] 既存テストがすべてパス（110テスト）

## Phase 8: ドキュメント更新

- [x] CLAUDE.md の Development Context 更新
- [x] COMPLETED.md 作成

---

## 進捗トラッキング

| Phase | ステータス | 完了日 |
|-------|----------|--------|
| Phase 1 | ✅ 完了 | 2026-02-04 |
| Phase 2 | ✅ 完了 | 2026-02-04 |
| Phase 3 | ✅ 完了 | 2026-02-04 |
| Phase 4 | ✅ 完了 | 2026-02-04 |
| Phase 5 | ✅ 完了 | 2026-02-04 |
| Phase 6 | ✅ 完了 | 2026-02-04 |
| Phase 7 | ✅ 完了 | 2026-02-04 |
| Phase 8 | ✅ 完了 | 2026-02-04 |

---

## 注意事項

1. **TDD厳守**: 各タスクは必ず「テスト作成 → 実装 → リファクタリング」の順序
2. **小さいステップ**: 一度に多くのテストを書かない。1つずつ進める
3. **コミット粒度**: テスト追加・実装完了ごとにコミット
4. **LLMモック**: LLM呼び出しは必ずモック化してテスト
5. **レベルスキップ禁止**: テストで必ず順番通りにレベル進行することを検証
6. **既存テスト維持**: 新しいコードが既存機能を壊さないことを確認
