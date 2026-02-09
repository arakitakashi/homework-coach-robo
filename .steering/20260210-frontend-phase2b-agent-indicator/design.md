# Design - Phase 2b エージェント切り替えUIコンポーネント

## アーキテクチャ概要

`AgentIndicator` コンポーネントは、Jotai atoms（`activeAgentAtom`）を購読し、現在のアクティブエージェントをリアルタイムに表示します。エージェント切り替え時には、Framer Motionを使用したアニメーションでスムーズな視覚的フィードバックを提供します。

```
┌─────────────────────────────────────┐
│       SessionContent.tsx            │
│  ┌───────────────────────────────┐  │
│  │     AgentIndicator            │  │
│  │  - activeAgentAtom 購読       │  │
│  │  - エージェント名表示         │  │
│  │  - 教科アイコン表示           │  │
│  │  - 切り替えアニメーション     │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
         ↑
         │ WebSocket Message
         │ (AgentTransitionMessage)
         │
┌─────────────────────────────────────┐
│    useDialogue フック               │
│  - handleAgentTransition            │
│  - activeAgentAtom 更新             │
└─────────────────────────────────────┘
```

## 技術選定

| 技術 | 用途 | 理由 |
|------|------|------|
| **Jotai** | 状態管理 | 既存の`activeAgentAtom`を活用 |
| **Framer Motion** | アニメーション | React向けアニメーションライブラリ、宣言的API |
| **Tailwind CSS** | スタイリング | プロジェクト標準 |
| **Lucide React** | アイコン | 軽量で一貫性のあるアイコンセット |
| **Vitest + Testing Library** | テスト | プロジェクト標準 |

## データ設計

### 使用する型定義（`types/phase2.ts`）

```typescript
// エージェントタイプ
type AgentType = 'router' | 'math_coach' | 'japanese_coach' | 'encouragement' | 'review';

// アクティブエージェント
interface ActiveAgent {
  type: AgentType;
  activatedAt: string; // ISO 8601 timestamp
}

// エージェント切り替え履歴
interface AgentTransition {
  from: AgentType;
  to: AgentType;
  reason?: string;
  timestamp: string;
}
```

### Jotai Atoms（`store/atoms/phase2.ts`）

```typescript
// 既存のatoms（変更なし）
export const activeAgentAtom = atom<ActiveAgent | null>(null);
export const agentTransitionHistoryAtom = atom<AgentTransition[]>([]);
```

## ファイル構成

```
frontend/components/features/AgentIndicator/
├── AgentIndicator.tsx          # メインコンポーネント
├── AgentIndicator.test.tsx     # ユニットテスト
├── AgentIcon.tsx               # エージェントアイコンコンポーネント
├── AgentIcon.test.tsx          # アイコンテスト
└── index.ts                    # エクスポート集約
```

## コンポーネント設計

### AgentIndicator.tsx

```typescript
'use client';

import { useAtom } from 'jotai';
import { motion, AnimatePresence } from 'framer-motion';
import { activeAgentAtom } from '@/store/atoms/phase2';
import { AgentIcon } from './AgentIcon';
import type { AgentType } from '@/types/phase2';

// エージェント名のマッピング
const AGENT_LABELS: Record<AgentType, string> = {
  router: 'ルーター',
  math_coach: '算数コーチ',
  japanese_coach: '国語コーチ',
  encouragement: '励まし',
  review: '振り返り',
};

export function AgentIndicator() {
  const [activeAgent] = useAtom(activeAgentAtom);

  if (!activeAgent) {
    return null; // エージェントがアクティブでない場合は非表示
  }

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={activeAgent.type}
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 10 }}
        transition={{ duration: 0.3 }}
        className="flex items-center gap-2 rounded-lg bg-blue-50 px-3 py-2 text-sm"
        aria-label={`現在のエージェント: ${AGENT_LABELS[activeAgent.type]}`}
      >
        <AgentIcon type={activeAgent.type} />
        <span className="font-medium text-blue-700">
          {AGENT_LABELS[activeAgent.type]}
        </span>
      </motion.div>
    </AnimatePresence>
  );
}
```

### AgentIcon.tsx

```typescript
import { Calculator, BookOpen, Heart, ClipboardList, Router } from 'lucide-react';
import type { AgentType } from '@/types/phase2';

interface AgentIconProps {
  type: AgentType;
  className?: string;
}

const AGENT_ICONS = {
  router: Router,
  math_coach: Calculator,
  japanese_coach: BookOpen,
  encouragement: Heart,
  review: ClipboardList,
} as const;

export function AgentIcon({ type, className = 'h-5 w-5' }: AgentIconProps) {
  const Icon = AGENT_ICONS[type];
  return <Icon className={className} aria-hidden="true" />;
}
```

## SessionContent.tsx への統合

```typescript
// SessionContent.tsx（部分的な例）
import { AgentIndicator } from '@/components/features/AgentIndicator';

export function SessionContent() {
  // ... 既存のコード

  return (
    <div className="flex flex-col h-full">
      {/* エージェントインジケーター */}
      <div className="p-4 border-b">
        <AgentIndicator />
      </div>

      {/* 既存のコンテンツ */}
      <div className="flex-1 overflow-y-auto">
        {/* ... */}
      </div>
    </div>
  );
}
```

## 依存関係

### 新規追加

```json
{
  "dependencies": {
    "framer-motion": "^11.15.1",
    "lucide-react": "^0.468.0"
  }
}
```

**注**: 既にインストール済みの可能性があるため、`package.json` を確認してから追加する。

## エラーハンドリング

### ケース1: activeAgentがnull

- **対応**: コンポーネントを非表示にする（early return）
- **理由**: セッション開始前や終了後はエージェントがアクティブでない

### ケース2: 不明なAgentType

- **対応**: TypeScript型チェックで防止（`AgentType` は union type）
- **フォールバック**: 万が一の場合は「不明なエージェント」と表示

## アニメーション仕様

### エージェント切り替えアニメーション

```typescript
{
  initial: { opacity: 0, y: -10 },  // 上からフェードイン
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: 10 },      // 下へフェードアウト
  transition: { duration: 0.3 }     // 300ms
}
```

### パフォーマンス考慮

- `AnimatePresence` の `mode="wait"` を使用し、前の要素が完全に消えてから次の要素を表示
- GPU加速されるプロパティ（`opacity`, `transform`）のみを使用

## アクセシビリティ考慮事項

### ARIA属性

```tsx
<div aria-label={`現在のエージェント: ${AGENT_LABELS[activeAgent.type]}`}>
  <Icon aria-hidden="true" />
  <span>{AGENT_LABELS[activeAgent.type]}</span>
</div>
```

### キーボードナビゲーション

- 本コンポーネントは情報表示のみ（インタラクティブ要素なし）
- キーボード操作は不要

## テスト戦略

### ユニットテスト（AgentIndicator.test.tsx）

```typescript
describe('AgentIndicator', () => {
  it('activeAgentがnullの場合、何も表示しない', () => {
    // activeAgentAtom = null でレンダリング
    // 何も表示されないことを確認
  });

  it('activeAgentが設定されている場合、エージェント名とアイコンを表示', () => {
    // activeAgentAtom = { type: 'math_coach', activatedAt: '2026-02-10T00:00:00Z' }
    // 「算数コーチ」が表示されることを確認
    // Calculatorアイコンが表示されることを確認
  });

  it('エージェント切り替え時にアニメーションが実行される', async () => {
    // activeAgentAtom を math_coach → japanese_coach に変更
    // アニメーションが実行されることを確認（waitForを使用）
  });
});
```

### Jotaiテストパターン

```typescript
import { Provider, createStore } from 'jotai';
import { activeAgentAtom } from '@/store/atoms/phase2';

const TestWrapper = ({ children, initialAgent }: { children: ReactNode; initialAgent?: ActiveAgent | null }) => {
  const store = useMemo(() => {
    const s = createStore();
    if (initialAgent !== undefined) {
      s.set(activeAgentAtom, initialAgent);
    }
    return s;
  }, [initialAgent]);
  return <Provider store={store}>{children}</Provider>;
};
```

## セキュリティ考慮事項

- **XSS対策**: エージェント名は定数（`AGENT_LABELS`）から取得するため、XSSリスクなし
- **入力検証**: `AgentType` は型安全な union type で制約済み

## パフォーマンス考慮事項

### 最適化ポイント

1. **React.memo**: `AgentIcon` を memo化し、不要な再レンダリングを防ぐ
2. **useMemo**: アイコンコンポーネントの選択をメモ化
3. **アトム粒度**: `activeAgentAtom` のみを購読し、不要な依存を避ける

## 代替案と採用理由

### 代替案1: CSS Transitionのみ使用

- **メリット**: 依存パッケージ不要
- **デメリット**: `AnimatePresence` のような要素の追加/削除アニメーションが複雑
- **採用しない理由**: Framer Motionはプロジェクトで既に使用されている可能性があり、宣言的で保守性が高い

### 代替案2: エージェント切り替え履歴を表示

- **メリット**: デバッグやユーザーへの透明性向上
- **デメリット**: UIが複雑化し、小学生には理解しづらい
- **採用しない理由**: Out of Scope（将来の拡張として検討）
