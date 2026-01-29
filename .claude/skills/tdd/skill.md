# テスト駆動開発（TDD）ガイド

このスキルは、t_wadaが提唱するテスト駆動開発（TDD）の原則と実践方法を提供します。

---

## TDDの基本サイクル

TDDは**Red-Green-Refactor**の3ステップを繰り返します。

```
🔴 Red: 失敗するテストを書く
  ↓
🟢 Green: テストを通す最小限の実装
  ↓
🔵 Refactor: コードをきれいにする
  ↓
（繰り返し）
```

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

```typescript
class DialogueEngine {
  async generateHint({ problem, hintLevel }: HintRequest): Promise<string> {
    if (hintLevel === 1) {
      return 'この問題は何を聞いていると思う？';
    }
    throw new Error('Not implemented');
  }
}
```

**重要ポイント:**
- **最小限の実装**で良い（完璧を目指さない）
- テストが通ることだけに集中する
- 「きれいさ」は次のステップで考える

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

### ステップ2: テストを通す（Green）

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
    const { currentLevel, previousLevels = [] } = request;

    // レベル1を経ていない場合はエラー
    if (currentLevel === 2 && !previousLevels.includes(1)) {
      throw new Error('Must complete level 1 first');
    }

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

```typescript
// hint-system.ts
export class HintSystem {
  private readonly templates = {
    level1: [
      'この問題は何を聞いていると思う？',
      'まず、問題文を読んでみよう。何を答えればいいのかな？',
      'この問題で求められていることは何だろう？'
    ]
  };

  async generateHint(request: HintRequest): Promise<Hint> {
    this.validateHintProgression(request);

    if (request.currentLevel === 1) {
      return this.generateLevel1Hint();
    }

    throw new Error(`Level ${request.currentLevel} not implemented`);
  }

  private validateHintProgression(request: HintRequest): void {
    const { currentLevel, previousLevels = [] } = request;

    // レベルは順番に進む必要がある
    for (let i = 1; i < currentLevel; i++) {
      if (!previousLevels.includes(i)) {
        throw new Error(`Must complete level ${i} first`);
      }
    }
  }

  private generateLevel1Hint(): Hint {
    return {
      level: 1,
      message: this.selectRandomTemplate(this.templates.level1),
      type: 'understanding'
    };
  }

  private selectRandomTemplate(templates: string[]): string {
    const index = Math.floor(Math.random() * templates.length);
    return templates[index];
  }
}
```

**テスト実行: 🟢 Green**
```bash
$ bun test
PASS  hint-system.test.ts (リファクタリング後も全てパス)
```

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

### 絶対に守るべき3つのルール

1. **失敗するテストを書くまで、実装コードを書いてはいけない**
   - テストがない状態でコードを書き始めない
   - 「ちょっとだけ」の実装も禁止

2. **失敗するテストを1つだけ書く（コンパイルエラーも失敗）**
   - 一度に複数のテストを書かない
   - 1つのテストが失敗したらすぐに実装に移る

3. **テストを通すのに必要な最小限の実装のみを書く**
   - 過剰な実装をしない
   - 「こうなるかもしれない」という将来の予測で実装しない

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

### コード作成前
- [ ] 実装したい機能の振る舞いを明確にした
- [ ] テストファーストを実践する準備ができている

### Redフェーズ
- [ ] 失敗するテストを書いた
- [ ] テストが実際に失敗することを確認した
- [ ] 失敗メッセージが明確である

### Greenフェーズ
- [ ] 最小限の実装でテストを通した
- [ ] 過剰な実装をしていない
- [ ] テストが通ることを確認した

### Refactorフェーズ
- [ ] コードの重複を排除した
- [ ] 意味のある名前をつけた
- [ ] テストが通り続けることを確認しながらリファクタリングした
- [ ] コードが読みやすくなった

### 完了前
- [ ] 全てのテストが通っている
- [ ] カバレッジが目標値（80%）を満たしている
- [ ] テストコードも読みやすくリファクタリングされている
