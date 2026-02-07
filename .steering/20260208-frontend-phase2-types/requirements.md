# Requirements - Phase 2 フロントエンド型定義・状態管理基盤

## 背景・目的

プロジェクトは Phase 1 (MVP) を完了し、Phase 2 への移行準備中。Phase 2 ではバックエンドに以下の機能が追加される：

- **Phase 2a**: ADK Function Calling ツール（calculate_tool, manage_hint_tool, record_progress_tool, check_curriculum_tool, analyze_image_tool）
- **Phase 2b**: マルチエージェントシステム（Router Agent → Math Coach / Japanese Coach / Encouragement / Review Agent）
- **Phase 2c**: Vertex AI RAG（セマンティック記憶検索）
- **Phase 2d**: 感情適応（音声トーン分析 → 対話トーン・サポートレベル動的調整）

フロントエンドがこれらのバックエンド変更に対応するため、まず **型定義（TypeScript types）** と **状態管理（Jotai atoms）** の基盤を整備する。UIコンポーネントの更新は後続タスクで行う。

## 要求事項

### 機能要件

1. **Phase 2a ツール型定義**: ToolName, ToolExecution, CalculationResult, HintManagementResult, ProgressRecordResult, CurriculumCheckResult, ImageAnalysisResult
2. **Phase 2b マルチエージェント型定義**: AgentType, ActiveAgent, AgentTransition, SubjectType
3. **Phase 2c RAG型定義**: MemoryType, RetrievedMemory
4. **Phase 2d 感情適応型定義**: EmotionType, EmotionAnalysis, SupportLevel, DialogueTone, EmotionAdaptation
5. **共通拡張型**: QuestionType, ResponseAnalysis, ThinkingTendencies, SubjectUnderstanding, ChildLearningProfile, SessionSummary
6. **既存型の拡張**: DialogueTurn, LearningProgress, WebSocketIncomingMessage に Phase 2 オプショナルフィールド追加
7. **Jotai atoms**: 各Phase 2機能に対応する状態管理atom（11個 + 派生atom 1個）

### 非機能要件

- **後方互換性**: 既存のMVPコードが一切変更なしで動作すること（新フィールドはすべてオプショナル）
- **型安全性**: `any`型を使用しない。すべての型が明示的に定義される
- **テストカバレッジ**: 新規コードに対して80%以上のテストカバレッジ
- **TDD遵守**: Red-Green-Refactorサイクルに従う

### 制約条件

- UIコンポーネントは作成しない（型とatomsのみ）
- バックエンドのPydanticモデルと整合性を保つ（camelCase変換）
- 循環インポートを避ける（`phase2.ts`は他の型ファイルからインポートしない）
- Auto-formatフックとの共存（インポートと使用コードを同じEditで追加）

## 対象範囲

### In Scope

- `frontend/types/phase2.ts` — Phase 2 型定義（新規作成）
- `frontend/types/dialogue.ts` — DialogueTurnへのオプショナルフィールド追加
- `frontend/types/session.ts` — LearningProgressへのオプショナルフィールド追加
- `frontend/types/websocket.ts` — 新WebSocketメッセージ型追加・union拡張
- `frontend/types/index.ts` — バレルエクスポート更新
- `frontend/store/atoms/phase2.ts` — Phase 2 atoms（新規作成）
- `frontend/store/atoms/index.ts` — バレルエクスポート更新
- 上記すべてのテストファイル

### Out of Scope

- UIコンポーネントの更新（CharacterDisplay, ProgressDisplay等）
- フック（useDialogue, useVoiceStream等）の更新
- APIクライアント（DialogueClient, VoiceWebSocketClient等）の更新
- E2Eテスト

## 成功基準

1. すべての新規型定義が TypeScript strict mode でコンパイルできる
2. 既存のテスト（172テスト）がすべてパスする（後方互換性）
3. 新規テストがすべてパスする
4. `bun lint` エラーなし
5. `bun typecheck` エラーなし
6. `bunx vitest run` 全テスト通過
