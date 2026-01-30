# 宿題コーチロボット - 開発ガイドライン

**Document Version**: 1.4
**Last Updated**: 2026-01-31
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

**重要**: 実装開始時は、必ず**TDD skill**を参照してください。

### 2.1 TDD Skillの使用

このプロジェクトでは、和田卓人（t_wada）が提唱するテスト駆動開発を徹底します。

実装時は以下のコマンドでTDD skillを呼び出してください：

```
/tdd
```

TDD skillには以下が含まれます：

- **Red-Green-Refactor**サイクルの詳細解説
- **仮実装・三角測量・明白な実装**の3つの戦略
- **TODOリスト駆動開発**
- **ベイビーステップ**の実践方法
- 3段階ヒントシステムの実装例（完全なコード付き）
- TDDベストプラクティス
- バックエンド（FastAPI + pytest）でのTDD
- TDDで困った時のQ&A
- TDDチェックリスト

**テストカバレッジ目標: 80%以上**

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

**重要**: FastAPI実装時は、必ず**FastAPI skill**を参照してください。

#### FastAPI Skillの使用

実装時は以下のコマンドでFastAPI skillを呼び出してください：

```
/fastapi
```

FastAPI skillには以下が含まれます：

- **プロジェクト構造**（ドメインベース）
- **Firestore統合**パターン
- **JWT認証**の実装方法
- **Pydantic v2**のベストプラクティス
- **7つの既知の問題**と予防策
- CORS、バリデーション、非同期処理のパターン
- テストとデプロイメント

#### 基本原則

- **型ヒントを必ず使用**: 全ての関数・メソッドに型ヒント
- **非同期処理**: I/O処理は`async/await`を使用
- **依存性注入**: FastAPIのDependency Injectionを活用
- **エラーハンドリング**: 適切な例外処理とHTTPステータスコード

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
from typing import Optional, List, Dict, Any

# ✅ 良い例: 完全な型ヒント
async def get_session(session_id: str, db: FirestoreClient) -> Optional[Session]:
    """セッションを取得する"""
    # 実装は FastAPI skill を参照

# ❌ 悪い例: 型ヒントなし
async def get_session(session_id, db):
    # 型情報が欠落
```

**詳細な実装例は `/fastapi` skillを参照してください。**

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

### v1.4 (2026-01-31)
- **FastAPI重複記述の削除**
  - development-guidelines.mdからFastAPIの詳細実装例を削除
  - ファイル構成、APIエンドポイント、WebSocket、非同期処理、エラーハンドリングの例を削除
  - FastAPI skillへの参照のみに簡素化
  - FastAPI skill (v1.0) にFirestore統合を含む完全なガイドラインを集約

### v1.3 (2026-01-31)
- **TDD重複記述の削除**
  - development-guidelines.mdからTDDの詳細な記述を削除
  - TDD skillへの参照のみに簡素化
  - TDD skill (v2.0) に完全な和田卓人準拠のガイドラインを集約

### v1.2 (2026-01-29)
- **TDDセクションをskillに移行**
  - TDDの詳細を `.claude/skills/tdd/skill.md` に分離
  - development-guidelines.mdには概要とskill参照方法を記載
  - TDDの実装例、ベストプラクティス、Q&Aをskillに集約

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

**最終更新**: 2026-01-31
**次回レビュー**: MVP開発開始時
