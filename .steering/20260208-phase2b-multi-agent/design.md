# Design - Phase 2b: マルチエージェント構成

## アーキテクチャ概要

```
Router Agent（振り分け）
├── Math Coach Agent      # 算数専門コーチ（tools: calculate, hint, curriculum, progress）
├── Japanese Coach Agent  # 国語専門コーチ（tools: hint, curriculum, progress）
├── Encouragement Agent   # 励まし・休憩提案（tools: progress）
└── Review Agent          # 復習・振り返り（tools: progress）
```

ADK の `sub_agents` + AutoFlow パターンを使用。Router Agent の LLM が `transfer_to_agent(agent_name='...')` を自動生成し、フレームワークが実行フォーカスを切り替える。

## 技術選定

| 技術 | 選定理由 |
|------|---------|
| ADK `Agent` + `sub_agents` | ADK標準のマルチエージェントパターン。LLM駆動委譲が自動 |
| AutoFlow（デフォルト） | `sub_agents` 設定時にデフォルトで有効。明示的なルーティングロジック不要 |
| 既存ツール再利用 | Phase 2a の5ツールをエージェント別に割り振り |

## データ設計

### session.state の拡張

既存の session.state に以下を追加（エージェント間で共有）：

```python
session.state = {
    # 既存（Phase 2a）
    "hint_level": int,            # 0-3
    "current_problem_id": str,
    "problems_attempted": int,
    "problems_solved": int,
    "total_points": int,

    # Phase 2b 追加
    "current_subject": str,       # "math", "japanese", "general"
}
```

**注意**: `current_agent` の追跡は ADK フレームワークが内部的に管理するため、手動管理は不要。

## ファイル構成

```
backend/app/services/adk/
├── agents/                       # NEW
│   ├── __init__.py               # エージェントファクトリのエクスポート
│   ├── router.py                 # create_router_agent()
│   ├── math_coach.py             # create_math_coach_agent()
│   ├── japanese_coach.py         # create_japanese_coach_agent()
│   ├── encouragement.py          # create_encouragement_agent()
│   ├── review.py                 # create_review_agent()
│   └── prompts/                  # エージェント別プロンプト
│       ├── __init__.py
│       ├── router.py             # ROUTER_SYSTEM_PROMPT
│       ├── math_coach.py         # MATH_COACH_SYSTEM_PROMPT
│       ├── japanese_coach.py     # JAPANESE_COACH_SYSTEM_PROMPT
│       ├── encouragement.py      # ENCOURAGEMENT_SYSTEM_PROMPT
│       └── review.py             # REVIEW_SYSTEM_PROMPT
├── runner/
│   ├── agent.py                  # MODIFY: create_router_agent を使用するように変更
│   └── runner_service.py         # MODIFY: Router Agent を使用
├── tools/                        # 既存（変更なし）
├── sessions/                     # 既存（変更なし）
└── memory/                       # 既存（変更なし）
```

## 各エージェントの設計

### Router Agent

```python
def create_router_agent(model: str | None = None) -> Agent:
    return Agent(
        name="router_agent",
        model=model or DEFAULT_MODEL,
        instruction=ROUTER_SYSTEM_PROMPT,
        description="子供の宿題を手伝うロボットチームのリーダー。入力を分析して最適な専門コーチに繋ぐ。",
        sub_agents=[
            create_math_coach_agent(model),
            create_japanese_coach_agent(model),
            create_encouragement_agent(model),
            create_review_agent(model),
        ],
    )
```

- **ツール**: なし（ルーティングのみ）
- **sub_agents**: 全4つのサブエージェント
- **AutoFlow**: LLM が入力内容に基づき `transfer_to_agent` を自動生成

### Math Coach Agent

```python
def create_math_coach_agent(model: str | None = None) -> Agent:
    return Agent(
        name="math_coach",
        model=model or DEFAULT_MODEL,
        instruction=MATH_COACH_SYSTEM_PROMPT,
        description="算数の問題を解く手助けをする専門コーチ。計算、文章題、図形などに対応。",
        tools=[calculate_tool, manage_hint_tool, check_curriculum_tool, record_progress_tool],
    )
```

### Japanese Coach Agent

```python
def create_japanese_coach_agent(model: str | None = None) -> Agent:
    return Agent(
        name="japanese_coach",
        model=model or DEFAULT_MODEL,
        instruction=JAPANESE_COACH_SYSTEM_PROMPT,
        description="国語の問題を解く手助けをする専門コーチ。漢字、読解、作文に対応。",
        tools=[manage_hint_tool, check_curriculum_tool, record_progress_tool],
    )
```

### Encouragement Agent

```python
def create_encouragement_agent(model: str | None = None) -> Agent:
    return Agent(
        name="encouragement_agent",
        model=model or DEFAULT_MODEL,
        instruction=ENCOURAGEMENT_SYSTEM_PROMPT,
        description="疲れた、わからない、やめたいなどネガティブな気持ちの子供を励まし、休憩を提案する。",
        tools=[record_progress_tool],
    )
```

### Review Agent

```python
def create_review_agent(model: str | None = None) -> Agent:
    return Agent(
        name="review_agent",
        model=model or DEFAULT_MODEL,
        instruction=REVIEW_SYSTEM_PROMPT,
        description="今日の学習を振り返り、何を頑張ったかを一緒に確認する。保護者向けのサマリーも作る。",
        tools=[record_progress_tool],
    )
```

## runner_service.py の変更

```python
# Before (Phase 2a)
from app.services.adk.runner.agent import create_socratic_agent
self._agent = create_socratic_agent()

# After (Phase 2b)
from app.services.adk.agents import create_router_agent
self._agent = create_router_agent()
```

Runner の `run_async()` / `run_live()` はそのまま。ADK フレームワークが sub_agents 間のルーティングを自動処理。

## 既存 agent.py の取り扱い

`runner/agent.py` の `create_socratic_agent()` は残す（後方互換）。`runner_service.py` のインポート先のみ変更。

## エラーハンドリング

- サブエージェントの委譲先が不明な場合: Router Agent が「何をやりたいか教えて？」と子供に確認する（プロンプトで制御）
- ツール呼び出し失敗時: 各エージェントがプロンプトベースでフォールバック（Phase 2a と同様）

## テスト戦略

### ユニットテスト

各エージェント作成関数のテスト:
- エージェント名、モデル、ツール、sub_agents の検証
- プロンプト文字列の内容検証（キーワード含有チェック）

### 統合テスト

- Router Agent が正しいサブエージェントに委譲するかの検証（モック LLM）
- セッション状態の共有が正しく動作するか

## 代替案と採用理由

| 代替案 | 不採用理由 |
|--------|-----------|
| AgentTool（明示的呼び出し） | AutoFlow の方がシンプルで、LLM が文脈に応じて柔軟に判断できる |
| カスタムルーティングロジック | ADK 標準の AutoFlow を使う方が保守性が高い |
| 単一エージェント + ツール追加 | 教科ごとのプロンプト最適化ができない |
