# 宿題コーチロボット - エージェントアーキテクチャ設計書

**Document Version**: 1.0
**Last Updated**: 2026-02-09
**Status**: Phase 2d 実装完了

---

## 目次

1. [現状分析](#1-現状分析)
2. [目標アーキテクチャ](#2-目標アーキテクチャ)
3. [Phase 2a: ツール導入（Function Calling）](#3-phase-2a-ツール導入function-calling)
4. [Phase 2b: マルチエージェント構成](#4-phase-2b-マルチエージェント構成)
5. [Phase 2c: Vertex AI RAG（セマンティック記憶）](#5-phase-2c-vertex-ai-ragセマンティック記憶)
6. [Phase 2d: 感情適応エージェント](#6-phase-2d-感情適応エージェント)
7. [Phase 3: Vertex AI Agent Engine デプロイ](#7-phase-3-vertex-ai-agent-engine-デプロイ)
8. [実装ロードマップ](#8-実装ロードマップ)

---

## 1. 現状分析

### 1.1 MVP実装の状態

現在のMVP実装では、Google ADK（Agent Development Kit）を**最小限**の構成で使用している。

| ADK機能 | 利用状況 | 備考 |
|---------|---------|------|
| `Agent`（マルチ） | ✅ 使用中 | Router Agent + 4サブエージェント（Phase 2b完了） |
| `Runner.run_async()` | ✅ 使用中 | テキスト対話（SSE） |
| `Runner.run_live()` | ✅ 使用中 | 音声ストリーミング |
| `BaseSessionService` | ✅ 使用中 | Firestore永続化を自前実装 |
| `BaseMemoryService` | ✅ 使用中 | Firestore永続化を自前実装 |
| Tool / Function Calling | ✅ 使用中 | Phase 2a で5ツール導入 |
| マルチエージェント | ✅ 使用中 | Phase 2b で導入（AutoFlow委譲） |
| サブエージェント委譲 | ✅ 使用中 | Router → Math/Japanese/Encouragement/Review |
| Agent Engine（マネージド） | ✅ 準備済み | Agent Engine 作成スクリプト + Memory Bank 用 |
| VertexAiMemoryBankService | ✅ 準備済み | ファクトリパターンで切り替え（AGENT_ENGINE_ID） |

### 1.2 現在のアーキテクチャ

```
FastAPI Endpoints
├── POST /api/v1/dialogue/run (SSE)
│   └── AgentRunnerService
│       └── Runner.run_async()
│           └── Router Agent (AutoFlow, tools=[update_emotion])
│               ├── Math Coach Agent (tools=[calculate, hint, curriculum, progress])
│               ├── Japanese Coach Agent (tools=[hint, curriculum, progress])
│               ├── Encouragement Agent (tools=[progress])
│               └── Review Agent (tools=[progress, load_memory])
│
└── WebSocket /ws/{user_id}/{session_id}
    └── VoiceStreamingService
        ├── LiveRequestQueue (full-duplex)
        └── Runner.run_live()
            └── Socratic Agent (instruction-only, tools=[5ツール])
                └── Gemini Live 2.5 Flash (native audio)
```

### 1.3 現在の制約

| 制約 | 影響 | 原因 |
|------|------|------|
| ~~ツールなし~~ | ~~計算検証が不正確（LLMの幻覚リスク）~~ | ✅ Phase 2a で解決 |
| ~~単一エージェント~~ | ~~教科ごとの最適化不可~~ | ✅ Phase 2b で解決（Router + 4サブエージェント） |
| ~~キーワード検索のみ~~ | ~~過去の学習履歴を活かせない~~ | ✅ Phase 2c で解決（VertexAiMemoryBankService + load_memory） |
| ~~感情認識なし~~ | ~~サポートレベルの適応が不十分~~ | ✅ Phase 2d で解決（update_emotion_tool + 感情ベースルーティング） |
| ~~プロンプト依存~~ | ~~ヒント段階の管理が不確実~~ | ✅ Phase 2a で解決（manage_hint_tool） |

---

## 2. 目標アーキテクチャ

### 2.1 全体像

```
                        ┌─────────────────────────────────────┐
                        │     Vertex AI Agent Engine           │
                        │     (マネージドデプロイ - Phase 3)     │
                        └─────────────────────────────────────┘
                                         │
                        ┌────────────────┼────────────────┐
                        │                │                │
                   ┌────▼────┐    ┌──────▼──────┐   ┌────▼────┐
                   │ Router  │    │  Emotion    │   │ Review  │
                   │ Agent   │    │  Agent      │   │ Agent   │
                   └────┬────┘    └──────┬──────┘   └────┬────┘
                        │                │                │
          ┌─────────────┼────────┐       │                │
          │             │        │       │                │
     ┌────▼────┐  ┌────▼────┐  ┌▼───────▼──┐       ┌────▼────┐
     │  Math   │  │Japanese │  │Encourage- │       │Progress │
     │  Coach  │  │ Coach   │  │ment Agent │       │ Report  │
     │  Agent  │  │ Agent   │  └───────────┘       │ Agent   │
     └────┬────┘  └────┬────┘                      └────┬────┘
          │             │                                │
     ┌────▼────────────▼────────────────────────────────▼────┐
     │                      Tools Layer                       │
     ├─────────┬──────────┬───────────┬──────────┬───────────┤
     │calculate│curriculum│  record   │ analyze  │  search   │
     │ _tool   │  _tool   │_progress  │ _image   │ _memory   │
     │         │          │  _tool    │  _tool   │  _tool    │
     └────┬────┴────┬─────┴────┬──────┴────┬─────┴────┬──────┘
          │         │          │           │          │
     ┌────▼────┐ ┌──▼───┐ ┌───▼────┐ ┌────▼───┐ ┌───▼──────┐
     │ Python  │ │Fire- │ │Fire-   │ │Vision  │ │Vertex AI │
     │ stdlib  │ │store │ │store+  │ │API     │ │RAG       │
     │         │ │      │ │BigQuery│ │        │ │          │
     └─────────┘ └──────┘ └────────┘ └────────┘ └──────────┘
```

### 2.2 設計原則

1. **段階的導入**: 各フェーズは独立してデプロイ可能
2. **後方互換性**: 既存のSSE/WebSocketエンドポイントは維持
3. **テスト駆動**: 各ツール・エージェントにユニットテスト必須
4. **フォールバック**: ツール呼び出し失敗時はプロンプトベースにフォールバック

---

## 3. Phase 2a: ツール導入（Function Calling）✅ 実装完了

### 3.1 概要

~~現在プロンプトのみで実現している機能を~~ ADK Toolとして切り出し済み。LLMの幻覚リスクを排除し、確実な動作を保証する。

> **Status**: PR #59 で実装完了。5ツール（70テスト、カバレッジ88%）。

### 3.2 ツール一覧

#### 3.2.1 `calculate_tool` — 計算検証ツール

**目的**: 子供の回答の正誤を確実に検証する（LLMの計算ミスを防止）

```python
from google.adk.tools import FunctionTool

def calculate_and_verify(
    expression: str,
    child_answer: str,
    grade_level: int,
) -> dict:
    """
    算数の計算を検証し、結果を返す。

    Args:
        expression: 数式（例: "23 + 45"）
        child_answer: 子供の回答（例: "68"）
        grade_level: 学年（1-3）

    Returns:
        dict: {
            "correct_answer": str,
            "is_correct": bool,
            "error_type": str | None,  # "calculation", "unit", "misread" etc.
            "hint": str  # 間違いの傾向に基づくヒント
        }
    """
    ...

calculate_tool = FunctionTool(func=calculate_and_verify)
```

**対応する問題タイプ**:
- 足し算・引き算（繰り上がり・繰り下がり含む）
- 掛け算（九九）
- 割り算（余りあり）
- 文章題の数式変換

#### 3.2.2 `manage_hint_tool` — ヒント段階管理ツール

**目的**: 3段階ヒントシステムの状態を確実に管理する（プロンプト依存からの脱却）

```python
def manage_hint(
    session_id: str,
    action: str,  # "get_current", "advance", "reset"
    problem_id: str | None = None,
) -> dict:
    """
    ヒント段階を管理する。

    Returns:
        dict: {
            "current_level": int,  # 0-3 (0=未使用)
            "max_level": 3,
            "hint_template": str,  # 現在のレベルに対応するヒントテンプレート
            "can_advance": bool,
            "hints_used_total": int
        }
    """
    ...
```

**状態管理**: ADK SessionServiceの`session.state`に`hint_level`を保存。プロンプトではなくツール経由でのみ段階が遷移する。

#### 3.2.3 `check_curriculum_tool` — カリキュラム参照ツール

**目的**: 学年・教科に応じた適切な指導内容を参照する

```python
def check_curriculum(
    grade_level: int,
    subject: str,  # "math", "japanese", "science"
    topic: str,    # "addition_carry", "kanji_grade2", etc.
) -> dict:
    """
    カリキュラム情報を参照する。

    Returns:
        dict: {
            "prerequisites": list[str],  # 前提知識
            "learning_objectives": list[str],  # 学習目標
            "common_mistakes": list[str],  # よくある間違い
            "teaching_strategies": list[str],  # 指導戦略
            "related_topics": list[str]  # 関連トピック
        }
    """
    ...
```

**データソース**: Phase 2a ではインメモリ静的辞書で実装。Phase 2c以降でFirestoreに移行予定。

#### 3.2.4 `record_progress_tool` — 学習進捗記録ツール

**目的**: 学習プロセスのポイント付与と進捗記録を確実に行う

```python
def record_progress(
    user_id: str,
    session_id: str,
    problem_id: str,
    outcome: str,  # "self_solved", "hint_solved", "guided_solved"
    hints_used: int,
    time_spent_seconds: int,
) -> dict:
    """
    学習進捗を記録し、ポイントを付与する。

    Returns:
        dict: {
            "points_earned": int,  # 1-3
            "total_points": int,
            "streak": int,  # 連続正解数
            "achievement_unlocked": str | None,  # 新しい称号
            "encouragement_message": str
        }
    """
    ...
```

**ポイントシステム**:
| アウトカム | ポイント | 説明 |
|-----------|---------|------|
| `self_solved` | 3 | 自分で気づいた |
| `hint_solved` | 2 | ヒントで気づいた |
| `guided_solved` | 1 | 一緒に解いた |

#### 3.2.5 `analyze_image_tool` — 宿題画像分析ツール

**目的**: 宿題の写真から問題文を読み取り、構造化データに変換する

```python
def analyze_homework_image(
    image_data: str,  # base64 encoded
    expected_subject: str | None = None,
) -> dict:
    """
    宿題の画像を分析して問題を抽出する。

    Returns:
        dict: {
            "problems": list[{
                "text": str,
                "type": str,  # "arithmetic", "word_problem", "kanji", etc.
                "difficulty": int,
                "expression": str | None  # 数式がある場合
            }],
            "confidence": float,
            "needs_confirmation": bool
        }
    """
    ...
```

**使用API**: Gemini Vision API（プライマリ）+ Cloud Vision API（OCRフォールバック）

### 3.3 エージェント定義（Phase 2b でマルチエージェントに移行済み）

```python
# Phase 2a 時点の定義（現在は agents/router.py の Router Agent に置き換え済み）
# runner/agent.py - create_socratic_agent() は音声ストリーミング用に残存
agent = Agent(
    name="socratic_dialogue_agent",
    model="gemini-2.5-flash",
    instruction=SOCRATIC_SYSTEM_PROMPT,  # ツール使用ガイダンス含む
    tools=[
        calculate_tool,
        manage_hint_tool,
        check_curriculum_tool,
        record_progress_tool,
        analyze_image_tool,
    ],
)
```

> **Note**: テキスト対話（SSE）は Phase 2b で Router Agent に移行。音声ストリーミング（WebSocket）は引き続き単一エージェントを使用。

### 3.4 ファイル構成

```
backend/app/services/adk/
├── agents/                   # ✅ Phase 2b 実装済み
│   ├── __init__.py
│   ├── router.py             # Router Agent (AutoFlow → sub_agents)
│   ├── math_coach.py         # Math Coach Agent (4ツール)
│   ├── japanese_coach.py     # Japanese Coach Agent (3ツール)
│   ├── encouragement.py      # Encouragement Agent (1ツール)
│   ├── review.py             # Review Agent (2ツール: progress + load_memory)
│   └── prompts/
│       ├── __init__.py
│       ├── router.py
│       ├── math_coach.py
│       ├── japanese_coach.py
│       ├── encouragement.py
│       └── review.py
├── tools/                    # ✅ Phase 2a 実装済み
│   ├── __init__.py
│   ├── calculate.py          # calculate_tool
│   ├── hint_manager.py       # manage_hint_tool
│   ├── curriculum.py         # check_curriculum_tool
│   ├── progress_recorder.py  # record_progress_tool
│   ├── image_analyzer.py     # analyze_image_tool
│   └── emotion_analyzer.py   # ✅ Phase 2d: update_emotion_tool
├── runner/
│   ├── agent.py              # create_socratic_agent()（音声用、レガシー）
│   └── runner_service.py     # AgentRunnerService（Router Agent使用）
├── sessions/
└── memory/
    ├── __init__.py
    ├── converters.py
    ├── firestore_memory_service.py
    └── memory_factory.py         # ✅ Phase 2c: メモリサービスファクトリ
```

### 3.5 テスト戦略

各ツールに対して:
1. **ユニットテスト**: ツール関数単体の入出力検証
2. **統合テスト**: エージェントがツールを正しく呼び出すか検証
3. **E2Eテスト**: 子供の対話シナリオでツールが適切に使われるか検証

---

## 4. Phase 2b: マルチエージェント構成 ✅ 実装完了

### 4.1 概要

単一のソクラテスエージェントを、教科・役割ごとに特化した複数エージェントに分離。ルーターエージェントが子供の入力を分析し、ADK AutoFlow で最適なエージェントに委譲する。

> **Status**: PR #69 で実装完了。5エージェント（72テスト、カバレッジ100%）。

### 4.2 エージェント構成

```
Router Agent（振り分け）
├── Math Coach Agent      # 算数専門コーチ
├── Japanese Coach Agent  # 国語専門コーチ
├── Encouragement Agent   # 励まし・休憩提案
└── Review Agent          # 復習・振り返り
```

#### 4.2.1 Router Agent（ルーターエージェント）

**役割**: 子供の入力を分析し、適切な専門エージェントに委譲する。

```python
from google.adk.agents import Agent

router_agent = Agent(
    name="router_agent",
    model="gemini-2.5-flash",
    instruction="""
    あなたは子供の宿題を手伝うロボットチームのリーダーです。
    子供の発言を分析して、最適な専門家に繋ぎます。

    判断基準:
    - 算数の問題 → math_coach に委譲
    - 国語の問題（漢字、読解、作文）→ japanese_coach に委譲
    - 「疲れた」「わからない」「やめたい」→ encouragement_agent に委譲
    - 「今日やったこと」「振り返り」→ review_agent に委譲
    - 判断が難しい場合は子供に確認する
    """,
    sub_agents=[
        math_coach_agent,
        japanese_coach_agent,
        encouragement_agent,
        review_agent,
    ],
)
```

#### 4.2.2 Math Coach Agent（算数コーチ）

**役割**: 算数に特化したソクラテス式対話

```python
math_coach_agent = Agent(
    name="math_coach",
    model="gemini-2.5-flash",
    instruction=MATH_COACH_PROMPT,  # 算数専用プロンプト
    tools=[
        calculate_tool,
        manage_hint_tool,
        check_curriculum_tool,
        record_progress_tool,
    ],
)
```

**特化ポイント**:
- 繰り上がり・繰り下がりの段階的指導
- 九九の暗記支援（リズム、語呂合わせ）
- 文章題の「何を求めているか」分析

#### 4.2.3 Japanese Coach Agent（国語コーチ）

**役割**: 国語に特化したソクラテス式対話

```python
japanese_coach_agent = Agent(
    name="japanese_coach",
    model="gemini-2.5-flash",
    instruction=JAPANESE_COACH_PROMPT,  # 国語専用プロンプト
    tools=[
        manage_hint_tool,
        check_curriculum_tool,
        record_progress_tool,
    ],
)
```

> **Note**: 国語専用ツール（`kanji_lookup_tool`, `reading_comprehension_tool`）は将来のフェーズで追加予定。現在はLLMのプロンプトベースで対応。

**特化ポイント**:
- 漢字の書き順・部首の指導
- 読解問題の「何が聞かれているか」分析
- 作文の構成支援（はじめ・なか・おわり）

#### 4.2.4 Encouragement Agent（励ましエージェント）

**役割**: 感情サポートと休憩提案

```python
encouragement_agent = Agent(
    name="encouragement_agent",
    model="gemini-2.5-flash",
    instruction=ENCOURAGEMENT_PROMPT,
    tools=[
        record_progress_tool,  # 今日の頑張りを振り返る
    ],
)
```

**トリガー条件**:
- フラストレーションレベルが高い
- 同じ問題で3回以上つまずいている
- 「疲れた」「もうやだ」等のネガティブ発言
- 連続15分以上の利用

**対応パターン**:
| 状況 | 対応 |
|------|------|
| イライラ | 「難しいよね。でも○○はもう3問も解けたんだよ！」 |
| 疲れ | 「ちょっと休憩しない？水を飲んできてもいいよ」 |
| 自信喪失 | 「前は△△も難しかったけど、今はできるようになったよね」 |
| 飽き | ミニゲーム提案（計算バトル等） |

#### 4.2.5 Review Agent（振り返りエージェント）

**役割**: セッション終了時の振り返りと保護者レポート生成

```python
review_agent = Agent(
    name="review_agent",
    model="gemini-2.5-flash",
    instruction=REVIEW_PROMPT,
    tools=[
        record_progress_tool,
        load_memory,  # ADK 組み込みツール（Phase 2c で追加）
    ],
)
```

> **Note**: `load_memory` は ADK 組み込みのメモリ検索ツール。Phase 2c で追加済み。

**機能**:
- 今日のセッションの要約（何を頑張ったか）
- 苦手分野の特定と次回の学習提案
- 保護者向けレポートの生成（テキスト/JSON）

### 4.3 エージェント間の状態共有

ADK SessionServiceの`session.state`を活用して、エージェント間で状態を共有する。

```python
# session.state の構造
{
    # ルーター状態
    "current_agent": "math_coach",
    "agent_switch_count": 2,

    # 共通状態
    "hint_level": 1,
    "current_problem_id": "prob_123",
    "frustration_level": 0.3,  # 0.0-1.0

    # 進捗状態
    "problems_attempted": 5,
    "problems_solved": 3,
    "total_points": 12,
    "session_start_time": "2026-02-08T15:00:00Z",
}
```

### 4.4 ファイル構成

```
backend/app/services/adk/
├── agents/
│   ├── __init__.py
│   ├── router.py             # Router Agent
│   ├── math_coach.py         # Math Coach Agent
│   ├── japanese_coach.py     # Japanese Coach Agent
│   ├── encouragement.py      # Encouragement Agent
│   ├── review.py             # Review Agent
│   └── prompts/
│       ├── router.py
│       ├── math_coach.py
│       ├── japanese_coach.py
│       ├── encouragement.py
│       └── review.py
├── tools/
├── runner/
├── sessions/
└── memory/
```

---

## 5. Phase 2c: Vertex AI Memory Bank（セマンティック記憶）✅ 実装完了

### 5.1 概要

現在のキーワードベースの記憶検索を、ADK 公式の `VertexAiMemoryBankService` を使用したセマンティック検索に置き換える。Memory Bank は LLM による事実抽出（Fact Extraction）+ セマンティック検索を提供し、対話履歴から自動的に「事実」を抽出・保存する。

> **Status**: PR #73 で実装完了。ファクトリパターン + Agent Engine 作成スクリプト + load_memory ツール。

### 5.2 VertexAiMemoryBankService vs FirestoreMemoryService

| 機能 | FirestoreMemoryService（フォールバック） | VertexAiMemoryBankService（推奨） |
|------|----------------------------------------|----------------------------------|
| 保存 | テキストをそのまま保存 | LLM が事実（Fact）を自動抽出して保存 |
| 検索 | キーワードマッチ（英語のみ） | セマンティック類似度検索（日本語対応） |
| 精度 | 低（完全一致のみ） | 高（意味的な類似度） |
| 依存 | Firestore のみ | Agent Engine + Memory Bank |

### 5.3 アーキテクチャ

```
セッション完了
    │
    ▼
┌──────────────────────────────┐
│ VertexAiMemoryBankService    │
│ .add_session_to_memory()     │
│                              │
│ 1. セッション events を送信  │
│ 2. LLM が事実を自動抽出     │
│    - 「繰り上がりで3回つまずいた」 │
│    - 「九九の7の段が苦手」     │
│    - 「前回は自力で解けた」    │
│ 3. Memory Bank に保存        │
└──────────────────────────────┘

エージェント対話中
    │
    ▼
┌──────────────────────────────┐
│ load_memory ツール (ADK組み込み) │
│                              │
│ - 過去の学習履歴を検索       │
│ - セマンティック類似度で     │
│   関連する事実を取得         │
│ - エージェントが参照して     │
│   個別化された対話を生成     │
└──────────────────────────────┘
```

### 5.4 メモリサービスファクトリ

```python
# memory_factory.py
def create_memory_service() -> BaseMemoryService:
    agent_engine_id = os.environ.get("AGENT_ENGINE_ID", "").strip()
    if not agent_engine_id:
        return FirestoreMemoryService()  # フォールバック
    from google.adk.memory import VertexAiMemoryBankService
    return VertexAiMemoryBankService(
        agent_engine_id=agent_engine_id,
        project=os.environ.get("GCP_PROJECT_ID") or None,
        location=os.environ.get("GCP_LOCATION") or None,
    )
```

### 5.5 load_memory ツール（ADK 組み込み）

Review Agent に ADK 組み込みの `load_memory` ツールを追加。エージェントが明示的に過去の学習履歴を検索できる。

```python
from google.adk.tools import load_memory

review_agent = Agent(
    name="review_agent",
    tools=[record_progress_tool, load_memory],
)
```

### 5.6 Agent Engine 作成

Memory Bank は Agent Engine を前提とするため、Agent Engine 作成スクリプトを提供。

```bash
uv run python scripts/create_agent_engine.py --project <project-id> --location us-central1
# → export AGENT_ENGINE_ID=<出力された ID>
```

### 5.7 個別化された対話の例

```
[子供]: 23 + 45 がわからない

[load_memory 検索結果]:
- 2日前: 繰り上がりの足し算で3回つまずいた
- 先週: 10の位の足し算は自力で解けた
- 苦手パターン: 一の位の繰り上がり時に10の位を忘れる

[エージェントの応答]:
「23 + 45 だね！前に10の位の足し算は得意だったよね。
 まず一の位から計算してみよう。3 + 5 はいくつかな？」
```

### 5.8 環境変数

| 変数名 | 必須 | 説明 |
|--------|------|------|
| `AGENT_ENGINE_ID` | 任意 | Agent Engine ID（設定時 Memory Bank 有効化） |
| `GCP_PROJECT_ID` | 任意 | GCP プロジェクト ID |
| `GCP_LOCATION` | 任意 | GCP ロケーション |

---

## 6. Phase 2d: 感情適応 ✅ 実装完了

### 6.1 概要

Router Agent が毎ターン子供の発言内容から感情状態を分析し、`session.state["emotion"]` に記録する。感情状態に基づいて、エージェントの対話トーンとサポートレベルを動的に調整する。

> **Status**: PR #75 で実装完了。update_emotion_tool + Router Agent 感情ベースルーティング + サブエージェント感情コンテキスト参照。

### 6.2 設計判断: Router Agent + ツール方式

感情分析の方式として「別の Emotion Agent を追加」ではなく「Router Agent にツールを追加」を採用。

| 方式 | メリット | デメリット |
|------|---------|----------|
| 別 Emotion Agent | 関心の分離 | 追加の LLM コール（レイテンシ増大） |
| **Router Agent + ツール（採用）** | レイテンシなし、Router が直接感情を判断 | Router の責務増加 |

Router は全メッセージを最初に処理するため、感情分析も同時に行うのが最も効率的。

### 6.3 アーキテクチャ

```
子供の発言
    │
    ▼
Router Agent
    │
    ├── 1. update_emotion ツール呼び出し
    │       └── session.state["emotion"] に記録
    │           ├── frustration, confidence, fatigue, excitement
    │           ├── primary_emotion
    │           ├── support_level (intensive/moderate/minimal)
    │           └── action_recommended (continue/encourage/rest)
    │
    ├── 2. 感情ベースルーティング（内容より優先）
    │       ├── frustration > 0.7 → encouragement_agent
    │       └── fatigue > 0.6 → encouragement_agent（休憩提案）
    │
    └── 3. 内容ベースルーティング（通常）
            ├── 算数 → math_coach
            ├── 国語 → japanese_coach
            └── 振り返り → review_agent
```

### 6.4 update_emotion_tool

```python
from google.adk.tools import FunctionTool

def update_emotion(
    frustration: float,      # 0.0-1.0（範囲外はクランプ）
    confidence: float,       # 0.0-1.0
    fatigue: float,          # 0.0-1.0
    excitement: float,       # 0.0-1.0
    primary_emotion: str,    # frustrated/confident/confused/happy/tired/neutral
    tool_context: Any = None,
) -> dict[str, object]:
    """感情スコアを session.state["emotion"] に記録する。"""
    ...

update_emotion_tool = FunctionTool(func=update_emotion)
```

**サポートレベル計算:**

| 条件 | support_level |
|------|--------------|
| frustration > 0.7 OR fatigue > 0.6 | intensive |
| frustration > 0.4 OR fatigue > 0.3 | moderate |
| それ以外 | minimal |

**アクション推奨:**

| 条件 | action_recommended |
|------|-------------------|
| fatigue > 0.6（優先） | rest |
| frustration > 0.7 | encourage |
| それ以外 | continue |

### 6.5 サブエージェントの感情コンテキスト参照

各サブエージェントのプロンプトに「感情への配慮」セクションを追加。`session.state["emotion"]` を参照して対応を調整する。

| エージェント | 感情対応 |
|-------------|---------|
| Math Coach | 高frustration → 小さいステップ、高confidence → チャレンジ促進、高fatigue → 短い問題 |
| Japanese Coach | 高frustration → やさしくゆっくり、高confidence → 応用問題、高fatigue → 無理させない |
| Encouragement | 高frustration → 気持ち受容＋成功体験、高fatigue → 休憩提案、confused → 安心させる |

### 6.6 感情状態と対話トーンのマッピング（将来拡張）

音声ストリーミング（TTS）での対話トーン調整は将来フェーズで実装予定。

| 感情状態 | 対話トーン | speaking_rate | pitch | 例 |
|---------|-----------|--------------|-------|-----|
| 高フラストレーション | 優しく・ゆっくり | 0.8 | +1.0 | 「大丈夫だよ、ゆっくりやろう」 |
| 高自信 | 明るく・テンポよく | 1.1 | +3.0 | 「すごいね！もっと難しいのやる？」 |
| 高疲労 | 穏やかに | 0.85 | +1.5 | 「頑張ったね。少し休もうか」 |
| 高興奮 | 一緒に楽しむ | 1.05 | +2.5 | 「やったー！正解だよ！」 |

### 6.7 将来の高度化（Phase 3以降）

- **Vertex AI AutoML**: カスタム音声感情認識モデル（児童の音声サンプル + ラベル）
- **TTS パラメータ連動**: speaking_rate / pitch を感情に応じて動的調整
- **感情履歴分析**: セッション全体の感情推移を記録・分析

---

## 7. Phase 3: Vertex AI Agent Engine デプロイ

### 7.1 概要

現在Cloud Runに直接デプロイしているADKエージェントを、Vertex AI Agent Engineに移行する。これにより、マネージドインフラ、組み込みのセッション管理、モニタリング、A/Bテストなどの機能を活用する。

### 7.2 Agent Engine のメリット

| 機能 | Cloud Run（現在） | Agent Engine |
|------|-------------------|-------------|
| インフラ管理 | 自前（Terraform） | マネージド |
| セッション管理 | 自前（FirestoreSessionService） | 組み込み |
| スケーリング | Cloud Run Auto-scaling | 自動最適化 |
| モニタリング | Cloud Logging/Monitoring | 専用ダッシュボード |
| A/Bテスト | 自前実装必要 | 組み込み |
| エージェント評価 | 手動 | 自動評価ツール |

### 7.3 移行手順

```
Step 1: Agent Engine にエージェントをデプロイ
        └── agent.py をそのまま使用可能

Step 2: セッション管理を Agent Engine に移行
        └── FirestoreSessionService → Agent Engine 組み込み

Step 3: APIエンドポイントの更新
        └── Cloud Run → Agent Engine エンドポイント

Step 4: フロントエンドの接続先更新
        └── WebSocket URL の変更

Step 5: Cloud Run のエージェント関連サービスを削除
```

### 7.4 A/Bテスト活用例

| テスト項目 | バリアントA | バリアントB | 評価指標 |
|-----------|-----------|-----------|---------|
| プロンプト | 現行プロンプト | 改善プロンプト | 自力解決率 |
| ヒント戦略 | 3段階固定 | 適応的段階 | 学習継続率 |
| エージェント構成 | 単一 | マルチ | 教科別正答率 |
| 励まし頻度 | 毎回 | 適応的 | セッション時間 |

### 7.5 デプロイ構成

```python
from google.adk.agents import Agent
from vertexai.agents.engines import AgentEngine

# Agent Engine にデプロイ
engine = AgentEngine.create(
    agent=router_agent,  # マルチエージェント構成
    display_name="homework-coach-agent",
    description="小学校低学年向けソクラテス式対話コーチ",
)

# エンドポイント取得
endpoint = engine.resource_name
```

---

## 8. 実装ロードマップ

### 8.1 フェーズ別スケジュール

```
Phase 2a: ツール導入
├── Step 1: calculate_tool + manage_hint_tool（コア）
├── Step 2: record_progress_tool（進捗記録）
├── Step 3: check_curriculum_tool（カリキュラム参照）
└── Step 4: analyze_image_tool（画像認識）

Phase 2b: マルチエージェント
├── Step 1: Router Agent + Math Coach Agent
├── Step 2: Japanese Coach Agent
├── Step 3: Encouragement Agent
└── Step 4: Review Agent

Phase 2c: Memory Bank (✅ 完了)
├── Step 1: memory_factory + VertexAiMemoryBankService 切り替え
├── Step 2: Review Agent に load_memory ツール追加
└── Step 3: Agent Engine 作成スクリプト

Phase 2d: 感情適応 (✅ 完了)
├── Step 1: update_emotion_tool（感情スコア記録 + support_level/action 計算）
├── Step 2: Router Agent 感情ベースルーティング
└── Step 3: サブエージェントプロンプト感情コンテキスト参照

Phase 3: Agent Engine
├── Step 1: Agent Engine へのデプロイ
├── Step 2: セッション管理の移行
└── Step 3: A/Bテスト環境の構築
```

### 8.2 依存関係

```
Phase 2a（ツール）──▶ Phase 2b（マルチエージェント）
                           │
Phase 2c（RAG）────────────┤
                           │
Phase 2d（感情）───────────┘
                           │
                           ▼
                    Phase 3（Agent Engine）
```

- **Phase 2a は実装完了** ✅（他の全フェーズの基盤）
- **Phase 2b は実装完了** ✅（Router Agent + 4サブエージェント）
- **Phase 2c は実装完了** ✅（Memory Bank ファクトリ + Agent Engine + load_memory）
- **Phase 2d は実装完了** ✅（update_emotion_tool + 感情ベースルーティング + サブエージェントプロンプト更新）
- **フロントエンド Phase 2 型定義・状態管理基盤** ✅（Phase 2a-2d 全サブフェーズの型定義25型 + Jotai atoms 12個。PR #60）
- **Phase 3 は Phase 2c の Agent Engine 基盤を活用**

### 8.3 優先度と推奨実装順序

| 順序 | フェーズ | 優先度 | 理由 |
|------|---------|-------|------|
| 1 | Phase 2a: ツール導入 | ✅ 完了 | 全フェーズの基盤。PR #59 で実装完了 |
| 2 | Phase 2b: マルチエージェント | ✅ 完了 | 教科最適化で学習効果が大幅向上。PR #69 で実装完了 |
| 3 | Phase 2c: Memory Bank | ✅ 完了 | VertexAiMemoryBankService + Agent Engine。PR #73 で実装完了 |
| 4 | Phase 2d: 感情適応 | ✅ 完了 | update_emotion_tool + 感情ベースルーティング。PR #75 で実装完了 |
| 5 | Phase 3: Agent Engine | 中 | 運用改善。Phase 2が安定してから移行 |

---

## 付録

### A. ADK バージョン要件

| パッケージ | 最小バージョン | 用途 |
|-----------|-------------|------|
| `google-adk` | ≥1.23.0 | Agent, Runner, Tools |
| `google-genai` | ≥1.0.0 | Gemini API types |
| `google-cloud-aiplatform` | ≥1.60.0 | Vertex AI RAG, Agent Engine |

### B. 参考資料

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [ADK Tools Guide](https://google.github.io/adk-docs/tools/)
- [ADK Multi-Agent Systems](https://google.github.io/adk-docs/agents/multi-agents/)
- [Vertex AI RAG Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-overview)
- [Vertex AI Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)

### C. 用語集

| 用語 | 説明 |
|------|------|
| **ADK** | Agent Development Kit。Googleのエージェント開発フレームワーク |
| **Function Calling** | LLMが外部関数を呼び出す機能 |
| **RAG** | Retrieval-Augmented Generation。検索で補強された生成 |
| **Agent Engine** | Vertex AIのマネージドエージェント実行環境 |
| **Router Agent** | 入力を分析して適切なサブエージェントに振り分けるエージェント |
| **Sub-Agent** | ルーターエージェントから委譲を受ける専門エージェント |
