# 宿題コーチロボット - 開発ガイドライン

**Document Version**: 1.1
**Last Updated**: 2026-01-29
**Status**: Active

---

## 目次

1. [開発の基本方針](#1-開発の基本方針)
2. [テスト駆動開発（TDD）](#2-テスト駆動開発tdd)
3. [コーディング規約](#3-コーディング規約)
4. [命名規則](#4-命名規則)
5. [スタイリング規約](#5-スタイリング規約)
6. [テスト規約](#6-テスト規約)
7. [Git規約](#7-git規約)
8. [レビュープロセス](#8-レビュープロセス)
9. [セキュリティガイドライン](#9-セキュリティガイドライン)

---

## 1. 開発の基本方針

### 1.1 全ての開発はテストから始める

このプロジェクトでは、**テスト駆動開発（TDD）を徹底**します。コードを書く前に必ずテストを書き、テストファーストの開発を実践します。

**基本原則:**

- **テストなしにコードを書かない**: 実装コードを書く前に、必ず失敗するテストを書く
- **小さいステップで進める**: 一度に多くの機能を実装せず、小さく確実に進める
- **リファクタリングを恐れない**: テストがあるからこそ、安心してリファクタリングできる
- **動作するきれいなコード**: テストを通すだけでなく、きれいなコードを保つ

### 1.2 なぜTDDなのか

TDDを実践することで、以下のメリットが得られます：

1. **高品質なコード**: バグの早期発見、仕様の明確化
2. **設計の改善**: テストしやすいコードは、疎結合で保守性が高い
3. **安心感**: リファクタリングや機能追加時に既存機能の破壊を防ぐ
4. **ドキュメント**: テストコードが仕様書・ドキュメントとして機能する
5. **開発速度の向上**: 長期的にはデバッグ時間が減り、開発が加速する

---

## 2. テスト駆動開発（TDD）

### 2.1 TDDの基本サイクル

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

#### 🔴 Red: 失敗するテストを書く

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

#### 🟢 Green: テストを通す最小限の実装

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

#### 🔵 Refactor: コードをきれいにする

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

### 2.2 TDD実践例：3段階ヒントシステムの実装

#### ステップ1: レベル1のテストを書く（Red）

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

#### ステップ2: テストを通す（Green）

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

#### ステップ3: リファクタリング（Refactor）

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

#### ステップ4: レベル2のテストを追加（Red → Green → Refactor）

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

### 2.3 TDDのベストプラクティス

#### 2.3.1 テストファースト（Test First）

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

#### 2.3.2 小さいステップで進める

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

#### 2.3.3 意味のあるテスト名

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

#### 2.3.4 1つのテストで1つの概念をテスト

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

### 2.4 TDD実践のルール

#### 絶対に守るべき3つのルール

1. **失敗するテストを書くまで、実装コードを書いてはいけない**
   - テストがない状態でコードを書き始めない
   - 「ちょっとだけ」の実装も禁止

2. **失敗するテストを1つだけ書く（コンパイルエラーも失敗）**
   - 一度に複数のテストを書かない
   - 1つのテストが失敗したらすぐに実装に移る

3. **テストを通すのに必要な最小限の実装のみを書く**
   - 過剰な実装をしない
   - 「こうなるかもしれない」という将来の予測で実装しない

#### 具体例: ルールの適用

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

### 2.5 バックエンドでのTDD

#### FastAPI + pytest でのTDD

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

### 2.6 TDDで困った時のQ&A

#### Q1: すでに実装してしまったコードがある場合は？

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

#### Q2: テストを書くのが難しい複雑な機能がある場合は？

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

#### Q3: 外部APIやデータベースをテストする場合は？

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

### 2.7 TDDチェックリスト

開発時に以下をチェックしてください：

```markdown
## TDD実践チェックリスト

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
```

---

## 3. コーディング規約

### 3.1 フロントエンド（TypeScript / React）

#### 基本原則

- **型安全性を最優先**: `any`の使用を避け、適切な型定義を行う
- **関数型プログラミング**: 副作用を最小化し、純粋関数を優先
- **宣言的なコード**: 命令的ではなく宣言的なコードを書く
- **コンポーネントの単一責任**: 1つのコンポーネントは1つの責任のみを持つ

#### ファイル構成

```
frontend/
├── app/                      # Next.js App Router
│   ├── (auth)/              # 認証グループルート
│   ├── session/             # セッションページ
│   ├── layout.tsx           # ルートレイアウト
│   └── page.tsx             # ホームページ
├── components/              # 再利用可能なコンポーネント
│   ├── ui/                  # UIプリミティブ
│   ├── features/            # 機能別コンポーネント
│   └── layouts/             # レイアウトコンポーネント
├── lib/                     # ユーティリティ・ヘルパー
│   ├── atoms/               # Jotai atoms
│   ├── hooks/               # カスタムフック
│   ├── utils/               # ユーティリティ関数
│   └── api/                 # APIクライアント
├── types/                   # 型定義
└── public/                  # 静的アセット
```

#### TypeScriptガイドライン

**型定義の原則:**

```typescript
// ✅ 良い例: 明示的な型定義
interface SessionConfig {
  userId: string;
  character: CharacterType;
  gradeLevel: 1 | 2 | 3;
  startTime: Date;
}

function createSession(config: SessionConfig): Session {
  // 実装
}

// ❌ 悪い例: any型の使用
function createSession(config: any): any {
  // 実装
}
```

**型のエクスポート:**

```typescript
// types/session.ts
export type CharacterType = 'robot' | 'wizard' | 'astronaut' | 'animal';

export interface Session {
  id: string;
  userId: string;
  character: CharacterType;
  status: 'active' | 'paused' | 'completed';
}

export interface DialogueTurn {
  id: string;
  speaker: 'child' | 'ai';
  content: string;
  timestamp: Date;
  emotion?: 'positive' | 'neutral' | 'negative';
}
```

**Utility Typesの活用:**

```typescript
// 既存の型から新しい型を派生
type SessionUpdate = Partial<Session>;
type SessionCreation = Omit<Session, 'id'>;
type SessionId = Pick<Session, 'id'>;
```

#### Reactコンポーネント規約

**関数コンポーネントを使用:**

```typescript
// ✅ 良い例: 関数コンポーネント + 型定義
interface CharacterAvatarProps {
  character: CharacterType;
  audioLevel: number;
  isRecording: boolean;
}

export function CharacterAvatar({
  character,
  audioLevel,
  isRecording
}: CharacterAvatarProps) {
  return (
    <div className="character-avatar">
      {/* 実装 */}
    </div>
  );
}

// ❌ 悪い例: クラスコンポーネント
export class CharacterAvatar extends React.Component {
  // 実装
}
```

**Server ComponentsとClient Componentsの区別:**

```typescript
// ✅ Server Component（デフォルト）
// app/session/[id]/page.tsx
export default async function SessionPage({ params }: { params: { id: string } }) {
  const session = await getSession(params.id);

  return (
    <div>
      <SessionHeader session={session} />
      <DialogueInterface sessionId={params.id} /> {/* Client Component */}
    </div>
  );
}

// ✅ Client Component（'use client'を明示）
// components/features/DialogueInterface.tsx
'use client';

import { useAtom } from 'jotai';
import { isRecordingAtom } from '@/lib/atoms/session';

export function DialogueInterface({ sessionId }: { sessionId: string }) {
  const [isRecording, setIsRecording] = useAtom(isRecordingAtom);

  return (
    <div>
      {/* WebSocket接続、状態管理などのクライアント側ロジック */}
    </div>
  );
}
```

**カスタムフックの作成:**

```typescript
// lib/hooks/useAudioRecorder.ts
import { useAtom } from 'jotai';
import { audioLevelAtom, isRecordingAtom } from '@/lib/atoms/session';
import { useCallback, useEffect, useRef } from 'react';

export function useAudioRecorder() {
  const [audioLevel, setAudioLevel] = useAtom(audioLevelAtom);
  const [isRecording, setIsRecording] = useAtom(isRecordingAtom);
  const streamRef = useRef<MediaStream | null>(null);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true
        }
      });
      streamRef.current = stream;
      setIsRecording(true);

      // 音声レベルの監視
      monitorAudioLevel(stream, setAudioLevel);
    } catch (error) {
      console.error('Failed to start recording:', error);
      throw error;
    }
  }, [setIsRecording, setAudioLevel]);

  const stopRecording = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setIsRecording(false);
    setAudioLevel(0);
  }, [setIsRecording, setAudioLevel]);

  useEffect(() => {
    return () => {
      // クリーンアップ
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  return {
    isRecording,
    audioLevel,
    startRecording,
    stopRecording
  };
}
```

**Jotai状態管理:**

```typescript
// lib/atoms/session.ts
import { atom } from 'jotai';
import { atomWithStorage } from 'jotai/utils';

// 基本atom
export const sessionAtom = atom<Session | null>(null);
export const isRecordingAtom = atom(false);
export const audioLevelAtom = atom(0);

// 派生atom（読み取り専用）
export const isSessionActiveAtom = atom(
  (get) => {
    const session = get(sessionAtom);
    return session?.status === 'active';
  }
);

// 書き込み可能な派生atom
export const sessionIdAtom = atom(
  (get) => get(sessionAtom)?.id ?? null,
  (get, set, newId: string | null) => {
    const currentSession = get(sessionAtom);
    if (currentSession && newId) {
      set(sessionAtom, { ...currentSession, id: newId });
    }
  }
);

// LocalStorageに永続化
export const userPreferencesAtom = atomWithStorage('user-preferences', {
  character: 'robot' as CharacterType,
  voiceSpeed: 0.9,
  volumeLevel: 1.0
});
```

#### エラーハンドリング

```typescript
// ✅ 良い例: 適切なエラーハンドリング
async function startSession(userId: string): Promise<Session> {
  try {
    const response = await fetch('/api/sessions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ userId })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const session = await response.json();
    return session;
  } catch (error) {
    if (error instanceof Error) {
      console.error('Failed to start session:', error.message);
      throw new Error(`セッションの開始に失敗しました: ${error.message}`);
    }
    throw error;
  }
}

// ❌ 悪い例: エラーの無視
async function startSession(userId: string) {
  const response = await fetch('/api/sessions', {
    method: 'POST',
    body: JSON.stringify({ userId })
  });
  return response.json();
}
```

### 3.2 バックエンド（Python / FastAPI）

#### 基本原則

- **型ヒントを必ず使用**: 全ての関数・メソッドに型ヒント
- **非同期処理**: I/O処理は`async/await`を使用
- **依存性注入**: FastAPIのDependency Injectionを活用
- **エラーハンドリング**: 適切な例外処理とHTTPステータスコード

#### ファイル構成

```
backend/
├── app/
│   ├── api/                 # APIエンドポイント
│   │   ├── v1/
│   │   │   ├── sessions.py
│   │   │   ├── dialogue.py
│   │   │   └── vision.py
│   │   └── deps.py          # 共通の依存関係
│   ├── core/                # コア機能
│   │   ├── config.py        # 設定管理
│   │   ├── security.py      # 認証・認可
│   │   └── logging.py       # ログ設定
│   ├── models/              # データモデル
│   │   ├── session.py
│   │   ├── dialogue.py
│   │   └── user.py
│   ├── services/            # ビジネスロジック
│   │   ├── dialogue_engine.py
│   │   ├── hint_system.py
│   │   └── emotion_analyzer.py
│   ├── integrations/        # 外部サービス統合
│   │   ├── gemini/
│   │   ├── firestore/
│   │   └── bigquery/
│   └── main.py              # アプリケーションエントリーポイント
├── tests/
├── requirements.txt
└── pyproject.toml
```

#### Pythonコーディング規約

**PEP 8準拠:**

```python
# ✅ 良い例: PEP 8準拠
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class DialogueTurn(BaseModel):
    """対話のターンを表すモデル"""
    turn_id: str
    speaker: str
    content: str
    timestamp: datetime
    emotion: Optional[str] = None

def create_dialogue_turn(
    speaker: str,
    content: str,
    emotion: Optional[str] = None
) -> DialogueTurn:
    """
    新しい対話ターンを作成する

    Args:
        speaker: 話者（'child' or 'ai'）
        content: 発話内容
        emotion: 感情状態（オプション）

    Returns:
        作成された DialogueTurn インスタンス
    """
    return DialogueTurn(
        turn_id=generate_id(),
        speaker=speaker,
        content=content,
        timestamp=datetime.now(),
        emotion=emotion
    )

# ❌ 悪い例: PEP 8違反
def createDialogueTurn(speaker,content,emotion=None):
    return DialogueTurn(turn_id=generate_id(),speaker=speaker,content=content,timestamp=datetime.now(),emotion=emotion)
```

**型ヒントの徹底:**

```python
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel

# ✅ 良い例: 完全な型ヒント
async def get_session(
    session_id: str,
    db: FirestoreClient
) -> Optional[Session]:
    """セッションを取得する"""
    doc = await db.collection('sessions').document(session_id).get()
    if not doc.exists:
        return None
    return Session(**doc.to_dict())

async def list_user_sessions(
    user_id: str,
    limit: int = 10,
    db: FirestoreClient
) -> List[Session]:
    """ユーザーのセッション一覧を取得する"""
    docs = await db.collection('sessions')\
        .where('userId', '==', user_id)\
        .limit(limit)\
        .get()
    return [Session(**doc.to_dict()) for doc in docs]

# ❌ 悪い例: 型ヒントなし
async def get_session(session_id, db):
    doc = await db.collection('sessions').document(session_id).get()
    if not doc.exists:
        return None
    return Session(**doc.to_dict())
```

**FastAPI APIエンドポイント:**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_current_user, get_db
from app.models.session import SessionCreate, SessionResponse
from app.services.dialogue_engine import DialogueEngine

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])

@router.post(
    "",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="新しいセッションを作成"
)
async def create_session(
    session_data: SessionCreate,
    current_user: User = Depends(get_current_user),
    db: FirestoreClient = Depends(get_db)
) -> SessionResponse:
    """
    新しい学習セッションを作成する

    - **userId**: ユーザーID
    - **character**: キャラクタータイプ（robot, wizard, astronaut, animal）
    - **gradeLevel**: 学年（1-3）
    """
    try:
        session = await DialogueEngine.create_session(
            user_id=current_user.id,
            character=session_data.character,
            grade_level=session_data.gradeLevel,
            db=db
        )
        return SessionResponse(**session.dict())
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="セッションの作成に失敗しました"
        )

@router.get(
    "/{session_id}",
    response_model=SessionResponse,
    summary="セッション情報を取得"
)
async def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: FirestoreClient = Depends(get_db)
) -> SessionResponse:
    """指定されたIDのセッション情報を取得する"""
    session = await db.collection('sessions').document(session_id).get()

    if not session.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="セッションが見つかりません"
        )

    session_data = session.to_dict()

    # 権限チェック: 自分のセッションのみアクセス可能
    if session_data['userId'] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="このセッションにアクセスする権限がありません"
        )

    return SessionResponse(**session_data)
```

**WebSocket実装:**

```python
from fastapi import WebSocket, WebSocketDisconnect
from app.services.dialogue_engine import DialogueEngine

@router.websocket("/ws/dialogue/{session_id}")
async def dialogue_websocket(
    websocket: WebSocket,
    session_id: str,
    token: str,  # クエリパラメータで認証トークンを受け取る
    db: FirestoreClient = Depends(get_db)
):
    """
    双方向音声対話のWebSocketエンドポイント
    """
    # 認証
    try:
        user = await verify_token(token)
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # WebSocket接続確立
    await websocket.accept()

    # DialogueEngineの初期化
    engine = DialogueEngine(session_id=session_id, db=db)

    try:
        while True:
            # クライアントから音声チャンクを受信
            audio_chunk = await websocket.receive_bytes()

            # 音声処理・応答生成
            response_audio = await engine.process_audio(audio_chunk)

            # 応答音声を送信
            if response_audio:
                await websocket.send_bytes(response_audio)

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
        await engine.cleanup()
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        await engine.cleanup()
```

**非同期処理:**

```python
import asyncio
from typing import List

# ✅ 良い例: 並行処理の活用
async def get_user_progress_summary(user_id: str, db: FirestoreClient) -> Dict[str, Any]:
    """ユーザーの学習進捗サマリーを取得"""
    # 複数のデータソースから並行して取得
    sessions_task = db.collection('sessions')\
        .where('userId', '==', user_id)\
        .get()
    history_task = db.collection('learning_history')\
        .where('userId', '==', user_id)\
        .get()

    sessions, history = await asyncio.gather(sessions_task, history_task)

    return {
        'total_sessions': len(sessions),
        'total_problems': len(history),
        'self_solved_count': sum(1 for h in history if h['solved_independently']),
        'average_hints_used': sum(h['hints_used'] for h in history) / len(history) if history else 0
    }

# ❌ 悪い例: 同期的な逐次処理
async def get_user_progress_summary(user_id: str, db: FirestoreClient) -> Dict[str, Any]:
    sessions = await db.collection('sessions').where('userId', '==', user_id).get()
    history = await db.collection('learning_history').where('userId', '==', user_id).get()
    # 無駄な待ち時間が発生
```

**エラーハンドリング:**

```python
from app.core.exceptions import (
    SessionNotFoundError,
    UnauthorizedError,
    ValidationError
)

# カスタム例外の定義
class SessionNotFoundError(Exception):
    """セッションが見つからない場合の例外"""
    pass

# グローバル例外ハンドラ
@app.exception_handler(SessionNotFoundError)
async def session_not_found_handler(request: Request, exc: SessionNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": "セッションが見つかりません"}
    )

# サービス層でのエラーハンドリング
async def get_session_or_fail(session_id: str, db: FirestoreClient) -> Session:
    """
    セッションを取得する。見つからない場合は例外を発生。
    """
    try:
        doc = await db.collection('sessions').document(session_id).get()
        if not doc.exists:
            raise SessionNotFoundError(f"Session {session_id} not found")
        return Session(**doc.to_dict())
    except Exception as e:
        logger.error(f"Failed to get session {session_id}: {e}")
        raise
```

---

## 4. 命名規則

### 4.1 フロントエンド（TypeScript / React）

#### ファイル命名

```
components/
├── CharacterAvatar.tsx          # PascalCase（コンポーネント）
├── useAudioRecorder.ts          # camelCase（カスタムフック、useプレフィックス）
├── session.types.ts             # kebab-case（型定義）
└── api-client.ts                # kebab-case（ユーティリティ）
```

#### 変数・関数命名

```typescript
// 変数: camelCase
const sessionId = 'abc123';
const isRecording = false;
const audioLevel = 0.5;

// 定数: UPPER_SNAKE_CASE
const MAX_AUDIO_LEVEL = 100;
const DEFAULT_CHARACTER: CharacterType = 'robot';
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

// 関数: camelCase
function createSession(userId: string): Session { }
async function fetchUserData(userId: string): Promise<User> { }

// Boolean変数: is/has/canプレフィックス
const isLoading = true;
const hasError = false;
const canSubmit = true;

// コンポーネント: PascalCase
function CharacterAvatar() { }
function DialogueInterface() { }

// カスタムフック: use + PascalCase
function useAudioRecorder() { }
function useSessionState() { }
```

#### 型・インターフェース命名

```typescript
// インターフェース: PascalCase
interface Session {
  id: string;
  userId: string;
}

// 型エイリアス: PascalCase
type CharacterType = 'robot' | 'wizard' | 'astronaut' | 'animal';

// Props型: コンポーネント名 + Props
interface CharacterAvatarProps {
  character: CharacterType;
  audioLevel: number;
}

// イベントハンドラー型: on + 動詞
type OnRecordingStart = () => void;
type OnAudioReceived = (audio: ArrayBuffer) => void;
```

### 4.2 バックエンド（Python）

#### ファイル命名

```
app/
├── dialogue_engine.py          # snake_case
├── hint_system.py              # snake_case
└── emotion_analyzer.py         # snake_case
```

#### 変数・関数命名

```python
# 変数: snake_case
session_id = 'abc123'
is_recording = False
audio_level = 0.5

# 定数: UPPER_SNAKE_CASE
MAX_AUDIO_LEVEL = 100
DEFAULT_CHARACTER = 'robot'
API_BASE_URL = os.getenv('API_BASE_URL')

# 関数: snake_case
def create_session(user_id: str) -> Session:
    pass

async def fetch_user_data(user_id: str) -> User:
    pass

# Boolean変数: is/has/canプレフィックス
is_loading = True
has_error = False
can_submit = True

# プライベート関数・変数: _プレフィックス
def _internal_helper(data: str) -> str:
    pass

_private_constant = 'internal'
```

#### クラス命名

```python
# クラス: PascalCase
class DialogueEngine:
    pass

class HintSystem:
    pass

# 例外クラス: Error/Exceptionサフィックス
class SessionNotFoundError(Exception):
    pass

class ValidationError(ValueError):
    pass

# Pydanticモデル: PascalCase
class SessionCreate(BaseModel):
    user_id: str
    character: str

class SessionResponse(BaseModel):
    id: str
    user_id: str
    status: str
```

---

## 5. スタイリング規約

### 5.1 フロントエンド

#### TailwindCSS利用規約

**基本原則:**

- ユーティリティクラスを優先
- カスタムCSSは最小限に
- コンポーネント固有のスタイルは`@apply`で抽象化

```tsx
// ✅ 良い例: Tailwind Utility Classes
export function CharacterAvatar({ character, audioLevel }: CharacterAvatarProps) {
  return (
    <div className="relative w-64 h-64 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 shadow-lg">
      <div className="absolute inset-0 flex items-center justify-center">
        <RiveAnimation character={character} audioLevel={audioLevel} />
      </div>
    </div>
  );
}

// カスタムコンポーネントスタイル（必要な場合のみ）
// globals.css
@layer components {
  .character-avatar {
    @apply relative w-64 h-64 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 shadow-lg;
  }
}
```

**レスポンシブデザイン:**

```tsx
<div className="
  w-full
  md:w-1/2
  lg:w-1/3
  p-4
  sm:p-6
  lg:p-8
">
  {/* モバイルファースト */}
</div>
```

**ダークモード対応:**

```tsx
<div className="
  bg-white
  dark:bg-gray-900
  text-gray-900
  dark:text-gray-100
">
  {/* ライト/ダークモード対応 */}
</div>
```

#### アクセシビリティ

```tsx
// ✅ 良い例: アクセシビリティ配慮
<button
  type="button"
  aria-label="録音を開始"
  aria-pressed={isRecording}
  className="btn-primary"
  onClick={startRecording}
>
  <MicrophoneIcon className="w-6 h-6" aria-hidden="true" />
  {isRecording ? '録音中' : '録音開始'}
</button>

// ❌ 悪い例: アクセシビリティ不足
<div onClick={startRecording}>
  <MicrophoneIcon />
</div>
```

### 5.2 コードフォーマット

#### フロントエンド（Prettier）

```json
// .prettierrc
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "arrowParens": "always"
}
```

#### バックエンド（Black + isort）

```toml
# pyproject.toml
[tool.black]
line-length = 100
target-version = ['py310']
include = '\.pyi?$'

[tool.isort]
profile = "black"
line_length = 100
multi_line_output = 3
include_trailing_comma = true
```

---

## 6. テスト規約

### 6.1 フロントエンドテスト

#### テストファイル構成

```
components/
├── CharacterAvatar.tsx
├── CharacterAvatar.test.tsx
└── __tests__/
    └── CharacterAvatar.integration.test.tsx
```

#### ユニットテスト（Vitest + Testing Library）

```typescript
// CharacterAvatar.test.tsx
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { CharacterAvatar } from './CharacterAvatar';

describe('CharacterAvatar', () => {
  it('should render with robot character', () => {
    render(<CharacterAvatar character="robot" audioLevel={0} isRecording={false} />);

    const avatar = screen.getByRole('img', { name: /robot/i });
    expect(avatar).toBeInTheDocument();
  });

  it('should update audio level animation', () => {
    const { rerender } = render(
      <CharacterAvatar character="robot" audioLevel={0} isRecording={true} />
    );

    rerender(<CharacterAvatar character="robot" audioLevel={50} isRecording={true} />);

    // アニメーションの確認（実装に応じて）
    const avatar = screen.getByTestId('character-avatar');
    expect(avatar).toHaveStyle({ '--audio-level': 50 });
  });
});
```

#### カスタムフックのテスト

```typescript
// useAudioRecorder.test.ts
import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { useAudioRecorder } from './useAudioRecorder';

// getUserMediaのモック
global.navigator.mediaDevices = {
  getUserMedia: vi.fn()
};

describe('useAudioRecorder', () => {
  it('should start recording', async () => {
    const mockStream = { getTracks: () => [] };
    (navigator.mediaDevices.getUserMedia as any).mockResolvedValue(mockStream);

    const { result } = renderHook(() => useAudioRecorder());

    await act(async () => {
      await result.current.startRecording();
    });

    expect(result.current.isRecording).toBe(true);
  });

  it('should stop recording', async () => {
    const { result } = renderHook(() => useAudioRecorder());

    await act(async () => {
      await result.current.startRecording();
      result.current.stopRecording();
    });

    expect(result.current.isRecording).toBe(false);
    expect(result.current.audioLevel).toBe(0);
  });
});
```

#### テストカバレッジ目標

- **ユニットテスト**: 80%以上
- **統合テスト**: 主要フロー100%
- **E2Eテスト**: クリティカルパス100%

### 6.2 バックエンドテスト

#### テストファイル構成

```
tests/
├── unit/
│   ├── test_dialogue_engine.py
│   └── test_hint_system.py
├── integration/
│   └── test_api_sessions.py
└── conftest.py
```

#### ユニットテスト（pytest）

```python
# tests/unit/test_dialogue_engine.py
import pytest
from app.services.dialogue_engine import DialogueEngine
from app.models.session import Session

@pytest.fixture
def mock_session():
    return Session(
        id='test-session-id',
        user_id='test-user-id',
        character='robot',
        grade_level=2,
        status='active'
    )

@pytest.mark.asyncio
async def test_create_session(mock_db):
    """セッション作成のテスト"""
    engine = DialogueEngine(db=mock_db)
    session = await engine.create_session(
        user_id='test-user-id',
        character='robot',
        grade_level=2
    )

    assert session.id is not None
    assert session.user_id == 'test-user-id'
    assert session.character == 'robot'
    assert session.status == 'active'

@pytest.mark.asyncio
async def test_generate_hint_level_1(mock_session):
    """レベル1ヒント生成のテスト"""
    engine = DialogueEngine(db=mock_db)
    hint = await engine.generate_hint(
        session=mock_session,
        problem="3 + 5 = ?",
        hint_level=1
    )

    assert hint is not None
    assert "問題" in hint or "何" in hint  # 問題理解の確認
    assert len(hint) > 0
```

#### 統合テスト（pytest + TestClient）

```python
# tests/integration/test_api_sessions.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_session():
    """セッション作成APIのテスト"""
    response = client.post(
        "/api/v1/sessions",
        json={
            "userId": "test-user-id",
            "character": "robot",
            "gradeLevel": 2
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["userId"] == "test-user-id"
    assert data["character"] == "robot"
    assert "id" in data

def test_get_session_not_found():
    """存在しないセッションの取得テスト"""
    response = client.get(
        "/api/v1/sessions/nonexistent-id",
        headers={"Authorization": f"Bearer {test_token}"}
    )

    assert response.status_code == 404
    assert "見つかりません" in response.json()["detail"]

def test_get_session_forbidden():
    """他人のセッションへのアクセステスト"""
    # 他のユーザーのセッションを作成
    other_session_response = client.post(
        "/api/v1/sessions",
        json={"userId": "other-user-id", "character": "wizard", "gradeLevel": 1},
        headers={"Authorization": f"Bearer {other_user_token}"}
    )
    other_session_id = other_session_response.json()["id"]

    # 別のユーザーでアクセスを試みる
    response = client.get(
        f"/api/v1/sessions/{other_session_id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )

    assert response.status_code == 403
```

#### テストカバレッジ目標

```bash
# カバレッジ測定
pytest --cov=app --cov-report=html --cov-report=term

# 目標
# - ユニットテスト: 80%以上
# - 統合テスト: 主要API 100%
```

---

## 7. Git規約

### 7.1 ブランチ戦略（Git Flow）

```
main (本番環境)
  ↑
develop (開発環境)
  ↑
feature/xxx (機能開発)
hotfix/xxx (緊急修正)
```

**ブランチ命名規則:**

```bash
# 機能開発
feature/dialogue-engine
feature/camera-interface
feature/hint-system-level-1

# バグ修正
fix/audio-recording-issue
fix/websocket-disconnect

# ホットフィックス
hotfix/critical-audio-bug
hotfix/security-vulnerability

# リファクタリング
refactor/reorganize-components
refactor/optimize-audio-processing

# ドキュメント
docs/update-architecture
docs/add-api-documentation
```

### 7.2 コミットメッセージ規約

**フォーマット:**

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type:**

```bash
feat:     新機能追加
fix:      バグ修正
docs:     ドキュメント更新
style:    コードフォーマット（機能変更なし）
refactor: リファクタリング
test:     テスト追加・修正
chore:    ビルド・設定変更
perf:     パフォーマンス改善
ci:       CI/CD設定変更
```

**例:**

```bash
# 良い例
feat(dialogue): add 3-level hint system

Implemented the 3-level hint system as specified in PRD:
- Level 1: Problem understanding confirmation
- Level 2: Recall of learned knowledge
- Level 3: Partial support

Closes #42

# 良い例（日本語）
feat(dialogue): 3段階ヒントシステムの実装

PRDに記載された3段階ヒントシステムを実装:
- レベル1: 問題理解の確認
- レベル2: 既習事項の想起
- レベル3: 部分的支援

Closes #42

# 悪い例
update code
```

### 7.3 コミット粒度

```bash
# ✅ 良い例: 適切な粒度
git commit -m "feat(audio): add audio recording component"
git commit -m "feat(audio): integrate Web Audio API for level monitoring"
git commit -m "test(audio): add tests for audio recorder hook"

# ❌ 悪い例: 粒度が大きすぎる
git commit -m "feat: implement entire dialogue system with audio and hints"

# ❌ 悪い例: 粒度が小さすぎる
git commit -m "fix: typo"
git commit -m "fix: another typo"
git commit -m "fix: one more typo"
```

### 7.4 プルリクエスト

**PRタイトル:**

```
feat(dialogue): ソクラテス式対話エンジンの実装
fix(audio): WebSocket接続の切断問題を修正
```

**PRテンプレート:**

```markdown
## 概要
<!-- この変更の概要を記載 -->

## 変更内容
<!-- 具体的な変更内容を箇条書きで -->
-
-
-

## 関連Issue
<!-- 関連するIssueをリンク -->
Closes #123

## テスト
<!-- テスト方法を記載 -->
- [ ] ユニットテスト追加
- [ ] 統合テスト追加
- [ ] 手動テスト完了

## スクリーンショット（該当する場合）
<!-- UI変更の場合はスクリーンショットを添付 -->

## チェックリスト
- [ ] コードレビュー依頼前に自己レビュー完了
- [ ] テストが全て通過
- [ ] ドキュメント更新（必要な場合）
- [ ] CLAUDE.mdの指針に従っている
```

### 7.5 コードレビュー

**レビュワーの責任:**

- コードの正確性を確認
- セキュリティ脆弱性のチェック
- パフォーマンスへの影響を評価
- 可読性・保守性を確認
- テストの妥当性を検証

**レビュー基準:**

```markdown
## 必須チェック項目
- [ ] 機能要件を満たしているか
- [ ] テストが十分か（カバレッジ80%以上）
- [ ] セキュリティリスクはないか
- [ ] パフォーマンスへの悪影響はないか
- [ ] コーディング規約に準拠しているか
- [ ] ドキュメントが適切に更新されているか

## 推奨チェック項目
- [ ] より良い実装方法はないか
- [ ] エッジケースが考慮されているか
- [ ] エラーハンドリングが適切か
- [ ] ログ出力が適切か
```

---

## 8. レビュープロセス

### 8.1 プルリクエストの作成

1. **ブランチ作成**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. **変更の実装**
   - 小さく、レビュー可能な単位で実装
   - 1PR = 1機能/修正を原則とする

3. **自己レビュー**
   - コミット前に自分でコードを確認
   - 不要なコメント・デバッグコードを削除
   - テストを実行

4. **PR作成**
   ```bash
   git push origin feature/your-feature-name
   # GitHub上でPR作成
   ```

### 8.2 レビューフロー

```
作成者: PR作成
  ↓
レビュワー1: 初回レビュー（1営業日以内）
  ↓
作成者: フィードバック対応
  ↓
レビュワー2: 2次レビュー（必要な場合）
  ↓
承認 → マージ
```

### 8.3 マージ基準

- 最低1名のApprove必須
- CIが全てグリーン
- コンフリクト解消済み
- 全てのコメントが解決済み

---

## 9. セキュリティガイドライン

### 9.1 機密情報の管理

**環境変数の使用:**

```bash
# ❌ 悪い例: ハードコード
const GEMINI_API_KEY = 'AIzaSyC...';

# ✅ 良い例: 環境変数
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;

# ✅ 良い例（Python）
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
```

**.gitignoreに追加:**

```gitignore
# 機密情報
.env
.env.local
.env.production
*.pem
*.key
credentials.json
service-account.json

# ログ・デバッグファイル
*.log
debug.log
```

### 9.2 入力検証

```typescript
// ✅ 良い例: サーバー側で検証
import { z } from 'zod';

const SessionCreateSchema = z.object({
  userId: z.string().uuid(),
  character: z.enum(['robot', 'wizard', 'astronaut', 'animal']),
  gradeLevel: z.number().int().min(1).max(3)
});

export async function createSession(data: unknown) {
  // バリデーション
  const validated = SessionCreateSchema.parse(data);

  // 処理
  return await createSessionInDb(validated);
}
```

```python
# ✅ 良い例: Pydanticで検証
from pydantic import BaseModel, validator

class SessionCreate(BaseModel):
    user_id: str
    character: str
    grade_level: int

    @validator('character')
    def validate_character(cls, v):
        allowed = ['robot', 'wizard', 'astronaut', 'animal']
        if v not in allowed:
            raise ValueError(f'character must be one of {allowed}')
        return v

    @validator('grade_level')
    def validate_grade_level(cls, v):
        if v < 1 or v > 3:
            raise ValueError('grade_level must be between 1 and 3')
        return v
```

### 9.3 XSS対策

```typescript
// ✅ 良い例: Reactの自動エスケープ
export function DialogueMessage({ content }: { content: string }) {
  return <p>{content}</p>; // 自動的にエスケープされる
}

// ❌ 悪い例: dangerouslySetInnerHTMLの不用意な使用
export function DialogueMessage({ content }: { content: string }) {
  return <p dangerouslySetInnerHTML={{ __html: content }} />; // XSSリスク
}

// ✅ 良い例: 必要な場合はサニタイズ
import DOMPurify from 'isomorphic-dompurify';

export function DialogueMessage({ content }: { content: string }) {
  const sanitized = DOMPurify.sanitize(content);
  return <p dangerouslySetInnerHTML={{ __html: sanitized }} />;
}
```

### 9.4 SQLインジェクション対策

```python
# ✅ 良い例: パラメータ化クエリ（BigQuery）
from google.cloud import bigquery

async def get_user_sessions(user_id: str):
    query = """
        SELECT * FROM homework_coach.sessions
        WHERE user_id = @user_id
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
        ]
    )
    results = client.query(query, job_config=job_config)
    return list(results)

# ❌ 悪い例: 文字列結合
async def get_user_sessions(user_id: str):
    query = f"SELECT * FROM sessions WHERE user_id = '{user_id}'"
    # SQLインジェクションリスク
```

### 9.5 認証・認可

```python
# ✅ 良い例: 適切な認証・認可
from fastapi import Depends, HTTPException, status
from firebase_admin import auth

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

@router.get("/api/v1/sessions/{session_id}")
async def get_session(
    session_id: str,
    current_user = Depends(get_current_user)
):
    session = await fetch_session(session_id)

    # 認可チェック
    if session.user_id != current_user['uid']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return session
```

### 9.6 レート制限

```python
# API rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.post("/api/v1/vision/recognize")
@limiter.limit("10/minute")
async def recognize_image(request: Request):
    # 処理
    pass
```

---

## 付録

### A. 推奨ツール

**フロントエンド:**
- VS Code Extensions: ESLint, Prettier, Tailwind CSS IntelliSense
- Bun: パッケージマネージャー
- Vitest: テストフレームワーク

**バックエンド:**
- VS Code Extensions: Python, Pylance, Black Formatter
- uv: パッケージマネージャー
- pytest: テストフレームワーク

**共通:**
- Git: バージョン管理
- GitHub Actions: CI/CD
- Cloud Build: デプロイ

### B. 参考資料

**TDD関連:**
- [t_wada: テスト駆動開発](https://twitter.com/t_wada)
- [Test Driven Development: By Example (Kent Beck)](https://www.amazon.co.jp/dp/0321146530)
- [テスト駆動開発 (Kent Beck著、和田卓人訳)](https://www.amazon.co.jp/dp/4274217884)

**フロントエンド:**
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [React Documentation](https://react.dev/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Vitest Documentation](https://vitest.dev/)
- [Testing Library Documentation](https://testing-library.com/)

**バックエンド:**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [pytest Documentation](https://docs.pytest.org/)
- [PEP 8 -- Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

---

## 変更履歴

### v1.1 (2026-01-29)
- **TDD（テスト駆動開発）セクションを追加**
  - t_wadaが提唱するTDDの原則を詳細に記載
  - Red-Green-Refactorサイクルの説明
  - 3段階ヒントシステムの実装例
  - TDDベストプラクティス
  - TDD実践のルール（3つの絶対ルール）
  - バックエンドでのTDD実践例
  - TDDチェックリスト
- 開発の基本方針セクションを追加
- 全セクション番号を再構成（TDD追加により繰り下げ）

### v1.0 (2026-01-29)
- 初版作成
- コーディング規約、命名規則、スタイリング規約を定義
- テスト規約、Git規約、レビュープロセスを策定
- セキュリティガイドラインを記載

---

**最終更新**: 2026-01-29
**次回レビュー**: MVP開発開始時
