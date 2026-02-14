# Design - InputModeSelectorのUI統合

## アーキテクチャ概要

SessionContentに入力モード選択機能を追加します。

```
┌─────────────────────────────────────────┐
│         SessionContent                  │
│                                         │
│  ┌────────────────────────────────────┐ │
│  │  inputModeAtom: "voice" | "image"  │ │ (Jotai state)
│  │  | null (未選択)                    │ │
│  └────────────────────────────────────┘ │
│                                         │
│  If inputMode === null:                 │
│  ┌────────────────────────────────────┐ │
│  │   InputModeSelector                │ │
│  │   - onModeSelect(mode)             │ │
│  │     → setInputMode(mode)           │ │
│  └────────────────────────────────────┘ │
│                                         │
│  If inputMode === "voice":              │
│  ┌────────────────────────────────────┐ │
│  │   VoiceInterface                   │ │
│  │   - 録音開始・停止                   │ │
│  │   - 音声レベル表示                   │ │
│  └────────────────────────────────────┘ │
│                                         │
│  If inputMode === "image":              │
│  ┌────────────────────────────────────┐ │
│  │   (プレースホルダー)                  │ │
│  │   「画像モードは準備中です」          │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## 技術選定

### 状態管理

**Jotai atom を使用**

```typescript
// store/atoms/session.ts に追加
export const inputModeAtom = atom<"voice" | "image" | null>(null)
```

**理由：**
- 既存の状態管理パターンと一貫性
- テストでのストア分離が容易
- シンプルな状態（単一値）

### コンポーネント構成

**SessionContent内で条件分岐**

```typescript
const [inputMode, setInputMode] = useAtom(inputModeAtom)

if (inputMode === null) {
  return <InputModeSelector onModeSelect={setInputMode} />
}

if (inputMode === "voice") {
  return (
    <>
      <VoiceInterface ... />
      {/* 既存のUI要素 */}
    </>
  )
}

if (inputMode === "image") {
  return <div>画像モードは準備中です</div>
}
```

## データ設計

### 新規Jotai Atom

```typescript
// frontend/store/atoms/session.ts
export const inputModeAtom = atom<"voice" | "image" | null>(null)
```

**初期値：** `null`（未選択状態）

**更新タイミング：** InputModeSelectorのonModeSelectコールバック

**リセットタイミング：** セッション終了時（将来実装）

## ファイル構成

### 変更ファイル

1. **frontend/store/atoms/session.ts**（新規作成または既存に追加）
   - `inputModeAtom`の定義

2. **frontend/src/app/session/SessionContent.tsx**
   - InputModeSelectorのimport
   - inputModeAtomの使用
   - 条件分岐ロジックの追加

3. **frontend/src/app/session/SessionContent.test.tsx**
   - 新規テストケース追加
   - モード選択テスト
   - 条件分岐テスト

### 新規ファイル

なし（既存コンポーネントを使用）

## 依存関係

### 既存コンポーネント

- `InputModeSelector`（PR #159で実装済み）
- `VoiceInterface`（既存）
- `CharacterDisplay`（既存）

### Jotai Atoms

- `inputModeAtom`（新規）
- 既存atoms（`dialogueTurnsAtom`, `characterStateAtom`など）

## エラーハンドリング

### 想定エラー

1. **モード選択後の状態不整合**
   - 対策：モード選択時に明示的にsetStateを実行
   - テストで状態遷移を検証

2. **音声モード選択後のWebSocket接続失敗**
   - 対策：既存のエラーハンドリングをそのまま使用
   - 新規エラーハンドリングは追加しない

## セキュリティ考慮事項

- ユーザー入力は限定（"voice" | "image"のみ）
- XSS対策：Reactのデフォルトエスケープに依存
- 特別な対策は不要

## パフォーマンス考慮事項

### レンダリング最適化

- InputModeSelectorは選択後アンマウント（再レンダリング不要）
- VoiceInterfaceは既存のメモ化を維持
- 新規パフォーマンス問題は発生しない想定

### 状態更新

- inputModeAtomの更新は1回のみ（選択時）
- 頻繁な更新なし

## 代替案と採用理由

### 代替案1：useState使用

```typescript
const [inputMode, setInputMode] = useState<"voice" | "image" | null>(null)
```

**不採用理由：**
- 既存の状態管理パターンと不整合
- テストでのモック化が複雑

### 代替案2：URL パラメータでモード管理

```typescript
const searchParams = useSearchParams()
const inputMode = searchParams.get('mode')
```

**不採用理由：**
- 過剰設計（URLにモードを保持する必要性なし）
- ユーザー体験の複雑化

### 採用案：Jotai atom

**採用理由：**
- 既存パターンと一貫性
- テスト容易性
- シンプルな実装
