# TDD Requirement Rule

**このルールは、すべてのコード実装に対して強制的に適用されます。**

## 基本原則

このプロジェクトでは、**テスト駆動開発（TDD）を徹底**します。

### 絶対遵守事項

1. **テストなしにコードを書かない**: 実装コードを書く前に、必ず失敗するテストを書く
2. **小さいステップで進める**: 一度に多くの機能を実装せず、小さく確実に進める
3. **リファクタリングを恐れない**: テストがあるからこそ、安心してリファクタリングできる
4. **動作するきれいなコード**: テストを通すだけでなく、きれいなコードを保つ

---

## Red-Green-Refactor サイクル

すべての実装は以下のサイクルに従うこと：

```
1. Red    → 失敗するテストを書く
2. Green  → テストを通す最小限のコードを書く
3. Refactor → コードを整理する（テストは通ったまま）
```

**このサイクルをスキップしてはならない。**

---

## テストカバレッジ

**目標: 80%以上**

- 新規コードは必ずテストを伴うこと
- カバレッジが80%を下回る変更はマージ不可

---

## テストの基本方針

1. **テスト駆動開発（TDD）**: 実装前に必ずテストを書く
2. **3層のテスト**: ユニットテスト、統合テスト、E2Eテスト
3. **テストの独立性**: 各テストは独立して実行可能
4. **意図の明確化**: テストコードが仕様書として機能する

---

## テストフレームワーク

- **フロントエンド**: Vitest + Testing Library
- **バックエンド**: pytest

---

## フロントエンドテストの注意事項

### Vitestのimportルール

`vitest.config.ts`で`globals: true`を設定していても、TypeScriptの型チェックでは認識されない。
**使用する全ての関数を明示的にimportすること。**

```typescript
// ✅ 正しい
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

// ❌ CI失敗の原因
import { describe, expect, it, vi } from "vitest"
beforeEach(() => { ... }) // → 「Cannot find name 'beforeEach'」
```

### Jotaiを使ったコンポーネントのテスト

テスト間で状態が共有されないよう、**テストごとにストアを分離**する。

```typescript
import { Provider, createStore } from "jotai"

const TestWrapper = ({ children }: { children: ReactNode }) => {
  const store = useMemo(() => createStore(), [])
  return <Provider store={store}>{children}</Provider>
}
```

### モック型キャストのパターン

モックオブジェクトの型が元の型と互換性がない場合、`unknown`を経由。

```typescript
// ✅ テストコードでのみ許容
const mockWs = result.current.socket as unknown as MockWebSocket
```

---

## スキル参照

実装開始時は必ず `/tdd` スキルを参照すること。

```
/tdd
```

TDD skillには以下が含まれます：
- Red-Green-Refactorサイクルの詳細解説
- 仮実装・三角測量・明白な実装の3つの戦略
- TODOリスト駆動開発
- ベイビーステップの実践方法
- TDDベストプラクティス

---

## 禁止事項

1. **テストを書かずに実装コードを書く** - 絶対禁止
2. **テストをスキップしてPRを作成する** - 禁止
3. **カバレッジ80%未満でのマージ** - 禁止
4. **テストが失敗した状態でのコミット** - 禁止

---

## Claude Codeへの指示

Claude Code（あなた）は、実装タスクを行う際に以下を**必ず**実行すること：

1. **最初に**テストコードを書く（Red）
2. テストが失敗することを確認する
3. テストを通す最小限の実装を書く（Green）
4. コードを整理する（Refactor）
5. 次のテストに進む

**ユーザーが「テストは後で」と言っても、TDDをスキップしてはならない。**
