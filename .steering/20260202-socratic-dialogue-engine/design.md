# Design - ソクラテス式対話エンジン

## アーキテクチャ概要

```
┌─────────────────────────────────────────────────────────────┐
│                    対話エンジン層 (ADK)                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌─────────────────────────────┐    │
│  │  ADK Runner     │───▶│  Homework Coach Agent       │    │
│  │                 │    │                             │    │
│  │ - SessionService│    │ - SocraticDialogueManager   │    │
│  │ - MemoryService │    │ - instruction (SYSTEM_PROMPT)│   │
│  └─────────────────┘    └─────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Gemini Live API                          │
│                 (音声入出力 + LLM推論)                       │
└─────────────────────────────────────────────────────────────┘
```

## 技術選定

| コンポーネント | 技術 | 理由 |
|--------------|------|------|
| フレームワーク | Google ADK | Live API対応、Agentパターン |
| セッション管理 | ADK SessionService | 対話履歴の自動管理 |
| 長期記憶 | ADK MemoryBankService | ユーザーの学習履歴 |
| LLM | Gemini 2.5 Flash | Native Audio対応、低レイテンシ |
| 言語 | Python 3.10+ | ADK公式サポート |
| テスト | pytest | Python標準、TDD向け |
| 型チェック | Pydantic v2 | データバリデーション |

---

## ADKセッション管理

### ADKが管理するもの

ADKの`SessionService`が以下を自動管理するため、独自のStateTrackerは不要：

| 項目 | ADKの機能 |
|------|----------|
| 対話履歴 | `session.events` に自動保存 |
| 独自状態 | `session.state` に保存可能 |
| 長期記憶 | `MemoryBankService` で永続化 |

### session.stateに保存する独自状態

```python
# ADKセッションのstateに保存する独自の状態
session.state = {
    "current_phase": 2,           # 対話フローのフェーズ (1-7)
    "problem": "3 + 5 = ?",       # 現在の問題
    "attempts_count": 1,          # 試行回数
    "last_question_types": ["understanding_check"],  # 重複防止用
}
```

### ローカル開発時のセッションサービス

```python
# 開発環境: InMemorySessionService
from google.adk.sessions import InMemorySessionService
session_service = InMemorySessionService()

# 本番環境: VertexAiSessionService
from google.adk.sessions import VertexAiSessionService
session_service = VertexAiSessionService(
    project=PROJECT_ID,
    location=LOCATION,
    agent_engine_id=AGENT_ENGINE_ID,
)
```

---

## データ設計

### 対話コンテキスト（DTO）

ADKセッションから取得したデータを整形するためのモデル：

```python
from enum import Enum
from pydantic import BaseModel
from datetime import datetime


class QuestionType(str, Enum):
    """質問タイプ"""
    UNDERSTANDING_CHECK = "understanding_check"  # 理解確認
    THINKING_GUIDE = "thinking_guide"            # 思考誘導
    HINT = "hint"                                # ヒント


class DialogueTone(str, Enum):
    """対話トーン"""
    ENCOURAGING = "encouraging"  # 励まし
    NEUTRAL = "neutral"          # 中立
    EMPATHETIC = "empathetic"    # 共感


class ResponseAnalysis(BaseModel):
    """回答分析結果"""
    understanding_level: int  # 0-10: 理解度
    is_correct_direction: bool
    needs_clarification: bool
    key_insights: list[str]


class DialogueTurn(BaseModel):
    """対話ターン"""
    speaker: str  # "child" | "coach"
    content: str
    timestamp: datetime
    question_type: QuestionType | None = None
    tone: DialogueTone | None = None


class DialogueContext(BaseModel):
    """対話コンテキスト（ADKセッションから構築）"""
    session_id: str
    problem: str
    turns: list[DialogueTurn]
    current_phase: int  # 1-7: 対話フローのフェーズ
    attempts_count: int
    last_question_types: list[QuestionType]  # 重複防止用

    @classmethod
    def from_adk_session(cls, session) -> "DialogueContext":
        """ADKセッションからDialogueContextを構築"""
        state = session.state or {}
        return cls(
            session_id=session.id,
            problem=state.get("problem", ""),
            turns=[],  # session.eventsから構築
            current_phase=state.get("current_phase", 1),
            attempts_count=state.get("attempts_count", 0),
            last_question_types=state.get("last_question_types", []),
        )
```

### 対話フローフェーズ

```
Phase 1: 問題読み上げ
Phase 2: 理解度確認
Phase 3: 子供の回答を分析
Phase 4: 思考プロセスの誘導
Phase 5: 部分的な回答の評価
Phase 6: 最終回答
Phase 7: プロセスの振り返り
```

---

## コンポーネント設計

### SocraticDialogueManager

```python
class SocraticDialogueManager:
    """ソクラテス式対話マネージャ（プロンプト管理を含む）"""

    SYSTEM_PROMPT = """
あなたは小学校低学年の子供を導く優しいコーチです。
子供が自分で答えに気づけるよう、質問で導いてください。
決して答えを直接教えないでください。

重要なルール:
1. 簡単な言葉を使う（小学1-3年生が理解できるレベル）
2. 一度に1つの質問だけする
3. 子供の回答を肯定的に受け止める
4. 間違いを責めない
"""

    def __init__(self):
        self._question_history: list[str] = []

    def analyze_response(
        self,
        child_response: str,
        context: DialogueContext
    ) -> ResponseAnalysis:
        """子供の回答を分析"""
        pass

    def generate_question(
        self,
        context: DialogueContext,
        question_type: QuestionType,
        tone: DialogueTone
    ) -> str:
        """次の質問を生成"""
        pass

    def determine_question_type(
        self,
        analysis: ResponseAnalysis,
        context: DialogueContext
    ) -> QuestionType:
        """質問タイプを決定"""
        pass

    def determine_tone(
        self,
        analysis: ResponseAnalysis,
        context: DialogueContext
    ) -> DialogueTone:
        """トーンを決定"""
        pass

    def should_move_to_next_phase(
        self,
        analysis: ResponseAnalysis,
        context: DialogueContext
    ) -> bool:
        """次のフェーズに進むべきか判定"""
        pass

    def build_question_prompt(
        self,
        context: DialogueContext,
        question_type: QuestionType,
        tone: DialogueTone
    ) -> str:
        """質問生成用プロンプトを構築"""
        pass

    def build_analysis_prompt(
        self,
        child_response: str,
        context: DialogueContext
    ) -> str:
        """回答分析用プロンプトを構築"""
        pass
```

---

## ファイル構成

```
backend/
├── app/
│   └── services/
│       └── adk/
│           ├── __init__.py
│           ├── dialogue/
│           │   ├── __init__.py
│           │   ├── manager.py      # SocraticDialogueManager
│           │   └── models.py       # データモデル（Enum, DTO）
│           └── agent.py            # Homework Coach Agent
└── tests/
    └── unit/
        └── services/
            └── adk/
                └── dialogue/
                    ├── __init__.py
                    └── test_manager.py
```

---

## エラーハンドリング

### エラー種別

| エラー | 対処 |
|--------|------|
| LLM応答なし | フォールバック定型質問を使用 |
| 不正な回答形式 | 再質問を促す |
| セッション取得失敗 | 新規セッション作成 |

### フォールバック質問

```python
FALLBACK_QUESTIONS = [
    "この問題、何を聞いてると思う？",
    "もう一回問題読んでみようか",
    "前に似たような問題やったよね？",
]
```

---

## セキュリティ考慮事項

1. **入力バリデーション**: 子供の発話は必ずサニタイズ
2. **プロンプトインジェクション対策**: システムプロンプトを厳格に設計
3. **ログ出力**: 子供の個人情報をログに含めない
4. **セッション管理**: ADKのセッションサービスに委譲

---

## パフォーマンス考慮事項

1. **プロンプト最適化**: トークン数を最小化
2. **コンテキスト圧縮**: 長い対話履歴は要約
3. **キャッシング**: 定型的な質問はキャッシュ可能
4. **ストリーミング**: 応答はストリーミングで返す

---

## 代替案と採用理由

### 案1: 全てをLLMに任せる

- **概要**: 対話ロジックを全てLLMのプロンプトで制御
- **不採用理由**: テスト困難、一貫性が保てない

### 案2: ルールベース + LLM + ADKセッション（採用）

- **概要**: 対話フロー制御はコード、状態管理はADKセッション、質問生成のみLLM
- **採用理由**: テスト可能、ADKの機能を活用、シンプルな構成

### 案3: 独自StateTracker

- **概要**: ADKセッションを使わず独自で状態管理
- **不採用理由**: ADKの機能と重複、車輪の再発明

---

## 学習プロファイル永続化（ハイブリッドアプローチ）

セッション終了後に子供の思考傾向と科目別理解度を永続化する。

### アーキテクチャ

```
┌─────────────────────────────────────────────────────────────────┐
│                    データ永続化層                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐  │
│  │    Firestore    │  │ ADK MemoryBank  │  │    BigQuery    │  │
│  │                 │  │                 │  │                │  │
│  │ • 構造化データ   │  │ • 自然言語記憶   │  │ • 分析用データ  │  │
│  │ • 理解度スコア   │  │ • 学習の気づき   │  │ • 長期トレンド  │  │
│  │ • 統計情報      │  │ • 個別アドバイス │  │ • コホート分析  │  │
│  └─────────────────┘  └─────────────────┘  └────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 役割分担

| ストレージ | 用途 | データ例 |
|-----------|------|----------|
| **Firestore** | 構造化データ、リアルタイム表示 | 理解度スコア、セッション統計 |
| **ADK MemoryBank** | LLMが参照する自然言語記憶 | 「繰り上がりで混乱しやすい」 |
| **BigQuery** | 分析・レポート | 週次トレンド、クラス全体の傾向 |

### Firestore スキーマ

```
children/{childId}
├── profile: {
│     name: string,
│     gradeLevel: number,
│     createdAt: timestamp
│   }
├── thinkingProfile: {
│     persistenceScore: number,      // 粘り強さ (0-10)
│     independenceScore: number,     // 自立性 (0-10)
│     reflectionQuality: number,     // 振り返り力 (0-10)
│     hintDependency: number,        // ヒント依存度 (0-1)
│     updatedAt: timestamp
│   }
├── subjectUnderstanding/{subjectId}
│   └── {
│         subject: string,           // "math", "japanese"
│         topic: string,             // "addition", "kanji_grade1"
│         level: number,             // 理解度 (0-10)
│         trend: string,             // "improving" | "stable" | "declining"
│         weakPoints: string[],      // ["繰り上がり", "文章題"]
│         strongPoints: string[],
│         assessedAt: timestamp
│       }
└── sessionSummaries/{sessionId}
    └── {
          date: timestamp,
          duration: number,          // 秒
          problemsAttempted: number,
          problemsSolvedIndependently: number,
          hintsUsed: number,
          subjectsCovered: string[],
          insights: string[]         // セッションからの気づき
        }
```

### ADK MemoryBank 記憶形式

```python
# LLMが参照する自然言語形式の記憶
memories = [
    {
        "memory_type": "learning_insight",
        "content": "たろうくんは足し算は得意だが、繰り上がりがある問題では混乱しやすい。",
        "created_at": "2026-02-02T10:30:00Z",
        "tags": ["math", "addition", "weakness"]
    },
    {
        "memory_type": "thinking_pattern",
        "content": "最初は諦めそうになるが、励ましの言葉で粘り強く取り組める。",
        "created_at": "2026-02-02T10:30:00Z",
        "tags": ["persistence", "encouragement"]
    },
    {
        "memory_type": "effective_approach",
        "content": "「前にやった問題を思い出してみよう」という声かけが効果的。",
        "created_at": "2026-02-02T10:30:00Z",
        "tags": ["hint_strategy"]
    }
]
```

### Pydantic モデル

```python
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ThinkingTendencies(BaseModel):
    """思考の傾向"""
    persistence_score: float = Field(..., ge=0, le=10, description="粘り強さ")
    independence_score: float = Field(..., ge=0, le=10, description="自立性")
    reflection_quality: float = Field(..., ge=0, le=10, description="振り返り力")
    hint_dependency: float = Field(..., ge=0, le=1, description="ヒント依存度")
    updated_at: datetime


class SubjectUnderstanding(BaseModel):
    """科目別理解度"""
    subject: str = Field(..., description="科目 (math, japanese, etc.)")
    topic: str = Field(..., description="単元 (addition, kanji_grade1, etc.)")
    level: float = Field(..., ge=0, le=10, description="理解度")
    trend: Literal["improving", "stable", "declining"] = Field(..., description="傾向")
    weak_points: list[str] = Field(default_factory=list, description="苦手ポイント")
    strong_points: list[str] = Field(default_factory=list, description="得意ポイント")
    assessed_at: datetime


class SessionSummary(BaseModel):
    """セッションサマリー"""
    session_id: str
    date: datetime
    duration_seconds: int
    problems_attempted: int
    problems_solved_independently: int
    hints_used: int
    subjects_covered: list[str]
    insights: list[str] = Field(default_factory=list, description="セッションからの気づき")


class ChildLearningProfile(BaseModel):
    """子供の学習プロファイル（Firestore永続化用）"""
    child_id: str
    thinking: ThinkingTendencies
    subjects: list[SubjectUnderstanding]
    total_sessions: int
    total_problems_solved: int
    created_at: datetime
    updated_at: datetime


class LearningMemory(BaseModel):
    """ADK MemoryBank用の記憶"""
    memory_type: Literal["learning_insight", "thinking_pattern", "effective_approach"]
    content: str = Field(..., description="自然言語での記憶内容")
    tags: list[str] = Field(default_factory=list, description="検索用タグ")
    created_at: datetime
```

### 更新タイミング

| イベント | 更新対象 |
|----------|----------|
| セッション終了 | SessionSummary (Firestore) |
| セッション終了 | ThinkingTendencies 再計算 |
| 問題完了 | SubjectUnderstanding 更新 |
| 重要な気づき発生 | LearningMemory (MemoryBank) |
| 日次バッチ | BigQuery へエクスポート |

### LearningProfileService

```python
class LearningProfileService:
    """学習プロファイル管理サービス"""

    def __init__(
        self,
        firestore_client: FirestoreClient,
        memory_bank: MemoryBankService,
    ):
        self._firestore = firestore_client
        self._memory_bank = memory_bank

    async def update_after_session(
        self,
        child_id: str,
        session_summary: SessionSummary,
        insights: list[str],
    ) -> None:
        """セッション終了後にプロファイルを更新"""
        # 1. SessionSummary を Firestore に保存
        # 2. ThinkingTendencies を再計算
        # 3. SubjectUnderstanding を更新
        # 4. 重要な気づきを MemoryBank に保存
        pass

    async def get_profile(self, child_id: str) -> ChildLearningProfile:
        """子供の学習プロファイルを取得"""
        pass

    async def get_memories_for_llm(self, child_id: str) -> list[LearningMemory]:
        """LLM用の記憶を取得（MemoryBankから）"""
        pass

    def calculate_thinking_tendencies(
        self,
        recent_sessions: list[SessionSummary],
    ) -> ThinkingTendencies:
        """直近セッションから思考傾向を計算"""
        pass
```

---

## テスト戦略

### ユニットテスト

- `SocraticDialogueManager`: 各メソッドの入出力テスト（プロンプト構築含む）
- `models.py`: Enum値、Pydanticモデルのバリデーション
- `LearningProfileService`: プロファイル更新ロジックのテスト

### 統合テスト

- 対話フロー全体のシナリオテスト
- ADK Agentとの統合テスト（InMemorySessionService使用）
- Firestore エミュレータを使った永続化テスト

### モック

- LLM呼び出しはモック化してテスト
- Firestore/MemoryBank はエミュレータまたはモック
- 決定的なテストを実現
