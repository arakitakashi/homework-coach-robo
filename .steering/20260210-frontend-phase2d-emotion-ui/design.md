# Design - Phase 2d 感情適応UIコンポーネント

## アーキテクチャ概要

```
SessionContent
├── EmotionIndicator (新規)
│   ├── emotionAnalysisAtom 購読
│   ├── emotionAdaptationAtom 購読
│   └── 感情状態・レベル・サポートを表示
│
└── CharacterDisplay (拡張)
    ├── emotionAnalysisAtom 購読
    └── 感情に応じた表情変化
```

## 技術選定

- **UIライブラリ**: React 19
- **状態管理**: Jotai（既存のatoms使用）
- **スタイリング**: Tailwind CSS
- **アニメーション**: Framer Motion
- **アイコン**: Lucide React
- **テスト**: Vitest + Testing Library

## データ設計

### 使用する既存の型（`frontend/types/phase2.ts`）

```typescript
// 感情タイプ
type EmotionType = 'frustrated' | 'confident' | 'confused' | 'happy' | 'tired' | 'neutral'

// レベル
type Level = 'low' | 'medium' | 'high'

// サポートレベル
type SupportLevel = 'minimal' | 'moderate' | 'intensive'

// 感情分析
interface EmotionAnalysis {
  currentEmotion: EmotionType
  frustrationLevel: Level
  engagementLevel: Level
  triggerEvent?: string
  timestamp: Date
}

// 感情適応
interface EmotionAdaptation {
  supportLevel: SupportLevel
  suggestedActions: string[]
  adaptationReason: string
}
```

### 使用するJotai atoms（`frontend/store/atoms/phase2.ts`）

- `emotionAnalysisAtom`: 現在の感情分析状態
- `emotionAdaptationAtom`: 現在の適応状態
- `emotionHistoryAtom`: 感情履歴（配列）

## コンポーネント設計

### 1. EmotionIndicator

**責務**: 現在の感情状態とサポートレベルを視覚的に表示

**Props**: なし（atomsから直接購読）

**UI構成**:
```
┌─────────────────────────────────┐
│ 😊 元気いっぱい                    │
│ ──────────────────────────      │
│ やる気: ■■■□□ (中)              │
│ 集中度: ■■■■■ (高)              │
│ サポート: 📚 普通                │
└─────────────────────────────────┘
```

### 2. CharacterDisplay（拡張）

**既存機能**: キャラクターの状態アニメーション
**追加機能**: 感情に応じた表情変化

**感情→表情マッピング**:
- `frustrated`: 目が困った形、口が下がる、赤みがかった色
- `confident`: 目が輝く、口が笑顔、明るい色
- `confused`: 目が疑問形、口が「？」、青みがかった色
- `happy`: 目がキラキラ、口が大きな笑顔、黄色
- `tired`: 目が半開き、口が平ら、灰色がかった色
- `neutral`: デフォルトの表情

## ファイル構成

```
frontend/
├── components/features/
│   ├── EmotionIndicator/          # 新規
│   │   ├── EmotionIndicator.tsx
│   │   ├── EmotionIndicator.test.tsx
│   │   ├── EmotionLevelBar.tsx    # レベルバーサブコンポーネント
│   │   └── index.ts
│   │
│   └── CharacterDisplay/           # 拡張
│       ├── CharacterDisplay.tsx    # 感情連動追加
│       └── CharacterDisplay.test.tsx # テスト更新
│
└── src/app/session/
    ├── SessionContent.tsx          # 統合
    └── SessionContent.test.tsx     # テスト更新
```

## エラーハンドリング

- atomsが未定義の場合のフォールバック表示
- アニメーション失敗時のグレースフルデグラデーション

## セキュリティ考慮事項

- ユーザー入力なし（表示のみ）
- XSS対策: emotionType等は型制約済み

## パフォーマンス考慮事項

- `emotionAnalysisAtom`の変更時のみ再レンダリング
- Framer Motionの`AnimatePresence`で最適化
- メモ化（`useMemo`）を適切に使用

## 代替案と採用理由

### 採用案: 独立したEmotionIndicatorコンポーネント
- **メリット**: 関心の分離、再利用性、テスト容易性
- **デメリット**: コンポーネント数の増加

### 却下案: CharacterDisplayに統合
- **デメリット**: 責務が過大、テストが複雑化
