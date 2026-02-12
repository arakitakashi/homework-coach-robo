# Design - ProgressDisplay拡張（教科・トピック対応）

## アーキテクチャ概要

既存の`ProgressDisplay`コンポーネントを拡張し、Phase 2bで追加された教科・トピック・思考の傾向の情報を表示する。既存の進捗表示（自分で・ヒントで・一緒に）はそのまま維持し、その上部または下部に新しい情報を追加する。

## 技術選定

- **フレームワーク**: Next.js 16 (App Router) + React
- **言語**: TypeScript (strict mode)
- **スタイリング**: Tailwind CSS
- **テスト**: Vitest + Testing Library
- **アクセシビリティ**: セマンティックHTML + ARIA属性

## データ設計

### 入力データ

```typescript
// LearningProgress型（既存、拡張済み）
interface LearningProgress {
  selfDiscoveryCount: number
  hintDiscoveryCount: number
  togetherCount: number
  currentSubject?: SubjectType      // 追加フィールド
  currentTopic?: string             // 追加フィールド
  thinkingTendencies?: ThinkingTendencies  // 追加フィールド
}

// SubjectType型（既存）
type SubjectType = "math" | "japanese"

// ThinkingTendencies型（既存）
interface ThinkingTendencies {
  persistenceScore: number       // 0〜100
  independenceScore: number      // 0〜100
  reflectionQuality: number      // 0〜100
  hintDependency: number         // 0〜100
  updatedAt: Date
}
```

### 教科アイコン・カラーのマッピング

```typescript
const SUBJECT_CONFIG = {
  math: {
    icon: '🧮',
    label: '算数',
    bgColor: 'bg-blue-100',
    textColor: 'text-blue-600',
    borderColor: 'border-blue-300',
  },
  japanese: {
    icon: '📖',
    label: '国語',
    bgColor: 'bg-green-100',
    textColor: 'text-green-600',
    borderColor: 'border-green-300',
  },
} as const
```

## コンポーネント設計

### コンポーネント階層

```
ProgressDisplay (既存、拡張)
├── SubjectDisplay (新規)        - 教科・トピック表示
│   ├── SubjectBadge (新規)      - 教科バッジ（アイコン + ラベル）
│   └── TopicLabel (新規)        - トピック表示
├── [既存の進捗表示]
│   ├── ProgressItem (既存)
│   ├── ProgressItem (既存)
│   └── ProgressItem (既存)
└── ThinkingTendenciesDisplay (新規) - 思考の傾向表示
    ├── TendencyBar (新規)       - 各傾向のプログレスバー
    ├── TendencyBar (新規)
    ├── TendencyBar (新規)
    └── TendencyBar (新規)
```

### 各コンポーネントの責務

#### 1. `ProgressDisplay`（拡張）
- **責務**: 全体のレイアウト、条件付きレンダリング
- **Props**: `LearningProgress`型
- **レンダリング条件**:
  - `currentSubject`または`currentTopic`が存在する場合、`SubjectDisplay`を表示
  - `thinkingTendencies`が存在する場合、`ThinkingTendenciesDisplay`を表示

#### 2. `SubjectDisplay`（新規）
- **責務**: 教科とトピックの表示
- **Props**:
  ```typescript
  interface SubjectDisplayProps {
    subject?: SubjectType
    topic?: string
  }
  ```
- **レイアウト**: 横並び（教科バッジ + トピック）

#### 3. `SubjectBadge`（新規）
- **責務**: 教科のアイコンとラベル表示
- **Props**:
  ```typescript
  interface SubjectBadgeProps {
    subject: SubjectType
  }
  ```
- **スタイル**: 丸みのあるバッジ、教科ごとの色

#### 4. `TopicLabel`（新規）
- **責務**: トピック名の表示
- **Props**:
  ```typescript
  interface TopicLabelProps {
    topic: string
  }
  ```
- **スタイル**: シンプルなテキスト表示

#### 5. `ThinkingTendenciesDisplay`（新規）
- **責務**: 思考の傾向の視覚化
- **Props**:
  ```typescript
  interface ThinkingTendenciesDisplayProps {
    tendencies: ThinkingTendencies
  }
  ```
- **レイアウト**: 各傾向を縦に並べる

#### 6. `TendencyBar`（新規）
- **責務**: 個別の傾向のプログレスバー表示
- **Props**:
  ```typescript
  interface TendencyBarProps {
    label: string
    score: number  // 0〜100
    invert?: boolean  // hintDependencyの場合true（低い方が良い）
  }
  ```
- **スタイル**: ラベル + プログレスバー

## ファイル構成

```
frontend/components/features/ProgressDisplay/
├── ProgressDisplay.tsx                 # 既存ファイル（拡張）
├── ProgressDisplay.test.tsx            # 既存ファイル（更新）
├── SubjectDisplay.tsx                  # 新規
├── SubjectDisplay.test.tsx             # 新規
├── ThinkingTendenciesDisplay.tsx       # 新規
├── ThinkingTendenciesDisplay.test.tsx  # 新規
└── index.ts                            # エクスポート集約（更新）
```

## UIレイアウト

### デスクトップレイアウト（768px以上）

```
┌─────────────────────────────────────────┐
│  🧮 算数  ｜  トピック: 足し算の筆算     │  ← SubjectDisplay
├─────────────────────────────────────────┤
│            250 ポイント                 │
│  [自分で: 3] [ヒントで: 2] [一緒に: 1] │  ← 既存の進捗表示
├─────────────────────────────────────────┤
│  思考の傾向                             │
│  粘り強さ    ███████░░░ 70%            │
│  自立度      ████████░░ 80%            │
│  振り返り    ██████░░░░ 60%            │
│  ヒント依存  ████░░░░░░ 40%            │  ← ThinkingTendenciesDisplay
└─────────────────────────────────────────┘
```

### モバイルレイアウト（375px〜）

```
┌───────────────────────┐
│  🧮 算数              │
│  トピック: 足し算の筆算 │  ← SubjectDisplay（縦並び）
├───────────────────────┤
│      250 ポイント     │
│  [3] [2] [1]          │  ← 既存（コンパクト）
├───────────────────────┤
│  思考の傾向           │
│  粘り強さ ███░ 70%   │
│  自立度   ████ 80%   │
│  振り返り ███░ 60%   │
│  ヒント依存 ██░ 40%  │  ← ThinkingTendenciesDisplay
└───────────────────────┘
```

## エラーハンドリング

### 未設定フィールドの処理

```typescript
// currentSubject, currentTopic が undefined の場合
if (!currentSubject && !currentTopic) {
  // SubjectDisplay を表示しない
  return null
}

// thinkingTendencies が undefined の場合
if (!thinkingTendencies) {
  // ThinkingTendenciesDisplay を表示しない
  return null
}
```

### スコアの範囲チェック

```typescript
// TendencyBar で 0〜100 の範囲外を防ぐ
const normalizedScore = Math.max(0, Math.min(100, score))
```

## セキュリティ考慮事項

- XSS対策: Reactのデフォルトエスケープに依存（特別な対応不要）
- 入力検証: バックエンドで実施済み（フロントエンドは型チェックのみ）

## パフォーマンス考慮事項

### メモ化

```typescript
// 教科設定のメモ化（再計算を防ぐ）
const subjectConfig = useMemo(() => {
  return currentSubject ? SUBJECT_CONFIG[currentSubject] : null
}, [currentSubject])
```

### 条件付きレンダリング

- 未設定フィールドは早期リターンで不要なDOMノードを生成しない

## アクセシビリティ考慮事項

### 1. セマンティックHTML

```typescript
// 教科・トピックはセクションとして定義
<section aria-label="現在の学習内容">
  <SubjectDisplay subject={currentSubject} topic={currentTopic} />
</section>
```

### 2. ARIA属性

```typescript
// プログレスバーにはrole="progressbar"とaria-valuenow
<div
  role="progressbar"
  aria-valuenow={score}
  aria-valuemin={0}
  aria-valuemax={100}
  aria-label={`${label}: ${score}%`}
>
```

### 3. カラーコントラスト

- WCAG 2.1 AA基準を満たすカラーパレット
- Tailwind CSSのデフォルトカラーを使用（既にコントラスト比を満たしている）

## 代替案と採用理由

### 代替案1: 単一の大きなコンポーネント

```typescript
// すべてを ProgressDisplay 内に記述
export function ProgressDisplay({ ... }) {
  return (
    <div>
      {/* 教科表示 */}
      {currentSubject && <div>...</div>}
      {/* 既存の進捗 */}
      <div>...</div>
      {/* 思考の傾向 */}
      {thinkingTendencies && <div>...</div>}
    </div>
  )
}
```

**不採用理由**:
- 単一責任の原則に反する
- テストが複雑になる
- 再利用性が低い

### 代替案2: 教科とトピックを別々のコンポーネントに

```typescript
<SubjectBadge subject={currentSubject} />
<TopicLabel topic={currentTopic} />
```

**不採用理由**:
- レイアウトの一貫性が損なわれる
- 親コンポーネントでレイアウトロジックが複雑になる

### 採用案: 階層的なコンポーネント構成

**採用理由**:
- 各コンポーネントが単一責任を持つ
- テストが容易
- 再利用性が高い
- レイアウトの変更が柔軟

## テスト戦略

### テストケース

1. **SubjectDisplay**
   - 教科のみ存在する場合
   - トピックのみ存在する場合
   - 両方存在する場合
   - 両方未設定の場合（表示されない）

2. **SubjectBadge**
   - 算数の場合（アイコン、ラベル、カラー確認）
   - 国語の場合（アイコン、ラベル、カラー確認）

3. **ThinkingTendenciesDisplay**
   - 正常な傾向データの場合
   - スコアが範囲外の場合（0未満、100超）
   - 未設定の場合（表示されない）

4. **TendencyBar**
   - スコア0の場合
   - スコア50の場合
   - スコア100の場合
   - invert=trueの場合（色が反転）

5. **ProgressDisplay（統合）**
   - すべてのフィールドが存在する場合
   - 一部のフィールドのみ存在する場合
   - Phase 2フィールドがすべて未設定の場合（既存表示のみ）

### カバレッジ目標

- 80%以上（`bun test --coverage`で確認）
