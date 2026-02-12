# Design - セッションUI改善とバグ修正

## アーキテクチャ概要

6つのバグを個別に修正し、それぞれに対応するテストを作成する。フロントエンドのみで完結する修正であり、既存のJotai atoms構造と状態管理フローを活用する。

## 技術選定

- **状態管理**: Jotai（既存）
- **ルーティング**: Next.js App Router（既存）
- **テストフレームワーク**: Vitest + Testing Library（既存）
- **型チェック**: TypeScript strictモード（既存）

## データ設計

### #115: 対話履歴リセット

**修正対象atoms**:
- `dialogueHistoryAtom` - 対話履歴配列
- その他セッション関連atoms（必要に応じて）

**リセットタイミング**:
- セッションページアンマウント時（`useEffect` cleanup）
- または新規セッション開始時（useSessionフック内）

### #116: まほうつかいキャラクター画像

**画像パス**:
```
public/
├── robot.png (既存)
├── wizard.png (要確認・追加)
├── astronaut.png (要確認)
└── animal.png (要確認)
```

**CharacterDisplayコンポーネント修正**:
- `character` propに基づいた画像パス解決
- フォールバック画像の設定

### #117: ストーリー説明文

**キャラクター名マッピング**:
```typescript
const CHARACTER_NAMES: Record<Character, string> = {
  robot: 'ロボ',
  wizard: 'まほうつかい',
  astronaut: 'うちゅうひこうし',
  animal: 'どうぶつ',
};
```

**修正対象コンポーネント**:
- ストーリー進行状況セクション（SessionContent内）

### #118: 音声録音ボタン状態

**問題箇所**:
- WebSocket接続のクリーンアップ
- マイクアクセス状態の初期化

**修正アプローチ**:
- `useVoiceStream` または `useWebSocket` フック内の `useEffect` cleanup
- コンポーネントアンマウント時に接続を確実に切断

### #119: 404ページ

**新規ファイル**:
- `src/app/not-found.tsx`

**デザイン**:
```tsx
<div className="text-center">
  <h1 className="text-9xl font-bold">404</h1>
  <p className="text-2xl">このページは みつからないよ</p>
  <Link href="/">トップページにもどる</Link>
</div>
```

### #120: characterパラメータバリデーション

**バリデーション箇所**:
- `src/app/session/page.tsx` (Server Component)

**バリデーションロジック**:
```typescript
const validCharacters = ['robot', 'wizard', 'astronaut', 'animal'] as const;
const character = searchParams.character;

if (!character || !validCharacters.includes(character)) {
  redirect('/');
}
```

## ファイル構成

### 修正対象ファイル

```
src/
├── app/
│   ├── not-found.tsx (新規作成 #119)
│   └── session/
│       └── page.tsx (修正 #120)
├── components/features/
│   ├── CharacterDisplay/ (修正 #116)
│   └── SessionContent/ (修正 #115, #117)
└── lib/hooks/
    └── useVoiceStream.ts (修正 #118)
```

### テストファイル

```
tests/
├── app/
│   └── not-found.test.tsx (新規 #119)
└── pages/
    └── Session.test.tsx (修正 #115, #116, #117, #118, #120)
```

## 依存関係

- Jotai: 状態リセット処理で使用
- Next.js: ルーティングとリダイレクト
- Framer Motion: キャラクター表示アニメーション（既存）

## エラーハンドリング

### #120: 不正なcharacterパラメータ

- サーバーサイドでバリデーション → リダイレクト
- クライアントサイドでフォールバック表示なし（サーバーで弾く）

### #116: 画像読み込み失敗

- `<Image>` コンポーネントの `onError` ハンドラでフォールバック
- または、画像なしでもレイアウトが崩れないようCSSで対応

## セキュリティ考慮事項

- characterパラメータのXSS対策（Next.jsが自動エスケープ）
- 画像パスのディレクトリトラバーサル対策（ホワイトリスト方式）

## パフォーマンス考慮事項

- 画像の最適化（Next.js `<Image>` コンポーネント使用）
- atomsリセット処理の軽量化（必要最小限のatomsのみ）

## 代替案と採用理由

### #115: 対話履歴リセット方法

**案1: コンポーネントアンマウント時にリセット**
- 採用理由: セッション終了時に確実にクリア、次回セッションに影響しない

**案2: セッション開始時に初期化**
- 不採用: 一瞬前の履歴が見える可能性

### #120: 不正なcharacterパラメータ対応

**案1: トップページにリダイレクト**
- 採用理由: 不正な状態でセッション開始させない、明確な導線

**案2: デフォルト（robot）にフォールバック**
- 不採用: ユーザーが意図しないキャラクターでセッション開始

## 実装順序

1. #120: characterバリデーション（先にゲートを作る）
2. #119: 404ページ（独立した機能）
3. #115: 対話履歴リセット（セッション基盤）
4. #116: まほうつかい画像表示
5. #117: ストーリー説明文連動
6. #118: 音声録音ボタン状態修正
