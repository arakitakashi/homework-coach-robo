# 宿題コーチロボット - エージェントアーキテクチャ設計書

**Document Version**: 1.0
**Last Updated**: 2026-02-08
**Status**: Phase 2 設計完了

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
| Agent Engine（マネージド） | ❌ 未使用 | Cloud Runに直接デプロイ |
| Vertex AI RAG | ❌ 未使用 | キーワード検索のみ |

### 1.2 現在のアーキテクチャ

```
FastAPI Endpoints
├── POST /api/v1/dialogue/run (SSE)
│   └── AgentRunnerService
│       └── Runner.run_async()
│           └── Router Agent (AutoFlow)
│               ├── Math Coach Agent (tools=[calculate, hint, curriculum, progress])
│               ├── Japanese Coach Agent (tools=[hint, curriculum, progress])
│               ├── Encouragement Agent (tools=[progress])
│               └── Review Agent (tools=[progress])
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
| キーワード検索のみ | 過去の学習履歴を活かせない | セマンティック検索なし |
| 感情認識なし | サポートレベルの適応が不十分 | Phase 2dで計画 |
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
│   ├── review.py             # Review Agent (1ツール)
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
│   └── image_analyzer.py     # analyze_image_tool
├── runner/
│   ├── agent.py              # create_socratic_agent()（音声用、レガシー）
│   └── runner_service.py     # AgentRunnerService（Router Agent使用）
├── sessions/
└── memory/
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
    ],
)
```

> **Note**: `search_memory_tool` は Phase 2c（Vertex AI RAG）で追加予定。

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

## 5. Phase 2c: Vertex AI RAG（セマンティック記憶）

### 5.1 概要

現在のキーワードベースの記憶検索を、Vertex AI RAG Engine を使用したセマンティック検索に置き換える。これにより、子供の過去の学習パターンを文脈的に検索し、個別化された学習体験を提供する。

### 5.2 記憶の種類

| 記憶タイプ | 保存先 | 用途 |
|-----------|-------|------|
| **対話履歴** | Vertex AI RAG Corpus | 過去の対話から関連する指導パターンを検索 |
| **苦手分野** | Firestore + RAG | 「繰り上がりで3回つまずいた」等のパターン |
| **成功体験** | Firestore + RAG | 「前回は自力で解けた」等のポジティブ記録 |
| **カリキュラム** | RAG Corpus | 学習指導要領、教科書の内容 |

### 5.3 アーキテクチャ

```
子供の発言
    │
    ▼
┌──────────────────┐
│ Vertex AI RAG    │
│ Engine           │
│                  │
│ ┌──────────────┐ │
│ │ Corpus:      │ │
│ │ - 対話履歴   │ │     ┌──────────────┐
│ │ - 苦手分野   │ │────▶│ 関連コンテキスト │
│ │ - 成功体験   │ │     │ をエージェント  │
│ │ - カリキュラム│ │     │ に注入          │
│ └──────────────┘ │     └──────────────┘
└──────────────────┘
```

### 5.4 RAGツール定義

```python
from google.adk.tools import VertexAiSearchTool

# Vertex AI RAG をツールとして統合
search_memory_tool = VertexAiSearchTool(
    data_store_id="homework-coach-memory-store",
    description="子供の過去の学習履歴や苦手分野を検索する",
)
```

### 5.5 記憶の保存フロー

```
セッション終了
    │
    ▼
┌──────────────────┐
│ add_session_to_  │
│ memory()         │
│                  │
│ 1. 対話要約生成  │
│ 2. 苦手分野抽出  │
│ 3. 成功体験抽出  │
│ 4. RAG Corpusに  │
│    インデクシング │
└──────────────────┘
```

### 5.6 個別化された対話の例

```
[子供]: 23 + 45 がわからない

[RAG検索結果]:
- 2日前: 繰り上がりの足し算で3回つまずいた
- 先週: 10の位の足し算は自力で解けた
- 苦手パターン: 一の位の繰り上がり時に10の位を忘れる

[エージェントの応答]:
「23 + 45 だね！前に10の位の足し算は得意だったよね。
 まず一の位から計算してみよう。3 + 5 はいくつかな？」
```

### 5.7 FirestoreMemoryServiceからの移行

| 機能 | 現在（Firestore） | Phase 2c（RAG） |
|------|-------------------|-----------------|
| 保存 | テキスト保存 | ベクトル埋め込み + テキスト |
| 検索 | キーワードマッチ | セマンティック類似度検索 |
| 言語 | 英語のみ | 日本語対応 |
| 精度 | 低（完全一致のみ） | 高（意味的な類似度） |

---

## 6. Phase 2d: 感情適応エージェント

### 6.1 概要

音声のトーン分析を行い、子供の感情状態を推定する。感情状態に基づいて、エージェントの対話トーンとサポートレベルを動的に調整する。

### 6.2 アーキテクチャ

```
音声入力（PCM 16kHz）
    │
    ├──▶ Gemini Live API（通常の対話処理）
    │
    └──▶ Emotion Analysis Agent
              │
              ▼
         ┌──────────────────┐
         │ 感情状態の推定     │
         │                  │
         │ - frustration    │
         │ - confidence     │
         │ - fatigue        │
         │ - excitement     │
         └────────┬─────────┘
                  │
                  ▼
         session.state["emotion"] に反映
                  │
                  ▼
         対話エージェントが参照して適応
```

### 6.3 感情分析の手法

#### 方法1: Gemini マルチモーダル分析（推奨）

Gemini Live APIの音声入力を分析エージェントにも共有し、テキスト内容と音声トーンの両方から感情を推定する。

```python
emotion_agent = Agent(
    name="emotion_analyzer",
    model="gemini-2.5-flash",
    instruction="""
    子供の発言内容と話し方から感情状態を分析してください。
    以下のスケールで評価:
    - frustration: 0.0-1.0（イライラ度）
    - confidence: 0.0-1.0（自信度）
    - fatigue: 0.0-1.0（疲労度）
    - excitement: 0.0-1.0（興奮度）

    分析結果は update_emotion ツールで記録してください。
    """,
    tools=[update_emotion_tool],
)
```

#### 方法2: Vertex AI AutoML（高精度、Phase 3以降）

カスタム音声感情認識モデルをVertex AI AutoMLでトレーニングする。

- 訓練データ: 児童の音声サンプル（同意取得済み）
- ラベル: 感情カテゴリ（ポジティブ/ニュートラル/ネガティブ/疲労）
- 推論: Vertex AI Prediction Endpointとして提供

### 6.4 適応ロジック

```python
# session.state に基づく適応
emotion = session.state.get("emotion", {})

if emotion.get("frustration", 0) > 0.7:
    # 高フラストレーション → 励ましエージェントに委譲
    transfer_to(encouragement_agent)

elif emotion.get("fatigue", 0) > 0.6:
    # 高疲労 → 休憩提案
    suggest_break()

elif emotion.get("confidence", 0) > 0.8:
    # 高自信 → 難易度を少し上げる
    increase_difficulty()
```

### 6.5 感情状態と対話トーンのマッピング

| 感情状態 | 対話トーン | speaking_rate | pitch | 例 |
|---------|-----------|--------------|-------|-----|
| 高フラストレーション | 優しく・ゆっくり | 0.8 | +1.0 | 「大丈夫だよ、ゆっくりやろう」 |
| 高自信 | 明るく・テンポよく | 1.1 | +3.0 | 「すごいね！もっと難しいのやる？」 |
| 高疲労 | 穏やかに | 0.85 | +1.5 | 「頑張ったね。少し休もうか」 |
| 高興奮 | 一緒に楽しむ | 1.05 | +2.5 | 「やったー！正解だよ！」 |

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

Phase 2c: Vertex AI RAG
├── Step 1: RAG Corpus作成 + インデクシング
├── Step 2: search_memory_tool統合
└── Step 3: FirestoreMemoryServiceからの移行

Phase 2d: 感情適応
├── Step 1: テキストベースの感情分析（Gemini）
├── Step 2: 感情→対話トーン適応ロジック
└── Step 3: 音声トーン分析の高度化

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
- **Phase 2c, 2d は並行可能**
- **Phase 3 は全Phase 2完了後**

### 8.3 優先度と推奨実装順序

| 順序 | フェーズ | 優先度 | 理由 |
|------|---------|-------|------|
| 1 | Phase 2a: ツール導入 | ✅ 完了 | 全フェーズの基盤。PR #59 で実装完了 |
| 2 | Phase 2b: マルチエージェント | ✅ 完了 | 教科最適化で学習効果が大幅向上。PR #69 で実装完了 |
| 3 | Phase 2c: RAG記憶 | 高 | 個別化学習の実現。長期利用の鍵 |
| 4 | Phase 2d: 感情適応 | 中 | UX向上。まずはテキストベースから開始可能 |
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
