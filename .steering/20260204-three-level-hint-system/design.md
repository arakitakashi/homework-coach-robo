# Design - 3段階ヒントシステム

## アーキテクチャ概要

既存の `SocraticDialogueManager` を拡張し、3段階ヒントシステムを追加します。

```
SocraticDialogueManager (既存)
├── build_question_prompt()     # 質問生成プロンプト
├── build_analysis_prompt()     # 回答分析プロンプト
├── analyze_response()          # 回答分析
├── determine_question_type()   # 質問タイプ決定
├── determine_tone()            # トーン決定
├── generate_question()         # 質問生成
├── should_move_to_next_phase() # フェーズ遷移判定
└── [新規] 3段階ヒントシステム
    ├── build_hint_prompt()           # ヒントレベル別プロンプト構築
    ├── detect_answer_request()       # 「答え教えて」検出
    ├── generate_hint_response()      # ヒントレベル別レスポンス生成
    └── advance_hint_level()          # ヒントレベル進行
```

## データ設計

### HintLevel Enum（新規）

```python
class HintLevel(int, Enum):
    """ヒントレベル（3段階）"""

    PROBLEM_UNDERSTANDING = 1  # 問題理解の確認
    PRIOR_KNOWLEDGE = 2        # 既習事項の想起
    PARTIAL_SUPPORT = 3        # 部分的支援
```

### DialogueContext 拡張

既存の `current_hint_level: int` をそのまま活用。HintLevel Enumへの変換は内部で行う。

```python
# 既存（変更なし）
class DialogueContext(BaseModel):
    current_hint_level: int = Field(default=1, ge=1, le=3)
```

### AnswerRequestType（新規）

```python
class AnswerRequestType(str, Enum):
    """答えリクエストのタイプ"""

    NONE = "none"           # リクエストなし
    EXPLICIT = "explicit"   # 明示的（「答え教えて」）
    IMPLICIT = "implicit"   # 暗示的（「できない」「むずかしい」）
```

## プロンプト設計

### ヒントレベル別プロンプトテンプレート

```python
_HINT_LEVEL_INSTRUCTIONS = {
    HintLevel.PROBLEM_UNDERSTANDING: """
【レベル1: 問題理解の確認】
子供が問題を正しく理解しているか確認します。
- 問題文の再読を促す
- 何を求められているか質問する
- 例: 「この問題は何を聞いているかな？」「問題をもう一度読んでみよう」
""",
    HintLevel.PRIOR_KNOWLEDGE: """
【レベル2: 既習事項の想起】
子供が関連する知識を思い出せるよう導きます。
- 以前学んだ類似の概念を想起させる
- 関連する知識への橋渡しをする
- 例: 「前に似たような問題をやったよね」「○○のことを思い出してみて」
""",
    HintLevel.PARTIAL_SUPPORT: """
【レベル3: 部分的支援】
問題を小さく分解し、最初のステップのみ支援します。
- 問題を複数の小さなステップに分ける
- 最初のステップだけ一緒に考える
- 最終的な答えは絶対に教えない
- 例: 「まず最初のステップだけ一緒にやってみよう」
""",
}
```

### 答えリクエスト検出プロンプト

```python
ANSWER_REQUEST_DETECTION_PROMPT = """
子供の発話から「答えを教えてほしい」意図を検出してください。

子供の発話: {child_response}

以下のJSON形式で回答してください：
{{
    "request_type": "none" | "explicit" | "implicit",
    "confidence": 0.0-1.0,
    "detected_phrases": ["検出されたフレーズ"]
}}

判定基準:
- explicit: 「答え教えて」「答えを言って」「正解は？」など明示的な要求
- implicit: 「できない」「むずかしい」「わからない」「ギブアップ」など暗示的な要求
- none: 答えリクエストではない通常の回答
"""
```

## メソッド設計

### detect_answer_request()

```python
async def detect_answer_request(
    self,
    child_response: str,
) -> tuple[AnswerRequestType, float]:
    """子供の発話から答えリクエストを検出

    Args:
        child_response: 子供の発話

    Returns:
        (AnswerRequestType, confidence): リクエストタイプと信頼度
    """
```

### build_hint_prompt()

```python
def build_hint_prompt(
    self,
    context: DialogueContext,
    hint_level: HintLevel,
    tone: DialogueTone,
    is_answer_request: bool = False,
) -> str:
    """ヒントレベル別のプロンプトを構築

    Args:
        context: 対話コンテキスト
        hint_level: ヒントレベル
        tone: 対話トーン
        is_answer_request: 答えリクエストがあったか

    Returns:
        LLMに渡すプロンプト
    """
```

### generate_hint_response()

```python
async def generate_hint_response(
    self,
    context: DialogueContext,
    is_answer_request: bool = False,
) -> str:
    """ヒントレベルに応じたレスポンスを生成

    Args:
        context: 対話コンテキスト
        is_answer_request: 答えリクエストがあったか

    Returns:
        生成されたレスポンス
    """
```

### advance_hint_level()

```python
def advance_hint_level(
    self,
    context: DialogueContext,
    analysis: ResponseAnalysis,
) -> int:
    """ヒントレベルを進行させるべきか判定し、新しいレベルを返す

    ルール:
    - 各レベルで最低2ターン対話してから次へ
    - 理解度が改善傾向ならレベルを上げない
    - 最大レベル3を超えない

    Args:
        context: 対話コンテキスト
        analysis: 回答分析結果

    Returns:
        新しいヒントレベル（1-3）
    """
```

## ファイル構成

```
backend/app/services/adk/dialogue/
├── __init__.py
├── models.py              # HintLevel, AnswerRequestType 追加
├── learning_profile.py    # 変更なし
├── manager.py             # 3段階ヒントシステムのメソッド追加
└── hint_system.py         # [新規] ヒントシステム専用モジュール（オプション）

backend/tests/unit/services/adk/dialogue/
├── test_models.py         # HintLevel, AnswerRequestType テスト追加
├── test_manager.py        # ヒントシステムテスト追加
└── test_hint_system.py    # [新規] ヒントシステム専用テスト
```

## 設計判断

### モジュール分割について

**採用案**: 既存の `manager.py` を拡張

**理由**:
- SocraticDialogueManagerとの密結合が必要（context共有）
- 新規ファイル追加より既存拡張の方がシンプル
- テストの構成も既存に追加で済む

### HintLevel と QuestionType の関係

- `HintLevel`: 対話全体のサポートレベル（1回の対話で複数の質問を含む）
- `QuestionType`: 個々の質問の種類

これらは独立した概念として扱う。ヒントレベル内で、状況に応じて異なるQuestionTypeを使用可能。

## エラーハンドリング

| シナリオ | 処理 |
|----------|------|
| LLMクライアント未設定 | ValueError を raise |
| 答えリクエスト検出失敗 | デフォルトで `AnswerRequestType.NONE` を返す |
| ヒントレベル範囲外 | 1-3にクランプ |
| JSON パースエラー | フォールバックレスポンスを返す |

## セキュリティ考慮事項

- 子供の発話はログに記録しない（プライバシー保護）
- LLMへの入力はサニタイズ済みの問題文のみ
- 個人情報を含む可能性のある発話は分析後即座に破棄

## パフォーマンス考慮事項

- 答えリクエスト検出は軽量に（キーワードマッチングを優先、LLMは補助）
- ヒントレベル判定はメモリ内で完結（DB不要）
- LLM呼び出しは必要最小限に

## 代替案と採用理由

### 案1: 別クラス `HintSystemManager` として実装

**不採用理由**: SocraticDialogueManagerとの連携が複雑になる。状態の二重管理が発生。

### 案2: キーワードマッチングのみで答えリクエスト検出

**部分採用**: 高頻度キーワードは正規表現でマッチ、曖昧なケースのみLLM使用のハイブリッド方式を採用。
