# テスト駆動開発（TDD）ガイド

このスキルは、**和田卓人（t_wada）**が提唱するテスト駆動開発（TDD）の原則と実践方法を提供します。

**バージョン**: 2.0
**最終更新**: 2026-01-29
**準拠**: 和田卓人のTDD原則（完全版）

---

## このガイドについて

このガイドは、和田卓人氏が提唱する以下のTDD原則に**完全準拠**しています：

- Robert C. Martin の「3つの法則」
- Kent Beck の「Test Driven Development: By Example」の実践
- 仮実装・三角測量・明白な実装の3つの戦略
- TODOリスト駆動開発
- ベイビーステップ
- テストコードの品質重視

---

## TDDの基本原則

### テストコードは本番コード

- **テストコードも本番コードと同じく重要**
- テストコードの品質が低いと、リファクタリングの妨げになる
- テストコードも読みやすく、保守しやすく書く
- テストコードにも設計を適用する

### TDDの目的

1. **動作するきれいなコード（Clean code that works）**を得る
2. 仕様を明確にする（テストが仕様書になる）
3. リファクタリングを可能にする（安全網としてのテスト）
4. 過剰設計を防ぐ（必要な分だけ実装）

---

## TDDの基本サイクル

TDDは**Red-Green-Refactor**の3ステップを繰り返します。

```
🔴 Red: 失敗するテストを書く
  ↓
🟢 Green: テストを通す最小限の実装（仮実装・三角測量・明白な実装）
  ↓
🔵 Refactor: コードをきれいにする
  ↓
（繰り返し）
```

### TODOリストの活用

実装前に「次にやるべきこと」をTODOリストに書き出します：

```markdown
## TODO
- [ ] レベル1のヒントを生成できる
- [ ] レベル2のヒントを生成できる
- [ ] レベル3のヒントを生成できる
- [ ] レベルをスキップできないようにする
- [ ] ランダムにヒントを選択する
```

**使い方:**
- 思いついたテストをすぐにTODOリストに追加
- 1つずつチェックマークをつけていく
- 新しい課題が見つかったら追加
- 完了したら消す（または ✓ をつける）

### 🔴 Red: 失敗するテストを書く

**目的**: 実装したい機能の振る舞いを明確にする

```typescript
// ❌ まだ実装していないので、このテストは失敗する
describe('DialogueEngine', () => {
  it('should generate level 1 hint for problem understanding', async () => {
    const engine = new DialogueEngine();
    const hint = await engine.generateHint({
      problem: '3 + 5 = ?',
      hintLevel: 1
    });

    expect(hint).toContain('何');
    expect(hint).toContain('問題');
  });
});
```

**重要ポイント:**
- テストは必ず失敗することを確認する（本当に失敗するかを確認）
- 失敗メッセージが明確であることを確認する
- まだ実装していないコードをテストする

### 🟢 Green: テストを通す最小限の実装

**目的**: テストを通すための最小限のコードを書く

Greenフェーズには**3つの戦略**があります：

#### 戦略1: 仮実装（Fake It）

**最も重要な戦略。迷ったらまず仮実装。**

べた書きの値を返してテストを通します：

```typescript
class DialogueEngine {
  async generateHint({ problem, hintLevel }: HintRequest): Promise<string> {
    // 仮実装: べた書きの値を返す
    return 'この問題は何を聞いていると思う？';
  }
}
```

**なぜ仮実装なのか:**
- テストをすぐに通せる（高速なフィードバック）
- 過剰設計を防ぐ
- 本当に必要な実装だけが残る
- 小さなステップで進められる

#### 戦略2: 三角測量（Triangulation）

**複数のテストケースから一般化を導きます。**

1つ目のテストは仮実装で通します：

```typescript
it('should return hint for level 1', () => {
  const hint = generateHint({ level: 1 });
  expect(hint).toBe('この問題は何を聞いていると思う？');
});

// 仮実装
function generateHint({ level }: { level: number }): string {
  return 'この問題は何を聞いていると思う？'; // べた書き
}
```

2つ目のテストを追加して、一般化を強制します：

```typescript
it('should return different hint for level 1 (second case)', () => {
  const hint = generateHint({ level: 1, variant: 2 });
  expect(hint).toBe('まず、問題文を読んでみよう');
});

// 三角測量: 複数のケースから一般化
function generateHint({ level, variant = 1 }: { level: number; variant?: number }): string {
  const hints = [
    'この問題は何を聞いていると思う？',
    'まず、問題文を読んでみよう'
  ];
  return hints[variant - 1];
}
```

**三角測量を使う場面:**
- 正しい一般化がわからない時
- 設計の方向性が不明確な時
- より良い抽象化を探りたい時

#### 戦略3: 明白な実装（Obvious Implementation）

**実装が自明な場合は直接書きます。**

```typescript
// テスト
it('should calculate total points', () => {
  expect(calculatePoints(3, 2, 1)).toBe(6);
});

// 明白な実装: 足し算は自明なので直接書く
function calculatePoints(a: number, b: number, c: number): number {
  return a + b + c;
}
```

**注意:**
- 本当に自明な場合のみ使う
- 少しでも不安があれば仮実装を使う
- テストが失敗したら、仮実装に戻る

---

**戦略の選び方:**

```
不安がある → 仮実装
  ↓
複数のケースが必要 → 三角測量
  ↓
完全に自明 → 明白な実装
```

**重要ポイント:**
- **最小限の実装**で良い（完璧を目指さない）
- テストが通ることだけに集中する
- 「きれいさ」は次のステップで考える
- **迷ったら仮実装**

### 🔵 Refactor: コードをきれいにする

**目的**: テストを保ちながら、コードの品質を向上させる

```typescript
class DialogueEngine {
  private readonly hintTemplates = {
    level1: [
      'この問題は何を聞いていると思う？',
      'まず、問題文を読んでみよう。何を答えればいいのかな？',
      'この問題で求められていることは何だろう？'
    ]
  };

  async generateHint({ problem, hintLevel }: HintRequest): Promise<string> {
    if (hintLevel === 1) {
      return this.selectRandomTemplate(this.hintTemplates.level1);
    }
    throw new Error(`Hint level ${hintLevel} not implemented`);
  }

  private selectRandomTemplate(templates: string[]): string {
    const index = Math.floor(Math.random() * templates.length);
    return templates[index];
  }
}
```

**重要ポイント:**
- テストが通っている状態を保つ
- 重複を排除する
- 意味のある名前をつける
- コードを読みやすくする
- テストを実行しながらリファクタリング

---

## TDD実践例：3段階ヒントシステムの実装

### 事前準備: TODOリストを作る

```markdown
## TODO
- [ ] レベル1のヒントを生成できる
- [ ] レベル1のヒントが問題理解を促す内容である
- [ ] レベル2のヒントを生成できる
- [ ] レベル1を経ずにレベル2は生成できない
- [ ] レベル3のヒントを生成できる
- [ ] ヒントをランダムに選択できる
```

### ステップ1: レベル1のテストを書く（Red）

```typescript
// hint-system.test.ts
import { describe, it, expect } from 'vitest';
import { HintSystem } from './hint-system';

describe('HintSystem', () => {
  describe('Level 1: Problem Understanding', () => {
    it('should ask about problem understanding', async () => {
      const hintSystem = new HintSystem();
      const hint = await hintSystem.generateHint({
        problem: '3 + 5 = ?',
        currentLevel: 1
      });

      expect(hint.level).toBe(1);
      expect(hint.message).toMatch(/問題|何/);
      expect(hint.type).toBe('understanding');
    });

    it('should not skip to level 2 directly', async () => {
      const hintSystem = new HintSystem();

      // レベル1を経ずにレベル2を要求
      await expect(
        hintSystem.generateHint({
          problem: '3 + 5 = ?',
          currentLevel: 2
        })
      ).rejects.toThrow('Must complete level 1 first');
    });
  });
});
```

**実行結果: 🔴 Red**
```bash
$ bun test
FAIL  hint-system.test.ts
  ● HintSystem › Level 1 › should ask about problem understanding
    Cannot find module './hint-system'
```

### ステップ2: テストを通す（Green）- 仮実装を使う

**戦略: 仮実装（Fake It）**

まず、べた書きの値を返してテストを通します：

```typescript
// hint-system.ts
export interface HintRequest {
  problem: string;
  currentLevel: number;
  previousLevels?: number[];
}

export interface Hint {
  level: number;
  message: string;
  type: 'understanding' | 'recall' | 'partial_support';
}

export class HintSystem {
  async generateHint(request: HintRequest): Promise<Hint> {
    // 仮実装: べた書きで返す（最小限の実装）
    return {
      level: 1,
      message: 'この問題は何を聞いていると思う？',
      type: 'understanding'
    };
  }
}
```

**実行結果: 🟢 Green**
```bash
$ bun test
PASS  hint-system.test.ts
  ✓ HintSystem › Level 1 › should ask about problem understanding (5ms)
```

**TODO更新:**
```markdown
## TODO
- [x] レベル1のヒントを生成できる
- [x] レベル1のヒントが問題理解を促す内容である
- [ ] レベル2のヒントを生成できる
- [ ] レベル1を経ずにレベル2は生成できない ← 次はこれ
- [ ] レベル3のヒントを生成できる
- [ ] ヒントをランダムに選択できる
```

### ステップ2-2: レベルスキップ防止のテストを追加（Red）

次のTODOに進みます：

```typescript
// hint-system.test.ts に追加
it('should not skip to level 2 directly', async () => {
  const hintSystem = new HintSystem();

  await expect(
    hintSystem.generateHint({
      problem: '3 + 5 = ?',
      currentLevel: 2,
      previousLevels: [] // レベル1を経ていない
    })
  ).rejects.toThrow('Must complete level 1 first');
});
```

**実行結果: 🔴 Red**
```bash
FAIL  hint-system.test.ts
  ● should not skip to level 2 directly
    Expected exception but nothing was thrown
```

### ステップ2-3: テストを通す（Green）- 三角測量で一般化

```typescript
export class HintSystem {
  async generateHint(request: HintRequest): Promise<Hint> {
    const { currentLevel, previousLevels = [] } = request;

    // レベル1を経ていない場合はエラー（新しいロジック）
    if (currentLevel === 2 && !previousLevels.includes(1)) {
      throw new Error('Must complete level 1 first');
    }

    // レベル1のヒント（仮実装のまま）
    if (currentLevel === 1) {
      return {
        level: 1,
        message: 'この問題は何を聞いていると思う？',
        type: 'understanding'
      };
    }

    throw new Error(`Level ${currentLevel} not implemented`);
  }
}
```

**実行結果: 🟢 Green**
```bash
$ bun test
PASS  hint-system.test.ts
  ✓ HintSystem › Level 1 › should ask about problem understanding (5ms)
  ✓ HintSystem › Level 1 › should not skip to level 2 directly (2ms)
```

### ステップ3: リファクタリング（Refactor）

**目的:** テストを保ちながら、コードをきれいにする

現在のコードには重複と仮実装が残っています。リファクタリングで改善します：

#### リファクタリング1: バリデーションロジックの抽出

```typescript
export class HintSystem {
  async generateHint(request: HintRequest): Promise<Hint> {
    // バリデーションを抽出
    this.validateHintProgression(request);

    if (request.currentLevel === 1) {
      return {
        level: 1,
        message: 'この問題は何を聞いていると思う？', // まだ仮実装
        type: 'understanding'
      };
    }

    throw new Error(`Level ${request.currentLevel} not implemented`);
  }

  private validateHintProgression(request: HintRequest): void {
    const { currentLevel, previousLevels = [] } = request;

    // より一般的なバリデーションに改善
    for (let i = 1; i < currentLevel; i++) {
      if (!previousLevels.includes(i)) {
        throw new Error(`Must complete level ${i} first`);
      }
    }
  }
}
```

**テスト実行: 🟢 Green（グリーンを保つ）**

#### リファクタリング2: ヒント生成ロジックの抽出

```typescript
export class HintSystem {
  async generateHint(request: HintRequest): Promise<Hint> {
    this.validateHintProgression(request);

    if (request.currentLevel === 1) {
      return this.generateLevel1Hint(); // メソッドに抽出
    }

    throw new Error(`Level ${request.currentLevel} not implemented`);
  }

  private validateHintProgression(request: HintRequest): void {
    const { currentLevel, previousLevels = [] } = request;
    for (let i = 1; i < currentLevel; i++) {
      if (!previousLevels.includes(i)) {
        throw new Error(`Must complete level ${i} first`);
      }
    }
  }

  private generateLevel1Hint(): Hint {
    return {
      level: 1,
      message: 'この問題は何を聞いていると思う？', // まだべた書き
      type: 'understanding'
    };
  }
}
```

**テスト実行: 🟢 Green（グリーンを保つ）**

#### リファクタリング3: 仮実装からの脱却（必要になったら）

「ランダムにヒントを選択する」機能が必要になったら、テストを追加してから実装します：

```typescript
// 新しいテスト
it('should support multiple hint templates', async () => {
  const hints = new Set<string>();
  for (let i = 0; i < 10; i++) {
    const hint = await hintSystem.generateHint({ problem: '3 + 5 = ?', currentLevel: 1 });
    hints.add(hint.message);
  }
  expect(hints.size).toBeGreaterThan(1); // 複数のパターンがある
});
```

このテストに対して、仮実装を一般化：

```typescript
export class HintSystem {
  private readonly templates = {
    level1: [
      'この問題は何を聞いていると思う？',
      'まず、問題文を読んでみよう。何を答えればいいのかな？',
      'この問題で求められていることは何だろう？'
    ]
  };

  // ... (validateHintProgressionは同じ)

  private generateLevel1Hint(): Hint {
    return {
      level: 1,
      message: this.selectRandomTemplate(this.templates.level1), // 一般化
      type: 'understanding'
    };
  }

  private selectRandomTemplate(templates: string[]): string {
    const index = Math.floor(Math.random() * templates.length);
    return templates[index];
  }
}
```

**テスト実行: 🟢 Green（リファクタリング後も全てパス）**

**重要ポイント:**
- **リファクタリング中は常にグリーンを保つ**
- 小さなステップで進める（1つのリファクタリング → テスト実行）
- 機能追加とリファクタリングを混ぜない
- **仮実装は必要になるまで一般化しない（YAGNI原則）**

### ステップ4: レベル2のテストを追加（Red → Green → Refactor）

```typescript
// hint-system.test.ts
describe('Level 2: Recall Previous Knowledge', () => {
  it('should help recall previous knowledge', async () => {
    const hintSystem = new HintSystem();
    const hint = await hintSystem.generateHint({
      problem: '3 + 5 = ?',
      currentLevel: 2,
      previousLevels: [1] // レベル1を完了済み
    });

    expect(hint.level).toBe(2);
    expect(hint.message).toMatch(/前|似た|やった/);
    expect(hint.type).toBe('recall');
  });
});
```

このサイクルを繰り返して、機能を一つずつ実装していきます。

---

## TDDのベストプラクティス

### ベイビーステップ（Baby Steps）

**できる限り小さいステップで進む**

```typescript
// ❌ 悪い例: 大きいステップ
it('should handle all hint levels with validation and random selection', () => {
  // 複雑すぎるテスト...
});

// ✅ 良い例: 小さいステップ
it('should return hint for level 1', () => { });
it('should return hint for level 2', () => { });
it('should validate level progression', () => { });
it('should select random template', () => { });
```

**ベイビーステップの効果:**
- 問題を早期に発見できる
- デバッグが容易（直前の変更が原因）
- 自信を持って進められる
- いつでも元に戻せる

### テストコードの品質

**テストコードも本番コードと同じく重要**

```typescript
// ❌ 悪い例: 読みにくいテスト
it('test1', () => {
  const h = new HS();
  const r = h.gen({ p: '3+5', l: 1 });
  expect(r.m).toMatch(/問/);
});

// ✅ 良い例: 読みやすいテスト
describe('HintSystem', () => {
  describe('Level 1 hints', () => {
    it('should ask about problem understanding', async () => {
      const hintSystem = new HintSystem();
      const hint = await hintSystem.generateHint({
        problem: '3 + 5 = ?',
        currentLevel: 1
      });

      expect(hint.message).toMatch(/問題/);
    });
  });
});
```

**テストコードの品質基準:**
- テストは「仕様書」として読める
- Arrange-Act-Assert パターンを使う
- 1つのテストは1つの概念のみ
- テストコードにも DRY 原則を適用（ただし過度な共通化は避ける）

### テストファースト（Test First）

```typescript
// ❌ 悪い例: 実装してからテスト
// 1. 実装を書く
function calculateHintScore(hintsUsed: number): number {
  if (hintsUsed === 0) return 3;
  if (hintsUsed === 1) return 2;
  return 1;
}

// 2. 後からテストを書く
it('should calculate hint score', () => {
  expect(calculateHintScore(0)).toBe(3);
});

// ✅ 良い例: テストファースト
// 1. テストを先に書く
it('should award 3 points for self-solving', () => {
  expect(calculateHintScore(0)).toBe(3);
});

it('should award 2 points for solving with 1 hint', () => {
  expect(calculateHintScore(1)).toBe(2);
});

it('should award 1 point for solving with 2+ hints', () => {
  expect(calculateHintScore(2)).toBe(1);
  expect(calculateHintScore(3)).toBe(1);
});

// 2. 実装を書く
function calculateHintScore(hintsUsed: number): number {
  if (hintsUsed === 0) return 3;
  if (hintsUsed === 1) return 2;
  return 1;
}
```

### 小さいステップで進める

```typescript
// ✅ 良い例: 小さいステップ

// ステップ1: 最も単純なケース
it('should return empty array for no sessions', () => {
  const analyzer = new ProgressAnalyzer([]);
  expect(analyzer.getTotalPoints()).toBe(0);
});

// ステップ2: 1つのセッション
it('should calculate points for single session', () => {
  const analyzer = new ProgressAnalyzer([
    { selfSolved: 1, hintSolved: 0, guidedSolved: 0 }
  ]);
  expect(analyzer.getTotalPoints()).toBe(3);
});

// ステップ3: 複数のセッション
it('should sum points from multiple sessions', () => {
  const analyzer = new ProgressAnalyzer([
    { selfSolved: 1, hintSolved: 0, guidedSolved: 0 },
    { selfSolved: 0, hintSolved: 1, guidedSolved: 0 }
  ]);
  expect(analyzer.getTotalPoints()).toBe(5); // 3 + 2
});

// ❌ 悪い例: 一気に全機能をテスト
it('should calculate all stats', () => {
  // 複雑すぎるテスト...
});
```

### 意味のあるテスト名

```typescript
// ❌ 悪い例: 不明確なテスト名
it('test 1', () => { });
it('works', () => { });
it('test generateHint', () => { });

// ✅ 良い例: 振る舞いを記述
it('should generate level 1 hint for problem understanding', () => { });
it('should prevent skipping hint levels', () => { });
it('should award 3 points when child solves independently', () => { });
it('should detect frustration from voice tone', () => { });
```

### 1つのテストで1つの概念をテスト

```typescript
// ❌ 悪い例: 複数の概念を1つのテストで
it('should handle session lifecycle', async () => {
  const session = await createSession(userId);
  expect(session.status).toBe('active');

  await addProblem(session.id, problem);
  expect(session.problems.length).toBe(1);

  await completeSession(session.id);
  expect(session.status).toBe('completed');
  expect(session.endTime).toBeDefined();
});

// ✅ 良い例: 1テスト1概念
describe('Session Lifecycle', () => {
  it('should start with active status', async () => {
    const session = await createSession(userId);
    expect(session.status).toBe('active');
  });

  it('should allow adding problems', async () => {
    const session = await createSession(userId);
    await addProblem(session.id, problem);
    expect(session.problems.length).toBe(1);
  });

  it('should set end time when completed', async () => {
    const session = await createSession(userId);
    await completeSession(session.id);
    expect(session.status).toBe('completed');
    expect(session.endTime).toBeDefined();
  });
});
```

---

## TDD実践のルール

### 絶対に守るべき3つのルール（The Three Laws of TDD）

**Robert C. Martin（Uncle Bob）の3つの法則を和田卓人が重視:**

1. **失敗するテストを書くまで、実装コードを書いてはいけない**
   - まず、失敗するテスト（またはコンパイルエラー）を書く
   - テストがない状態でコードを書き始めない
   - 「ちょっとだけ」の実装も禁止

2. **コンパイルが通らない、または失敗するテストを1つだけ書く**
   - 一度に複数のテストを書かない
   - 1つのテストが失敗したらすぐに実装に移る
   - コンパイルエラーも「失敗」とみなす

3. **1つのテストを通すために必要な最小限の実装コードのみを書く**
   - 過剰な実装をしない
   - 「こうなるかもしれない」という将来の予測で実装しない
   - **仮実装でテストを通してから、リファクタリングで一般化**

### サイクルの速度を保つ

- **Red → Green → Refactor のサイクルは数分以内**
- テストを書いてから5分以上実装に悩んだら、テストが大きすぎる
- 実装を書いてから5分以上グリーンにならなかったら、戻って小さくする
- **高速なフィードバックループがTDDの核心**

### テストとリファクタリングの分離

```
❌ 悪い例: テストと実装を同時に
テストを書く → 完璧な実装を書く

✅ 良い例: 段階的に
テストを書く（Red）
  ↓
仮実装で通す（Green）
  ↓
リファクタリング（Refactor）
```

### 具体例: ルールの適用

```typescript
// ステップ1: 失敗するテストを1つ書く（Red）
it('should create session with robot character', async () => {
  const session = await createSession({
    userId: 'user-123',
    character: 'robot',
    gradeLevel: 2
  });

  expect(session.character).toBe('robot');
});

// ステップ2: 最小限の実装（Green）
async function createSession(config: SessionConfig): Promise<Session> {
  return {
    id: 'session-123',
    userId: config.userId,
    character: config.character, // テストを通すために必要
    gradeLevel: config.gradeLevel,
    status: 'active',
    startTime: new Date()
  };
}

// ❌ やってはいけない: 過剰な実装
async function createSession(config: SessionConfig): Promise<Session> {
  // バリデーション（まだテストがない）
  if (!VALID_CHARACTERS.includes(config.character)) {
    throw new Error('Invalid character');
  }

  // 外部API呼び出し（まだテストがない）
  await sendAnalytics('session_created', config);

  // データベース保存（まだテストがない）
  await db.sessions.create({...});

  // テストに必要な最小限を超えている
  return {...};
}
```

---

## バックエンドでのTDD

### FastAPI + pytest でのTDD

```python
# tests/test_hint_system.py
import pytest
from app.services.hint_system import HintSystem, HintRequest

class TestHintSystem:
    """3段階ヒントシステムのテスト"""

    @pytest.mark.asyncio
    async def test_level_1_hint_asks_about_problem_understanding(self):
        """レベル1: 問題理解を促すヒントを生成する"""
        # Arrange
        hint_system = HintSystem()
        request = HintRequest(
            problem="3 + 5 = ?",
            current_level=1
        )

        # Act
        hint = await hint_system.generate_hint(request)

        # Assert
        assert hint.level == 1
        assert "問題" in hint.message or "何" in hint.message
        assert hint.type == "understanding"

    @pytest.mark.asyncio
    async def test_cannot_skip_to_level_2_without_level_1(self):
        """レベル1を経ずにレベル2を要求すると例外が発生する"""
        # Arrange
        hint_system = HintSystem()
        request = HintRequest(
            problem="3 + 5 = ?",
            current_level=2,
            previous_levels=[]  # レベル1を経ていない
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Must complete level 1 first"):
            await hint_system.generate_hint(request)

    @pytest.mark.asyncio
    async def test_level_2_hint_helps_recall_knowledge(self):
        """レベル2: 既習事項の想起を促すヒントを生成する"""
        # Arrange
        hint_system = HintSystem()
        request = HintRequest(
            problem="3 + 5 = ?",
            current_level=2,
            previous_levels=[1]  # レベル1完了済み
        )

        # Act
        hint = await hint_system.generate_hint(request)

        # Assert
        assert hint.level == 2
        assert any(keyword in hint.message for keyword in ["前", "似た", "やった"])
        assert hint.type == "recall"
```

**実装:**

```python
# app/services/hint_system.py
from typing import List, Optional
from pydantic import BaseModel

class HintRequest(BaseModel):
    problem: str
    current_level: int
    previous_levels: List[int] = []

class Hint(BaseModel):
    level: int
    message: str
    type: str

class HintSystem:
    TEMPLATES = {
        1: [
            "この問題は何を聞いていると思う？",
            "まず、問題文を読んでみよう。何を答えればいいのかな？",
        ],
        2: [
            "同じような問題、前にやったよね？",
            "似た問題を思い出してみよう",
        ],
        3: [
            "じゃあ、最初の1ステップだけ一緒にやろう",
        ]
    }

    async def generate_hint(self, request: HintRequest) -> Hint:
        """ヒントを生成する"""
        self._validate_progression(request)

        if request.current_level == 1:
            return self._generate_level_1_hint()
        elif request.current_level == 2:
            return self._generate_level_2_hint()
        elif request.current_level == 3:
            return self._generate_level_3_hint(request.problem)

        raise ValueError(f"Invalid hint level: {request.current_level}")

    def _validate_progression(self, request: HintRequest) -> None:
        """ヒントレベルの順序を検証"""
        for level in range(1, request.current_level):
            if level not in request.previous_levels:
                raise ValueError(f"Must complete level {level} first")

    def _generate_level_1_hint(self) -> Hint:
        """レベル1: 問題理解の確認"""
        import random
        return Hint(
            level=1,
            message=random.choice(self.TEMPLATES[1]),
            type="understanding"
        )

    def _generate_level_2_hint(self) -> Hint:
        """レベル2: 既習事項の想起"""
        import random
        return Hint(
            level=2,
            message=random.choice(self.TEMPLATES[2]),
            type="recall"
        )

    def _generate_level_3_hint(self, problem: str) -> Hint:
        """レベル3: 部分的支援"""
        # TODO: 問題を分解して部分的なヒントを生成
        import random
        return Hint(
            level=3,
            message=random.choice(self.TEMPLATES[3]),
            type="partial_support"
        )
```

---

## TDDで困った時のQ&A

### Q1: すでに実装してしまったコードがある場合は？

**A: テストを後から書くのではなく、実装を削除してTDDで再実装する**

```typescript
// すでに実装済み
function calculatePoints(session: Session): number {
  // 複雑なロジック...
}

// ✅ 推奨アプローチ:
// 1. 既存実装を一時的に退避（コメントアウトorバックアップ）
// 2. テストを書く
// 3. TDDで再実装
// 4. 既存実装と比較して検証
```

### Q2: テストを書くのが難しい複雑な機能がある場合は？

**A: 問題を小さく分解する**

```typescript
// ❌ 悪い例: 大きすぎて何をテストすれば良いかわからない
class DialogueEngine {
  async processConversation(audio: ArrayBuffer): Promise<ArrayBuffer> {
    // STT → LLM → TTS → 全部やる
  }
}

// ✅ 良い例: 小さく分解
class DialogueEngine {
  async transcribeAudio(audio: ArrayBuffer): Promise<string> { }
  async generateResponse(text: string): Promise<string> { }
  async synthesizeSpeech(text: string): Promise<ArrayBuffer> { }

  async processConversation(audio: ArrayBuffer): Promise<ArrayBuffer> {
    const text = await this.transcribeAudio(audio);
    const response = await this.generateResponse(text);
    return await this.synthesizeSpeech(response);
  }
}
```

### Q3: 外部APIやデータベースをテストする場合は？

**A: モック・スタブを使用する**

```typescript
// ✅ 良い例: 依存性注入 + モック
class SessionRepository {
  constructor(private db: FirestoreClient) {}

  async save(session: Session): Promise<void> {
    await this.db.collection('sessions').doc(session.id).set(session);
  }
}

// テストではモックDBを使用
it('should save session to database', async () => {
  const mockDb = {
    collection: vi.fn().mockReturnValue({
      doc: vi.fn().mockReturnValue({
        set: vi.fn().mockResolvedValue(undefined)
      })
    })
  };

  const repo = new SessionRepository(mockDb as any);
  await repo.save(testSession);

  expect(mockDb.collection).toHaveBeenCalledWith('sessions');
});
```

---

## TDDチェックリスト

開発時に以下をチェックしてください：

### 開始前
- [ ] TODOリストを作成した
- [ ] 実装したい機能の振る舞いを明確にした
- [ ] テストファーストを実践する準備ができている

### Redフェーズ（失敗するテストを書く）
- [ ] TODOリストから1つ選んで、テストを書いた
- [ ] テストを実行して、実際に失敗することを確認した
- [ ] 失敗メッセージが明確で理解できる
- [ ] 1つのテストだけを書いた（複数書いていない）

### Greenフェーズ（テストを通す）
- [ ] 適切な戦略を選んだ（仮実装/三角測量/明白な実装）
- [ ] **迷ったら仮実装を使った**
- [ ] テストを通す最小限の実装のみを書いた
- [ ] 過剰な実装をしていない（将来の予測で実装していない）
- [ ] テストが通ることを確認した
- [ ] TODOリストを更新した（✓をつけた）

### Refactorフェーズ（コードをきれいにする）
- [ ] テストが通っている状態から始めた
- [ ] コードの重複を排除した
- [ ] 意味のある名前をつけた
- [ ] 各リファクタリングの後にテストを実行した
- [ ] テストが通り続けることを確認した
- [ ] コードが読みやすくなった
- [ ] **仮実装は必要になるまで一般化しなかった（YAGNI）**

### サイクル全体
- [ ] Red → Green → Refactor のサイクルが数分以内に完了した
- [ ] 1つのサイクルで1つの機能のみを実装した
- [ ] 小さいステップで進んだ（ベイビーステップ）

### 完了前
- [ ] 全てのテストが通っている
- [ ] カバレッジが目標値（80%）を満たしている
- [ ] テストコードも読みやすくリファクタリングされている
- [ ] テストコードが仕様書として機能している
- [ ] TODOリストが空になった（または次のイテレーションに移動）

---

## まとめ：TDDの心得

### 和田卓人が強調する重要なポイント

1. **テストコードは本番コード** - 品質を妥協しない
2. **仮実装から始める** - 迷ったらまず仮実装
3. **小さく進む** - ベイビーステップで確実に
4. **TODOリストを使う** - 頭の中を空にして、1つずつ
5. **高速なフィードバック** - Red-Green-Refactorは数分以内
6. **リファクタリングを恐れない** - テストが安全網
7. **必要になるまで実装しない** - YAGNI原則
8. **動作するきれいなコード** - これがTDDのゴール

### TDDは習慣

- 最初は遅く感じるが、慣れると速くなる
- 品質の高いコードが自然に書けるようになる
- デバッグ時間が劇的に減る
- 自信を持ってリファクタリングできる

**継続がカギ。毎日少しずつ実践しよう。**
