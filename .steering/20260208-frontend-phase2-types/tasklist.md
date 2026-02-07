# Task List - Phase 2 フロントエンド型定義・状態管理基盤

## Phase 1: 環境セットアップ

- [x] ブランチ `feature/frontend-phase2-types` を作成
- [x] ステアリングディレクトリ作成・ドキュメント整備

## Phase 2: 型定義のテスト作成（TDD - Red）

- [x] `frontend/types/phase2.test.ts` — Phase 2a ツール型のテスト（ToolName, ToolExecution, 各結果型）
- [x] `frontend/types/phase2.test.ts` — Phase 2b エージェント型のテスト（AgentType, ActiveAgent, AgentTransition）
- [x] `frontend/types/phase2.test.ts` — Phase 2c RAG型のテスト（MemoryType, RetrievedMemory）
- [x] `frontend/types/phase2.test.ts` — Phase 2d 感情型のテスト（EmotionType, EmotionAnalysis, EmotionAdaptation）
- [x] `frontend/types/phase2.test.ts` — 共通拡張型のテスト（QuestionType, ResponseAnalysis, ChildLearningProfile等）
- [x] `frontend/types/phase2.test.ts` — 後方互換性テスト（DialogueTurn, LearningProgress の既存フィールドのみで動作確認）

## Phase 3: 型定義の実装（TDD - Green）

- [x] `frontend/types/phase2.ts` — Phase 2a ツール型定義
- [x] `frontend/types/phase2.ts` — Phase 2b エージェント型定義
- [x] `frontend/types/phase2.ts` — Phase 2c RAG型定義
- [x] `frontend/types/phase2.ts` — Phase 2d 感情型定義
- [x] `frontend/types/phase2.ts` — 共通拡張型定義（QuestionType, ResponseAnalysis等）
- [x] `frontend/types/dialogue.ts` — DialogueTurnにオプショナルフィールド追加
- [x] `frontend/types/session.ts` — LearningProgressにオプショナルフィールド追加
- [x] `frontend/types/websocket.ts` — 新WebSocketメッセージ型追加 + union拡張
- [x] `frontend/types/index.ts` — バレルエクスポート更新
- [x] テスト実行確認（型テスト全パス + 既存テスト全パス）

## Phase 4: Atoms のテスト作成（TDD - Red）

- [x] `frontend/store/atoms/phase2.test.ts` — Phase 2a ツールatomsのテスト（初期値、更新、isToolRunningAtom派生atom）
- [x] `frontend/store/atoms/phase2.test.ts` — Phase 2b エージェントatomsのテスト
- [x] `frontend/store/atoms/phase2.test.ts` — Phase 2c RAG atomsのテスト
- [x] `frontend/store/atoms/phase2.test.ts` — Phase 2d 感情atomsのテスト
- [x] `frontend/store/atoms/phase2.test.ts` — learningProfileAtomのテスト

## Phase 5: Atoms の実装（TDD - Green）

- [x] `frontend/store/atoms/phase2.ts` — Phase 2a ツールatoms
- [x] `frontend/store/atoms/phase2.ts` — Phase 2b エージェントatoms
- [x] `frontend/store/atoms/phase2.ts` — Phase 2c RAG atoms
- [x] `frontend/store/atoms/phase2.ts` — Phase 2d 感情atoms
- [x] `frontend/store/atoms/phase2.ts` — learningProfileAtom
- [x] `frontend/store/atoms/index.ts` — バレルエクスポート更新
- [x] テスト実行確認（atom テスト全パス + 既存テスト全パス）

## Phase 6: 品質チェック

- [x] `bun lint` — エラーなし
- [x] `bun typecheck` — エラーなし
- [x] `bunx vitest run` — 全テスト通過（既存 + 新規）
- [x] リファクタリング（TDD - Refactor）
- [x] コミット

## Phase 7: 完了

- [ ] COMPLETED.md 作成
