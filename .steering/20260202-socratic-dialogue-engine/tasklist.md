# Task List - ソクラテス式対話エンジン

## Phase 1: 環境セットアップ

- [x] 必要なディレクトリ構造を作成
- [x] 依存パッケージの確認（pytest, pydantic, google-adk）
- [x] テスト設定の確認（conftest.py）

## Phase 2: データモデル実装（TDD）

### 2.1 models.py

- [x] `test_models.py` 作成 - QuestionType Enumテスト
- [x] `QuestionType` Enum実装
- [x] `test_models.py` 追加 - DialogueTone Enumテスト
- [x] `DialogueTone` Enum実装
- [x] `test_models.py` 追加 - ResponseAnalysisテスト
- [x] `ResponseAnalysis` Pydanticモデル実装
- [x] `test_models.py` 追加 - DialogueTurnテスト
- [x] `DialogueTurn` Pydanticモデル実装
- [x] `test_models.py` 追加 - DialogueContextテスト
- [x] `DialogueContext` Pydanticモデル実装
- [x] `test_models.py` 追加 - from_adk_sessionテスト
- [x] `from_adk_session()` クラスメソッド実装
- [x] リファクタリング

### 2.2 learning_profile.py（学習プロファイル永続化）

- [x] `test_learning_profile.py` 作成 - ThinkingTendenciesテスト
- [x] `ThinkingTendencies` Pydanticモデル実装
- [x] `test_learning_profile.py` 追加 - SubjectUnderstandingテスト
- [x] `SubjectUnderstanding` Pydanticモデル実装
- [x] `test_learning_profile.py` 追加 - SessionSummaryテスト
- [x] `SessionSummary` Pydanticモデル実装
- [x] `test_learning_profile.py` 追加 - ChildLearningProfileテスト
- [x] `ChildLearningProfile` Pydanticモデル実装
- [x] `test_learning_profile.py` 追加 - LearningMemoryテスト
- [x] `LearningMemory` Pydanticモデル実装
- [x] リファクタリング（ruff/mypy パス）

## Phase 3: SocraticDialogueManager実装（TDD）

### 3.1 プロンプト構築

- [x] `test_manager.py` 作成 - SYSTEM_PROMPTテスト
- [x] `SYSTEM_PROMPT` 定数実装
- [x] `test_manager.py` 追加 - build_question_promptテスト（理解確認）
- [x] `build_question_prompt()` 実装（理解確認）
- [x] `test_manager.py` 追加 - build_question_promptテスト（思考誘導）
- [x] `build_question_prompt()` 実装（思考誘導）
- [x] `test_manager.py` 追加 - build_analysis_promptテスト
- [x] `build_analysis_prompt()` 実装
- [x] リファクタリング

### 3.2 回答分析

- [x] `test_manager.py` 追加 - analyze_responseテスト（正しい理解）
- [x] `analyze_response()` 実装（基本）
- [x] `test_manager.py` 追加 - analyze_responseテスト（誤解）
- [x] `analyze_response()` 実装（誤解検出）
- [x] リファクタリング

### 3.3 質問タイプ決定

- [x] `test_manager.py` 追加 - determine_question_typeテスト（理解確認）
- [x] `determine_question_type()` 実装（理解確認）
- [x] `test_manager.py` 追加 - determine_question_typeテスト（思考誘導）
- [x] `determine_question_type()` 実装（思考誘導）
- [x] リファクタリング

### 3.4 トーン決定

- [x] `test_manager.py` 追加 - determine_toneテスト（励まし）
- [x] `determine_tone()` 実装（励まし）
- [x] `test_manager.py` 追加 - determine_toneテスト（共感）
- [x] `determine_tone()` 実装（共感）
- [x] リファクタリング

### 3.5 質問生成

- [x] `test_manager.py` 追加 - generate_questionテスト
- [x] `generate_question()` 実装
- [x] リファクタリング（ruff/mypy パス）

### 3.6 フェーズ遷移

- [x] `test_manager.py` 追加 - should_move_to_next_phaseテスト
- [x] `should_move_to_next_phase()` 実装
- [x] リファクタリング（ruff/mypy パス）

## Phase 4: 統合テスト

- [x] `test_dialogue_flow.py` 作成 - 基本フローテスト
- [x] 対話フロー全体の統合テスト（Phase 1-7）
- [x] エッジケーステスト（長い対話、早期終了）
- [x] エラーケーステスト（LLM失敗時のフォールバック）

## Phase 5: 品質チェック

- [x] コードレビュー（セルフレビュー）
- [x] テストカバレッジ確認（98% - 目標80%超）
- [x] リンター・フォーマッター実行（Ruff）
- [x] 型チェック（mypy）

## Phase 6: ドキュメント更新

- [x] CLAUDE.md の Development Context 更新
- [x] COMPLETED.md 作成

---

## 進捗トラッキング

| Phase | ステータス | 完了日 |
|-------|----------|--------|
| Phase 1 | ✅ 完了 | 2026-02-02 |
| Phase 2.1 | ✅ 完了 | 2026-02-02 |
| Phase 2.2 | ✅ 完了 | 2026-02-03 |
| Phase 3 | ✅ 完了 | 2026-02-04 |
| Phase 4 | ✅ 完了 | 2026-02-04 |
| Phase 5 | ✅ 完了 | 2026-02-04 |
| Phase 6 | ✅ 完了 | 2026-02-04 |

---

## 注意事項

1. **TDD厳守**: 各タスクは必ず「テスト作成 → 実装 → リファクタリング」の順序
2. **小さいステップ**: 一度に多くのテストを書かない。1つずつ進める
3. **コミット粒度**: テスト追加・実装完了ごとにコミット
4. **LLMモック**: LLM呼び出しは必ずモック化してテスト
5. **ADKセッション**: 状態管理はADK SessionServiceに委譲（独自StateTracker不要）
