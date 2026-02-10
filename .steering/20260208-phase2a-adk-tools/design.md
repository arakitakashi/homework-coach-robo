# Design - Phase 2a: ADK Function Tools

## アーキテクチャ概要

```
Agent (socratic_dialogue_agent)
├── tools=[
│   calculate_tool,        # 計算検証（純粋関数）
│   manage_hint_tool,      # ヒント管理（セッション状態）
│   record_progress_tool,  # 進捗記録（Firestore）
│   check_curriculum_tool, # カリキュラム参照（静的データ）
│   analyze_image_tool,    # 画像分析（Gemini Vision API）
│ ]
├── Runner → run_async() / run_live()
└── Events → SSE / WebSocket
```

ツールはADK `FunctionTool`でラップされ、エージェント実行時にLLMが自動的に呼び出す。
既存のRunner/API層は変更不要。

## ファイル構成

```
backend/app/services/adk/tools/
├── __init__.py              # 全ツールのエクスポート
├── calculate.py             # calculate_tool
├── hint_manager.py          # manage_hint_tool
├── curriculum.py            # check_curriculum_tool
├── progress_recorder.py     # record_progress_tool
└── image_analyzer.py        # analyze_image_tool

backend/tests/unit/services/adk/tools/
├── __init__.py
├── test_calculate.py
├── test_hint_manager.py
├── test_curriculum.py
├── test_progress_recorder.py
└── test_image_analyzer.py
```

## 各ツール設計

### 1. calculate_tool (calculate.py)

**目的**: LLMの計算ミスを防ぐため、四則演算を正確に検証

```python
def calculate_and_verify(
    expression: str,       # "23 + 45"
    child_answer: str,     # "68"
    grade_level: int,      # 1-3
) -> dict:
    return {
        "correct_answer": str,
        "is_correct": bool,
        "error_type": str | None,
        "hint": str,
    }
```

- `ast.literal_eval`や安全な式評価で計算
- 対応演算: +, -, ×, ÷
- エラー種類: "calculation", "unit", "misread"
- ヒントは学年に応じた言葉遣い

### 2. manage_hint_tool (hint_manager.py)

**目的**: 3段階ヒントシステムの状態を厳密に管理

```python
def manage_hint(
    session_id: str,
    action: str,           # "get_current", "advance", "reset"
    problem_id: str | None = None,
) -> dict:
    return {
        "current_level": int,
        "max_level": int,
        "hint_template": str,
        "can_advance": bool,
        "hints_used_total": int,
    }
```

- セッション状態（`ToolContext.state`）で管理
- LLMは直接レベルを変更不可（ツール経由のみ）
- ADKのToolContextを使用してセッション状態にアクセス

### 3. record_progress_tool (progress_recorder.py)

**目的**: 学習プロセスを記録し、ポイントを付与

```python
def record_progress(
    user_id: str,
    session_id: str,
    problem_id: str,
    outcome: str,          # "self_solved", "hint_solved", "guided_solved"
    hints_used: int,
    time_spent_seconds: int,
) -> dict:
    return {
        "points_earned": int,
        "total_points": int,
        "streak": int,
        "achievement_unlocked": str | None,
        "encouragement_message": str,
    }
```

- ポイント: self_solved=3, hint_solved=2, guided_solved=1
- ToolContextのセッション状態で累計管理
- 励ましメッセージは日本語

### 4. check_curriculum_tool (curriculum.py)

**目的**: 学年・教科に応じたカリキュラム情報を提供

```python
def check_curriculum(
    grade_level: int,
    subject: str,          # "math", "japanese"
    topic: str,            # "addition_carry", "kanji_grade2"
) -> dict:
    return {
        "prerequisites": list[str],
        "learning_objectives": list[str],
        "common_mistakes": list[str],
        "teaching_strategies": list[str],
        "related_topics": list[str],
    }
```

- Phase 2aではインメモリの静的データ（辞書）で実装
- 将来的にFirestore `curriculum`コレクションに移行

### 5. analyze_image_tool (image_analyzer.py)

**目的**: 宿題写真から問題を抽出

```python
def analyze_homework_image(
    image_data: str,                     # base64 encoded
    expected_subject: str | None = None,
) -> dict:
    return {
        "problems": list[dict],
        "confidence": float,
        "needs_confirmation": bool,
    }
```

- Gemini Vision APIを使用
- 手書き文字認識（OCR）
- 問題文の構造化抽出

## agent.pyの変更

```python
from app.services.adk.tools import (
    calculate_tool,
    check_curriculum_tool,
    manage_hint_tool,
    record_progress_tool,
    analyze_image_tool,
)

def create_socratic_agent(model: str | None = None) -> Agent:
    return Agent(
        name="socratic_dialogue_agent",
        model=model or DEFAULT_MODEL,
        instruction=SOCRATIC_SYSTEM_PROMPT,
        tools=[
            calculate_tool,
            manage_hint_tool,
            check_curriculum_tool,
            record_progress_tool,
            analyze_image_tool,
        ],
    )
```

## エラーハンドリング

- ツール内部のエラーはキャッチし、エラー情報を含むdictを返す
- ツール失敗時もエージェントは対話を継続できる（グレースフルデグラデーション）

## セキュリティ考慮事項

- `calculate_tool`: `eval()`は使用しない。安全な式パーサーを使用
- `analyze_image_tool`: base64データのサイズ制限を設ける
- 子供のデータはログに含めない
