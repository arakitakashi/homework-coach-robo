# Design - 学習プロファイル表示コンポーネント

## アーキテクチャ概要

```
LearningProfile (Jotai atom連携)
├── ProfileSummary (セッション数・問題解決数)
├── ThinkingTendenciesDisplay (既存コンポーネント再利用)
└── SubjectCard[] (教科別理解度)
    └── TrendBadge (トレンド表示)
```

## コンポーネント構成

```
frontend/components/features/LearningProfile/
├── LearningProfile.tsx
├── LearningProfile.test.tsx
├── ProfileSummary.tsx
├── ProfileSummary.test.tsx
├── SubjectCard.tsx
├── SubjectCard.test.tsx
├── TrendBadge.tsx
├── TrendBadge.test.tsx
└── index.ts
```

## 各コンポーネント設計

### TrendBadge
- Props: `{ trend: "improving" | "stable" | "declining" }`
- Lucideアイコン + ラベル + 色分け

### ProfileSummary
- Props: `{ totalSessions: number; totalProblemsSolved: number }`
- BookOpen + CheckCircle2 アイコン

### SubjectCard
- Props: `{ understanding: SubjectUnderstanding }`
- 習熟度バー + TrendBadge + 得意/苦手タグ

### LearningProfile
- Jotai `learningProfileAtom` から取得
- null時は `return null`

## 依存関係

- `@/types/phase2` - 型定義
- `@/store/atoms/phase2` - learningProfileAtom
- `@/components/features/ProgressDisplay` - ThinkingTendenciesDisplay
- `lucide-react` - アイコン
