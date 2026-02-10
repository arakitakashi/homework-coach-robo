# Design - フロントエンド ゲーミフィケーション要素

## アーキテクチャ概要

```
SessionContent
├── PointDisplay (新規)
├── BadgeNotification (新規)
├── StoryProgress (新規)
└── 既存コンポーネント
    ├── CharacterDisplay
    ├── VoiceInterface
    ├── AgentIndicator
    └── EmotionIndicator
```

**設計原則**:
- **段階的実装**: Phase 1はフロントエンドのみ、Phase 2でバックエンド連携
- **既存型の拡張**: `LearningProgress`を破壊的変更なしで拡張
- **コンポーネント分離**: 各ゲーミフィケーション要素を独立したコンポーネントに

---

## 技術選定

| カテゴリ | 技術 | 理由 |
|---------|------|------|
| アニメーション | Framer Motion | 既存（EmotionIndicator）で使用済み |
| 状態管理 | Jotai | 既存の状態管理と統一 |
| スタイリング | Tailwind CSS | プロジェクト標準 |
| アイコン | Lucide React | 軽量、既存で使用中 |
| テスト | Vitest + Testing Library | プロジェクト標準 |

---

## データ設計

### 型定義（`types/gamification.ts` - 新規作成）

```typescript
/**
 * ポイント獲得理由
 */
export type PointReason =
  | 'self_discovery'      // 自分で気づいた (3pt)
  | 'hint_discovery'      // ヒントで気づいた (2pt)
  | 'collaborative'       // 一緒に解いた (1pt)
  | 'bonus_streak'        // 連続正解ボーナス
  | 'bonus_first_clear';  // 初回クリアボーナス

/**
 * ポイント獲得イベント
 */
export interface PointEvent {
  points: number;
  reason: PointReason;
  timestamp: number;
  problemId?: string;
}

/**
 * バッジ定義
 */
export interface Badge {
  id: string;
  name: string;
  description: string;
  iconName: string; // Lucide icon name
  category: 'achievement' | 'streak' | 'mastery';
  unlockedAt?: number; // timestamp
}

/**
 * ストーリーチャプター
 */
export interface StoryChapter {
  id: string;
  title: string;
  description: string;
  requiredPoints: number;
  completed: boolean;
}

/**
 * ゲーミフィケーション状態
 */
export interface GamificationState {
  totalPoints: number;
  sessionPoints: number;
  level: number;
  badges: Badge[];
  currentChapter: StoryChapter;
  pointHistory: PointEvent[];
}
```

### Jotai Atoms（`store/atoms/gamification.ts` - 新規作成）

```typescript
import { atom } from 'jotai';
import type { GamificationState, PointEvent, Badge } from '@/types/gamification';

// ゲーミフィケーション状態
export const gamificationStateAtom = atom<GamificationState>({
  totalPoints: 0,
  sessionPoints: 0,
  level: 1,
  badges: [],
  currentChapter: {
    id: 'ch1',
    title: '冒険の始まり',
    description: 'ロボと一緒に最初の問題に挑戦しよう！',
    requiredPoints: 10,
    completed: false,
  },
  pointHistory: [],
});

// ポイント追加アクション（derived atom）
export const addPointsAtom = atom(
  null,
  (get, set, event: PointEvent) => {
    const state = get(gamificationStateAtom);
    const newTotalPoints = state.totalPoints + event.points;
    const newSessionPoints = state.sessionPoints + event.points;
    const newLevel = Math.floor(newTotalPoints / 50) + 1;

    set(gamificationStateAtom, {
      ...state,
      totalPoints: newTotalPoints,
      sessionPoints: newSessionPoints,
      level: newLevel,
      pointHistory: [...state.pointHistory, event],
    });
  }
);

// バッジ獲得アクション
export const unlockBadgeAtom = atom(
  null,
  (get, set, badge: Badge) => {
    const state = get(gamificationStateAtom);
    const alreadyUnlocked = state.badges.some(b => b.id === badge.id);

    if (!alreadyUnlocked) {
      set(gamificationStateAtom, {
        ...state,
        badges: [
          ...state.badges,
          { ...badge, unlockedAt: Date.now() }
        ],
      });
    }
  }
);

// 最近獲得したバッジ（5秒以内）
export const recentBadgeAtom = atom<Badge | null>((get) => {
  const state = get(gamificationStateAtom);
  const recent = state.badges
    .filter(b => b.unlockedAt && Date.now() - b.unlockedAt < 5000)
    .sort((a, b) => (b.unlockedAt || 0) - (a.unlockedAt || 0))[0];

  return recent || null;
});
```

### LearningProgress型の拡張（`types/index.ts` - 既存ファイル）

```typescript
// 既存の型を破壊せず、オプショナルフィールドで拡張
export interface LearningProgress {
  // 既存フィールド
  problem: string;
  hintsUsed: number;
  resolved: boolean;
  resolutionType?: 'self_discovery' | 'hint_discovery' | 'collaborative';

  // ゲーミフィケーション拡張（Phase 1ではモック、Phase 2でバックエンド実装）
  pointsEarned?: number;
  pointReason?: PointReason;
}
```

---

## コンポーネント設計

### 1. PointDisplay コンポーネント

**責務**: 現在のポイント・レベルを表示

**Props**: なし（Jotai atomから取得）

**デザイン**:
```
┌─────────────────────┐
│ ⭐ Level 3          │
│ 💎 125 / 150 pts    │  ← プログレスバー
└─────────────────────┘
```

**ファイル構成**:
```
components/features/gamification/PointDisplay/
├── PointDisplay.tsx
├── PointDisplay.test.tsx
├── LevelProgressBar.tsx
└── index.ts
```

### 2. BadgeNotification コンポーネント

**責務**: バッジ獲得時のトースト通知

**Props**: なし（Jotai atomから最近のバッジを取得）

**デザイン**:
```
┌─────────────────────────┐
│ 🏆 バッジ獲得！        │
│ 「初めての問題クリア」  │
└─────────────────────────┘
  ↑ Framer Motion でスライドイン
```

**アニメーション**:
- フェードイン + スライドアップ
- 3秒後に自動消滅

**ファイル構成**:
```
components/features/gamification/BadgeNotification/
├── BadgeNotification.tsx
├── BadgeNotification.test.tsx
└── index.ts
```

### 3. StoryProgress コンポーネント

**責務**: ストーリー進行状況の表示

**Props**: なし（Jotai atomから取得）

**デザイン**:
```
┌──────────────────────────────┐
│ 📖 Chapter 1: 冒険の始まり   │
│ ─────────────────────────    │ ← プログレスバー
│ 8 / 10 pts                   │
└──────────────────────────────┘
```

**ファイル構成**:
```
components/features/gamification/StoryProgress/
├── StoryProgress.tsx
├── StoryProgress.test.tsx
├── ChapterCard.tsx
└── index.ts
```

### 4. 統合（SessionContent.tsx）

```tsx
// 既存のSessionContentにゲーミフィケーション要素を追加
export function SessionContent() {
  // ... 既存のロジック

  return (
    <div className="...">
      {/* 新規追加: ゲーミフィケーション要素 */}
      <div className="gamification-panel">
        <PointDisplay />
        <StoryProgress />
      </div>

      {/* 既存コンポーネント */}
      <CharacterDisplay ... />
      <VoiceInterface ... />

      {/* トースト通知 */}
      <BadgeNotification />
    </div>
  );
}
```

---

## エラーハンドリング

- **Atomの初期化失敗**: デフォルト値にフォールバック
- **アニメーション失敗**: Framer Motionのフォールバック（静的表示）
- **不正なポイント値**: コンソール警告 + 無視

---

## パフォーマンス考慮事項

- **メモ化**: `useMemo`で高頻度計算をキャッシュ
- **仮想化**: バッジリストが多い場合は仮想スクロール（将来実装）
- **アニメーション最適化**: `will-change: transform` でGPU加速

---

## セキュリティ考慮事項

- **Phase 1（モックデータ）**: セキュリティリスクなし
- **Phase 2（バックエンド連携）**:
  - ポイント計算はバックエンドで実施
  - フロントエンドは表示のみ
  - WebSocket経由でポイント更新を受信

---

## 代替案と採用理由

### 代替案1: すべてのポイント計算をフロントエンドで実施
- **却下理由**: セキュリティリスク（不正な加算が可能）

### 代替案2: バッジをサーバーサイドレンダリング
- **却下理由**: アニメーションが必要なため、クライアントサイドが適切

### 代替案3: Zustand を状態管理に使用
- **却下理由**: プロジェクト標準はJotai、統一性を優先
