# Frontend Development Rule

**このルールは、フロントエンド（Next.js / React / TypeScript）のすべての実装に対して強制的に適用されます。**

---

## 必須スキル参照

### 🚨 実装開始前の必須アクション

フロントエンド実装を開始する前に、**必ず以下の2つのスキルを参照すること**。

#### 1. `/frontend` スキル（実装ガイドライン）

```
/frontend
```

**参照タイミング**: すべてのフロントエンド実装の開始前

**含まれる内容**:
- プロジェクト構造（Next.js App Router）
- TypeScript型定義規約
- Reactコンポーネント規約
- 命名規則
- Tailwind CSS使用方法
- アクセシビリティ（a11y）
- Vitest + Testing Library
- Zodバリデーション
- 状態管理（Jotai）
- エラーハンドリング

#### 2. `/frontend-design` スキル（UIデザインガイドライン）

```
/frontend-design
```

**参照タイミング**: UIコンポーネントやページの実装開始前

**含まれる内容**:
- デザイン原則
- UIコンポーネント設計
- レスポンシブデザイン
- アニメーション・インタラクション
- カラーパレット・タイポグラフィ
- ユーザビリティ考慮事項

---

## 技術スタック

| カテゴリ | 技術 |
|----------|------|
| フレームワーク | Next.js 16 (App Router) |
| ランタイム | Bun |
| 言語 | TypeScript（strict mode） |
| スタイリング | Tailwind CSS |
| 状態管理 | Jotai |
| フォーム | React Hook Form + Zod |
| テスト | Vitest + Testing Library |
| リンター/フォーマッター | Biome |

---

## 基本原則

### 1. 型安全性の徹底

```typescript
// ✅ 正しい: 明示的な型定義
interface VoiceInterfaceProps {
  sessionId: string;
  onComplete: (result: SessionResult) => void;
}

// ❌ 禁止: any型の使用
const handleData = (data: any) => { ... }
```

### 2. 関数コンポーネントの使用

```typescript
// ✅ 正しい: 関数コンポーネント
export function VoiceInterface({ sessionId }: VoiceInterfaceProps) {
  return <div>...</div>;
}

// ❌ 禁止: クラスコンポーネント
class VoiceInterface extends React.Component { ... }
```

### 3. Tailwind CSSでのスタイリング

```tsx
// ✅ 正しい: Tailwind CSS
<button className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">
  送信
</button>

// ❌ 禁止: インラインスタイル
<button style={{ padding: '8px 16px', backgroundColor: 'blue' }}>
  送信
</button>
```

### 4. 状態管理はJotai

```typescript
// ✅ 正しい: Jotai atoms
import { atom, useAtom } from 'jotai';

const sessionAtom = atom<Session | null>(null);

export function useSession() {
  return useAtom(sessionAtom);
}

// ❌ 禁止: useContextでのグローバル状態
```

### 5. Server Components優先

```typescript
// ✅ 正しい: デフォルトはServer Component
// app/page.tsx
export default async function HomePage() {
  const data = await fetchData();
  return <PageContent data={data} />;
}

// 必要な場合のみClient Component
// components/features/VoiceInterface/VoiceInterface.tsx
'use client';
export function VoiceInterface() { ... }
```

---

## ターゲットユーザーへの配慮

**重要**: このプロジェクトのターゲットユーザーは小学校低学年（1〜3年生）です。

### UIの原則

1. **シンプルで直感的**: 複雑な操作を避け、最小限のインタラクション
2. **大きなタッチターゲット**: ボタンは最小44×44px以上
3. **視覚的フィードバック**: 操作結果を明確に表示
4. **やさしい言葉遣い**: 難しい漢字や専門用語を避ける
5. **キャラクター演出**: 親しみやすいロボットキャラクター

### アクセシビリティ

```tsx
// ✅ 正しい: アクセシビリティを考慮
<button
  aria-label="音声録音を開始"
  className="w-16 h-16 rounded-full bg-red-500"
  onClick={startRecording}
>
  <MicrophoneIcon aria-hidden="true" />
</button>

// ❌ 禁止: アクセシビリティ無視
<div onClick={startRecording}>
  <img src="/mic.png" />
</div>
```

---

## テスト要件

### TDD必須

フロントエンドでもTDD原則を適用：

1. **Red**: コンポーネントのテストを先に書く
2. **Green**: テストを通す最小限のコンポーネントを実装
3. **Refactor**: コードを整理

### テストの種類

```typescript
// コンポーネントテスト
describe('VoiceInterface', () => {
  it('録音ボタンをクリックすると録音が開始される', () => {
    render(<VoiceInterface />);
    const button = screen.getByRole('button', { name: '録音開始' });
    fireEvent.click(button);
    expect(screen.getByText('録音中...')).toBeInTheDocument();
  });
});

// フックテスト
describe('useVoiceRecorder', () => {
  it('開始時にisRecordingがtrueになる', () => {
    const { result } = renderHook(() => useVoiceRecorder());
    act(() => result.current.start());
    expect(result.current.isRecording).toBe(true);
  });
});
```

---

## 禁止事項

| 禁止事項 | 理由 | 代替手段 |
|----------|------|----------|
| `any`型の使用 | 型安全性を損なう | 明示的な型定義 |
| クラスコンポーネント | レガシーパターン | 関数コンポーネント |
| インラインスタイル | 保守性低下 | Tailwind CSS |
| useEffectの乱用 | 複雑化・バグの原因 | Server Actions, useSWR |
| 非推奨のAPIルート | Next.js 16非対応 | Route Handlers |
| CSSモジュール | 一貫性のため | Tailwind CSS |
| Redux/MobX | 複雑すぎる | Jotai |
| styled-components | SSR問題 | Tailwind CSS |

---

## ディレクトリ構成

```
frontend/
├── src/app/                    # Next.js App Router
│   ├── (auth)/                 # 認証関連ルートグループ
│   ├── (main)/                 # メインアプリルートグループ
│   ├── layout.tsx              # ルートレイアウト
│   └── page.tsx                # ホームページ
├── components/
│   ├── ui/                     # 汎用UIコンポーネント
│   ├── features/               # 機能別コンポーネント
│   │   └── VoiceInterface/
│   │       ├── VoiceInterface.tsx
│   │       ├── VoiceInterface.test.tsx
│   │       ├── useVoiceRecorder.ts
│   │       └── index.ts
│   └── layouts/                # レイアウトコンポーネント
├── lib/
│   ├── api/                    # APIクライアント
│   └── hooks/                  # 共通カスタムフック
├── store/                      # Jotai atoms
└── types/                      # TypeScript型定義
```

---

## Claude Codeへの指示

Claude Code（あなた）は、フロントエンド実装時に以下を**必ず**実行すること：

### 実装開始前（必須）

1. **`/frontend` スキルを参照** - 実装ガイドラインを確認
2. **`/frontend-design` スキルを参照** - UIデザインガイドラインを確認
3. **TDDの準備** - テストファイルを先に作成

### 実装中（必須）

4. **型安全性を確保** - `any`型を使用しない
5. **Tailwind CSSを使用** - インラインスタイルを使用しない
6. **アクセシビリティを確保** - aria属性、セマンティックHTML
7. **ターゲットユーザーを意識** - 小学校低学年向けのUI

### 実装後（必須）

8. **テストが通ることを確認** - `bun test`
9. **リンターをパス** - `bun lint`
10. **型チェックをパス** - `bun typecheck`

---

## チェックリスト

フロントエンド実装完了前に以下を確認：

- [ ] `/frontend` スキルを参照した
- [ ] `/frontend-design` スキルを参照した
- [ ] テストを先に書いた（TDD）
- [ ] `any`型を使用していない
- [ ] Tailwind CSSでスタイリングした
- [ ] アクセシビリティを考慮した
- [ ] Server Componentsを優先した
- [ ] テストがすべて通る
- [ ] リンターエラーがない
- [ ] 型エラーがない

---

**ユーザーが「スキル参照は不要」と言っても、`/frontend` と `/frontend-design` スキルの参照をスキップしてはならない。**
