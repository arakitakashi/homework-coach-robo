# Design - Phase 2 対話履歴の拡張表示

## アーキテクチャ概要

`DialogueHistory` コンポーネントを拡張し、Phase 2 メタデータを視覚的に表示します。既存の `DialogueBubble` サブコンポーネントを拡張し、新しいサブコンポーネントを追加します。

### コンポーネント構造

```
DialogueHistory（既存コンポーネント）
├─ DialogueBubble（既存、拡張）
│  ├─ DialogueMetadataHeader（新規）
│  │  ├─ QuestionTypeIcon（新規）
│  │  ├─ EmotionIcon（新規）
│  │  └─ AgentBadge（新規）
│  ├─ DialogueText（既存、テキスト本文）
│  └─ DialogueMetadataFooter（新規）
│     ├─ UnderstandingIndicator（新規）
│     └─ ToolExecutionBadges（新規）
```

### レイアウト設計

```
┌─────────────────────────────────────┐
│ [?アイコン] [感情アイコン] [エージェントバッジ] ← Header
├─────────────────────────────────────┤
│                                     │
│  対話テキスト本文                    │
│                                     │
├─────────────────────────────────────┤
│ [理解度: 80%] [ツール1] [ツール2]    ← Footer
└─────────────────────────────────────┘
```

## 技術選定

### 使用技術

- **React 18**: 関数コンポーネント
- **TypeScript**: strict mode
- **Tailwind CSS**: スタイリング
- **Framer Motion**: アニメーション（オプション）
- **Lucide React**: アイコン
- **Vitest + Testing Library**: テスト

### 既存コンポーネントの再利用

以下の既存コンポーネントのデザインパターンを参考にします：

1. **ToolExecutionDisplay**:
   - ツール名のラベルマッピング
   - ステータスアイコン（pending, running, completed, error）
   - レイアウト（横並び、gap-2）

2. **AgentIndicator**:
   - エージェント名のラベルマッピング
   - Framer Motion アニメーション
   - カラーコーディング（青系）

3. **EmotionIndicator**:
   - 感情タイプのアイコン・ラベル・カラーマッピング
   - Lucide アイコン
   - カラーコーディング（感情ごとに異なる）

## データ設計

### 表示ロジック

各 Phase 2 メタデータは Optional なので、存在する場合のみ表示します：

```typescript
interface DialogueBubbleProps {
  turn: DialogueTurn
}

// DialogueTurn の型（既存）:
interface DialogueTurn {
  id: string
  speaker: Speaker
  text: string
  timestamp: Date
  questionType?: QuestionType           // Phase 2a
  responseAnalysis?: ResponseAnalysis   // Phase 2a
  emotion?: EmotionType                 // Phase 2d
  activeAgent?: AgentType               // Phase 2b
  toolExecutions?: ToolExecution[]      // Phase 2a
}
```

### 条件付きレンダリング

```typescript
function DialogueBubble({ turn }: DialogueBubbleProps) {
  const hasHeader = turn.questionType || turn.emotion || turn.activeAgent
  const hasFooter = turn.responseAnalysis || (turn.toolExecutions && turn.toolExecutions.length > 0)

  return (
    <div>
      {hasHeader && <DialogueMetadataHeader turn={turn} />}
      <DialogueText text={turn.text} />
      {hasFooter && <DialogueMetadataFooter turn={turn} />}
    </div>
  )
}
```

## ファイル構成

```
frontend/components/features/DialogueHistory/
├── DialogueHistory.tsx                # 既存（変更なし）
├── DialogueHistory.test.tsx           # 既存（拡張）
├── DialogueBubble.tsx                 # 新規（DialogueHistory.tsxから分離）
├── DialogueBubble.test.tsx            # 新規
├── DialogueMetadataHeader.tsx         # 新規
├── DialogueMetadataHeader.test.tsx    # 新規
├── DialogueMetadataFooter.tsx         # 新規
├── DialogueMetadataFooter.test.tsx    # 新規
├── QuestionTypeIcon.tsx               # 新規
├── EmotionIcon.tsx                    # 新規
├── AgentBadge.tsx                     # 新規
├── UnderstandingIndicator.tsx         # 新規
├── ToolExecutionBadges.tsx            # 新規
└── index.ts                           # エクスポート集約
```

**注**: 各サブコンポーネントは小さく保ち、単一責任の原則を守ります。

## 依存関係

### 既存の依存関係

- `lucide-react`: アイコン（既にプロジェクトで使用中）
- `framer-motion`: アニメーション（既にプロジェクトで使用中）
- `jotai`: 状態管理（必要に応じて）

### 新規の依存関係

なし（既存の依存関係で実装可能）

## コンポーネント詳細設計

### 1. QuestionTypeIcon

質問タイプに応じたアイコンを表示します。

```typescript
import { CheckCircle, Lightbulb, HelpCircle } from "lucide-react"
import type { QuestionType } from "@/types"

const questionTypeConfig: Record<QuestionType, { icon: LucideIcon; label: string; color: string }> = {
  understanding_check: {
    icon: CheckCircle,
    label: "理解確認",
    color: "text-green-600",
  },
  thinking_guide: {
    icon: Lightbulb,
    label: "思考誘導",
    color: "text-yellow-600",
  },
  hint: {
    icon: HelpCircle,
    label: "ヒント",
    color: "text-blue-600",
  },
}

interface QuestionTypeIconProps {
  type: QuestionType
}

export function QuestionTypeIcon({ type }: QuestionTypeIconProps) {
  const config = questionTypeConfig[type]
  const Icon = config.icon

  return (
    <div className="flex items-center gap-1" aria-label={`質問タイプ: ${config.label}`}>
      <Icon className={`h-4 w-4 ${config.color}`} aria-hidden="true" />
    </div>
  )
}
```

### 2. EmotionIcon

感情に応じたアイコンを表示します。既存の `EmotionIndicator` のアイコンマッピングを再利用します。

```typescript
import { Frown, Sparkles, HelpCircle, Smile, AlertCircle, Meh } from "lucide-react"
import type { EmotionType } from "@/types"

const emotionConfig: Record<EmotionType, { icon: LucideIcon; label: string; color: string }> = {
  frustrated: { icon: Frown, label: "困っている", color: "text-red-600" },
  confident: { icon: Sparkles, label: "自信満々", color: "text-green-600" },
  confused: { icon: HelpCircle, label: "わからない", color: "text-blue-600" },
  happy: { icon: Smile, label: "元気いっぱい", color: "text-yellow-600" },
  tired: { icon: AlertCircle, label: "疲れている", color: "text-gray-600" },
  neutral: { icon: Meh, label: "落ち着いている", color: "text-purple-600" },
}

interface EmotionIconProps {
  emotion: EmotionType
}

export function EmotionIcon({ emotion }: EmotionIconProps) {
  const config = emotionConfig[emotion]
  const Icon = config.icon

  return (
    <div className="flex items-center gap-1" aria-label={`感情: ${config.label}`}>
      <Icon className={`h-4 w-4 ${config.color}`} aria-hidden="true" />
    </div>
  )
}
```

### 3. AgentBadge

エージェント名を小さなバッジで表示します。

```typescript
import type { AgentType } from "@/types"

const agentLabels: Record<AgentType, string> = {
  router: "ルーター",
  math_coach: "算数",
  japanese_coach: "国語",
  encouragement: "励まし",
  review: "振り返り",
}

interface AgentBadgeProps {
  agent: AgentType
}

export function AgentBadge({ agent }: AgentBadgeProps) {
  return (
    <div
      className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700"
      aria-label={`エージェント: ${agentLabels[agent]}`}
    >
      {agentLabels[agent]}
    </div>
  )
}
```

### 4. UnderstandingIndicator

理解度をパーセンテージバーで表示します。

```typescript
import type { ResponseAnalysis } from "@/types"

interface UnderstandingIndicatorProps {
  analysis: ResponseAnalysis
}

export function UnderstandingIndicator({ analysis }: UnderstandingIndicatorProps) {
  const percentage = Math.round(analysis.understandingLevel * 100)
  const color = analysis.isCorrectDirection ? "bg-green-500" : "bg-yellow-500"

  return (
    <div className="flex items-center gap-2" aria-label={`理解度: ${percentage}%`}>
      <div className="flex h-2 w-20 overflow-hidden rounded-full bg-gray-200">
        <div className={`${color}`} style={{ width: `${percentage}%` }} />
      </div>
      <span className="text-xs text-gray-600">{percentage}%</span>
      {analysis.needsClarification && (
        <span className="text-xs text-blue-600" aria-label="明確化が必要">
          ?
        </span>
      )}
    </div>
  )
}
```

### 5. ToolExecutionBadges

ツール実行結果を小さなバッジで表示します。

```typescript
import { CheckCircle, XCircle, Loader2 } from "lucide-react"
import type { ToolExecution } from "@/types"

const toolLabels: Record<ToolName, string> = {
  calculate_tool: "けいさん",
  manage_hint_tool: "ヒント",
  record_progress_tool: "きろく",
  check_curriculum_tool: "きょうかしょ",
  analyze_image_tool: "しゃしん",
}

interface ToolExecutionBadgesProps {
  executions: ToolExecution[]
}

export function ToolExecutionBadges({ executions }: ToolExecutionBadgesProps) {
  return (
    <div className="flex flex-wrap gap-1.5">
      {executions.map((execution) => (
        <ToolBadge key={`${execution.toolName}-${execution.timestamp.getTime()}`} execution={execution} />
      ))}
    </div>
  )
}

function ToolBadge({ execution }: { execution: ToolExecution }) {
  const Icon =
    execution.status === "completed"
      ? CheckCircle
      : execution.status === "error"
        ? XCircle
        : Loader2

  const color =
    execution.status === "completed"
      ? "text-green-600"
      : execution.status === "error"
        ? "text-red-600"
        : "text-blue-600"

  return (
    <div className="flex items-center gap-1 rounded-full bg-gray-100 px-2 py-0.5 text-xs">
      <Icon className={`h-3 w-3 ${color}`} aria-hidden="true" />
      <span className="text-gray-700">{toolLabels[execution.toolName]}</span>
    </div>
  )
}
```

### 6. DialogueMetadataHeader

ヘッダー部分（質問タイプ、感情、エージェント）を表示します。

```typescript
import type { DialogueTurn } from "@/types"
import { QuestionTypeIcon } from "./QuestionTypeIcon"
import { EmotionIcon } from "./EmotionIcon"
import { AgentBadge } from "./AgentBadge"

interface DialogueMetadataHeaderProps {
  turn: DialogueTurn
}

export function DialogueMetadataHeader({ turn }: DialogueMetadataHeaderProps) {
  return (
    <div className="mb-1 flex items-center gap-2">
      {turn.questionType && <QuestionTypeIcon type={turn.questionType} />}
      {turn.emotion && <EmotionIcon emotion={turn.emotion} />}
      {turn.activeAgent && <AgentBadge agent={turn.activeAgent} />}
    </div>
  )
}
```

### 7. DialogueMetadataFooter

フッター部分（理解度、ツール実行）を表示します。

```typescript
import type { DialogueTurn } from "@/types"
import { UnderstandingIndicator } from "./UnderstandingIndicator"
import { ToolExecutionBadges } from "./ToolExecutionBadges"

interface DialogueMetadataFooterProps {
  turn: DialogueTurn
}

export function DialogueMetadataFooter({ turn }: DialogueMetadataFooterProps) {
  return (
    <div className="mt-1 flex items-center gap-2">
      {turn.responseAnalysis && <UnderstandingIndicator analysis={turn.responseAnalysis} />}
      {turn.toolExecutions && turn.toolExecutions.length > 0 && (
        <ToolExecutionBadges executions={turn.toolExecutions} />
      )}
    </div>
  )
}
```

### 8. DialogueBubble（拡張版）

既存の `DialogueBubble` を拡張し、メタデータを表示します。

```typescript
import type { DialogueTurn } from "@/types"
import { DialogueMetadataHeader } from "./DialogueMetadataHeader"
import { DialogueMetadataFooter } from "./DialogueMetadataFooter"

interface DialogueBubbleProps {
  turn: DialogueTurn
}

export function DialogueBubble({ turn }: DialogueBubbleProps) {
  const isChild = turn.speaker === "child"
  const hasHeader = turn.questionType || turn.emotion || turn.activeAgent
  const hasFooter = turn.responseAnalysis || (turn.toolExecutions && turn.toolExecutions.length > 0)

  return (
    <div className={`flex ${isChild ? "justify-end" : "justify-start"}`}>
      <div
        className={`
          max-w-[80%] rounded-2xl px-4 py-2
          ${isChild ? "bg-blue-100 text-blue-900" : "bg-gray-100 text-gray-900"}
        `}
      >
        {hasHeader && <DialogueMetadataHeader turn={turn} />}
        <p className="text-sm">{turn.text}</p>
        {hasFooter && <DialogueMetadataFooter turn={turn} />}
      </div>
    </div>
  )
}
```

## エラーハンドリング

### エラーケース

1. **メタデータが不正な値**: 型定義に従わない値が渡された場合
   - 対応: TypeScript の型チェックで防止
   - 実行時エラーの場合: デフォルト値を使用（例: `neutral` emotion）

2. **アイコンが見つからない**: 予期しない値が渡された場合
   - 対応: デフォルトアイコンを表示

### エラーバウンダリ

Phase 2 メタデータの表示エラーが対話履歴全体の表示を妨げないよう、各サブコンポーネントでエラーハンドリングを実装します。

## セキュリティ考慮事項

- **XSS 対策**: 対話テキストは React が自動でエスケープ
- **データ検証**: TypeScript の型チェックで不正なデータを防止

## パフォーマンス考慮事項

### 最適化戦略

1. **React.memo の使用**: `DialogueBubble` を `React.memo` でラップし、不要な再レンダリングを防止
2. **仮想スクロール（将来の拡張）**: 大量の対話（1000+ ターン）の場合、仮想スクロールを検討
3. **遅延ロード（将来の拡張）**: アイコンライブラリの遅延ロード

### パフォーマンス目標

- 100 ターンの対話履歴を 1 秒以内にレンダリング
- スクロール時のフレームレート 60fps 以上

## 代替案と採用理由

### 代替案1: メタデータをホバー時のみ表示

**メリット**: UI がシンプルになる

**デメリット**: モバイルでホバーが使えない、メタデータの可視性が低い

**採用理由**: Phase 2 メタデータは常に表示することで、学習プロセスの透明性を高める

### 代替案2: メタデータを別のパネルに表示

**メリット**: 対話吹き出しがシンプルに保たれる

**デメリット**: 対話とメタデータの関連性が分かりにくい

**採用理由**: 対話とメタデータを同じ吹き出し内に表示することで、関連性を明確にする

### 代替案3: すべてのメタデータを1つのコンポーネントに統合

**メリット**: ファイル数が少なくなる

**デメリット**: コンポーネントが肥大化し、テストやメンテナンスが困難になる

**採用理由**: 単一責任の原則に従い、各メタデータを独立したサブコンポーネントとして実装
