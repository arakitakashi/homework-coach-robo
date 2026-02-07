# Design - Phase 2 フロントエンド型定義・状態管理基盤

## アーキテクチャ概要

Phase 2 の型定義は、既存の型構造を拡張する形で追加する。新規ファイル `types/phase2.ts` に Phase 2 固有の型をすべて集約し、既存ファイルにはオプショナルフィールドのみ追加する。

```
types/
├── audio.ts        # 既存（変更なし）
├── dialogue.ts     # 既存（5つのオプショナルフィールド追加）
├── session.ts      # 既存（3つのオプショナルフィールド追加）
├── websocket.ts    # 既存（3つの新メッセージ型追加 + union拡張）
├── phase2.ts       # 新規（Phase 2a-2d 全型定義）
└── index.ts        # バレルエクスポート更新

store/atoms/
├── audio.ts        # 既存（変更なし）
├── dialogue.ts     # 既存（変更なし）
├── session.ts      # 既存（変更なし）
├── phase2.ts       # 新規（11 atoms + 1 derived atom）
└── index.ts        # バレルエクスポート更新
```

## 技術選定

- **型定義**: TypeScript interfaces/types（既存パターンに準拠）
- **状態管理**: Jotai atoms（既存パターンに準拠）
- **テスト**: Vitest（直接atom操作テスト + 型コンパイルテスト）

## データ設計

### Phase 2a: ツール型定義

バックエンドのADK Function Toolsに対応する型。

```typescript
type ToolName = "calculate_tool" | "manage_hint_tool" | "record_progress_tool"
              | "check_curriculum_tool" | "analyze_image_tool"

type ToolExecutionStatus = "pending" | "running" | "completed" | "error"

interface ToolExecution {
  toolName: ToolName
  status: ToolExecutionStatus
  input?: Record<string, unknown>
  output?: Record<string, unknown>
  error?: string
  timestamp: Date
}
```

各ツールの結果型（CalculationResult, HintManagementResult等）は個別interfaceで定義。

### Phase 2b: マルチエージェント型定義

バックエンドのRouter Agent + 専門エージェントに対応する型。

```typescript
type SubjectType = "math" | "japanese"
type AgentType = "router" | "math_coach" | "japanese_coach" | "encouragement" | "review"

interface ActiveAgent {
  type: AgentType
  name: string
  startedAt: Date
}
```

### Phase 2c: RAG型定義

Vertex AI RAGのセマンティック検索結果に対応する型。

```typescript
type MemoryType = "learning_insight" | "thinking_pattern" | "effective_approach"

interface RetrievedMemory {
  id: string
  memoryType: MemoryType
  content: string
  tags: string[]
  relevanceScore: number
  createdAt: Date
}
```

### Phase 2d: 感情適応型定義

音声トーン分析・感情適応に対応する型。

```typescript
type EmotionType = "frustrated" | "confident" | "confused" | "happy" | "tired" | "neutral"
type SupportLevel = "minimal" | "moderate" | "intensive"
type DialogueTone = "encouraging" | "neutral" | "empathetic"

interface EmotionAnalysis {
  primaryEmotion: EmotionType
  confidence: number        // 0-1
  frustrationLevel: number  // 0-10
  engagementLevel: number   // 0-10
  timestamp: Date
}
```

### 既存型の拡張

**DialogueTurn** — Phase 2 フィールドをオプショナルで追加:
- `questionType?: QuestionType` (Phase 2a)
- `responseAnalysis?: ResponseAnalysis` (Phase 2a)
- `emotion?: EmotionType` (Phase 2d)
- `activeAgent?: AgentType` (Phase 2b)
- `toolExecutions?: ToolExecution[]` (Phase 2a)

**LearningProgress** — Phase 2 フィールドをオプショナルで追加:
- `currentSubject?: SubjectType` (Phase 2b)
- `currentTopic?: string` (Phase 2b)
- `thinkingTendencies?: ThinkingTendencies` (Phase 2c/2d)

**WebSocketIncomingMessage** — 3つの新メッセージ型をunionに追加:
- `ToolExecutionMessage` (Phase 2a)
- `AgentTransitionMessage` (Phase 2b)
- `EmotionUpdateMessage` (Phase 2d)

## Jotai Atoms 設計

### Phase 2a: ツール状態

| Atom | 型 | 初期値 | 用途 |
|------|-----|--------|------|
| `activeToolExecutionsAtom` | `ToolExecution[]` | `[]` | 実行中ツール一覧 |
| `toolExecutionHistoryAtom` | `ToolExecution[]` | `[]` | ツール実行履歴 |
| `isToolRunningAtom` (derived) | `boolean` | `false` | ツール実行中フラグ |

### Phase 2b: マルチエージェント状態

| Atom | 型 | 初期値 | 用途 |
|------|-----|--------|------|
| `activeAgentAtom` | `ActiveAgent \| null` | `null` | アクティブエージェント |
| `agentTransitionHistoryAtom` | `AgentTransition[]` | `[]` | エージェント遷移履歴 |

### Phase 2c: RAG状態

| Atom | 型 | 初期値 | 用途 |
|------|-----|--------|------|
| `retrievedMemoriesAtom` | `RetrievedMemory[]` | `[]` | 取得された記憶 |

### Phase 2d: 感情適応状態

| Atom | 型 | 初期値 | 用途 |
|------|-----|--------|------|
| `emotionAnalysisAtom` | `EmotionAnalysis \| null` | `null` | 最新の感情分析結果 |
| `emotionAdaptationAtom` | `EmotionAdaptation \| null` | `null` | 感情適応設定 |
| `emotionHistoryAtom` | `EmotionAnalysis[]` | `[]` | 感情履歴 |

### 学習プロファイル

| Atom | 型 | 初期値 | 用途 |
|------|-----|--------|------|
| `learningProfileAtom` | `ChildLearningProfile \| null` | `null` | 子供の学習プロファイル |

## 依存関係

```
types/phase2.ts  ← (スタンドアロン、外部インポートなし)
   ↑
types/dialogue.ts  (phase2からToolExecution, QuestionType等をインポート)
types/session.ts   (phase2からSubjectType, ThinkingTendencies等をインポート)
types/websocket.ts (phase2からToolName, AgentType, EmotionType等をインポート)

store/atoms/phase2.ts ← types/phase2.ts の型をインポート
```

**循環インポート防止**: `phase2.ts`（型）は他の型ファイルからインポートしない。依存は一方向のみ。

## エラーハンドリング

型定義のみのため、ランタイムエラーハンドリングは不要。TypeScriptコンパイラによる静的型チェックが主な品質保証。

## セキュリティ考慮事項

- 機密情報を型定義に含めない
- 子供のデータを扱う型は適切にスコープされている（ChildLearningProfile等）

## パフォーマンス考慮事項

- Jotai atomsは遅延初期化のため、使用されるまでメモリを消費しない
- 派生atom（isToolRunningAtom）は依存atomが変更された時のみ再計算

## 代替案と採用理由

| 代替案 | 採用案 | 理由 |
|--------|--------|------|
| 各Phase毎に別ファイル（phase2a.ts, phase2b.ts...） | 単一ファイル phase2.ts | ファイル数を抑える。Phase間で共有される型がある |
| 既存型ファイルに直接追加 | 新規 phase2.ts + 既存ファイル拡張 | 変更の影響範囲を最小化。Phase 2 固有型の一覧性 |
| Phase2SessionExtension等の拡張interfaceを作成 | 既存interfaceにオプショナルフィールド追加 | シンプル。intersection typeは使い勝手が悪い |
