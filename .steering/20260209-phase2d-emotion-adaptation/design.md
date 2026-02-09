# Design - Phase 2d: 感情適応（バックエンド）

## アーキテクチャ概要

感情適応は「独立 Agent」ではなく、**ツール + プロンプト拡張**で実現する。
Router Agent が各対話ターンで感情を分析し、`update_emotion_tool` で session.state に記録。
サブエージェントは session.state の感情データを参照してトーンを適応する。

```
子供の発言
    │
    ▼
Router Agent
    │
    ├──▶ update_emotion_tool（感情分析 → session.state["emotion"]）
    │
    ├──▶ 感情 + 内容に基づくルーティング判断
    │     ├── frustration > 0.7 → encouragement_agent
    │     ├── 算数の問題 → math_coach
    │     └── ...
    │
    ▼
Sub-Agent（感情コンテキスト参照）
    │
    ▼
応答（トーン適応済み）
```

## 技術選定

### なぜ独立 Emotion Agent ではなくツールか

| アプローチ | メリット | デメリット |
|-----------|---------|-----------|
| 独立 Emotion Agent | 関心の分離 | 追加 LLM コール、レイテンシ増 |
| **Router + ツール（採用）** | 追加 LLM コール不要、Router が自然に分析 | Router プロンプトが長くなる |

Router Agent はすでに「子供の発言を分析して判断する」役割を持っているため、感情分析もその一部として自然に統合できる。Router が `update_emotion_tool` を呼び出してから委譲先を決定する。

## データ設計

### session.state 拡張

```python
# session.state["emotion"]
{
    "frustration": 0.3,      # 0.0-1.0
    "confidence": 0.7,       # 0.0-1.0
    "fatigue": 0.2,          # 0.0-1.0
    "excitement": 0.5,       # 0.0-1.0
    "primary_emotion": "neutral",  # frustrated/confident/confused/happy/tired/neutral
    "support_level": "moderate",   # minimal/moderate/intensive
    "updated_at": "2026-02-09T15:00:00Z"
}
```

### サポートレベル決定ロジック

```
frustration > 0.7 OR fatigue > 0.6 → intensive
frustration > 0.4 OR fatigue > 0.3 → moderate
上記以外 → minimal
```

## ファイル構成

### 新規作成

```
backend/app/services/adk/
├── tools/
│   └── emotion_analyzer.py     # update_emotion_tool
└── agents/
    └── prompts/
        # 既存ファイルを更新
```

### 変更対象

```
backend/app/services/adk/
├── tools/__init__.py           # update_emotion_tool エクスポート追加
├── agents/router.py            # update_emotion_tool をツールに追加
├── agents/prompts/router.py    # 感情分析指示 + 感情ベースルーティング追加
├── agents/prompts/math_coach.py      # 感情コンテキスト参照追加
├── agents/prompts/japanese_coach.py  # 感情コンテキスト参照追加
└── agents/prompts/encouragement.py   # 感情コンテキスト参照追加
```

### テスト

```
backend/tests/unit/services/adk/
├── tools/test_emotion_analyzer.py    # ツールのユニットテスト
└── agents/
    ├── test_router.py                # 更新: update_emotion_tool 統合テスト
    ├── test_math_coach.py            # 更新不要（プロンプト変更のみ）
    └── test_encouragement.py         # 更新不要（プロンプト変更のみ）
```

## ツール設計

### update_emotion_tool

```python
def update_emotion(
    frustration: float,
    confidence: float,
    fatigue: float,
    excitement: float,
    primary_emotion: str,
    tool_context: ToolContext,
) -> dict:
    """子供の感情状態を分析結果に基づいて更新する。

    Args:
        frustration: イライラ度 (0.0-1.0)
        confidence: 自信度 (0.0-1.0)
        fatigue: 疲労度 (0.0-1.0)
        excitement: 興奮度 (0.0-1.0)
        primary_emotion: 主な感情 (frustrated/confident/confused/happy/tired/neutral)
        tool_context: ADK ToolContext（session.state アクセス用）

    Returns:
        dict: {
            "primary_emotion": str,
            "support_level": str,  # minimal/moderate/intensive
            "action_recommended": str,  # continue/encourage/rest
        }
    """
```

## プロンプト変更方針

### Router Agent プロンプト追加セクション

- 「感情分析」セクション: 子供の発言から感情を推定し `update_emotion` を呼ぶ指示
- 「感情ベースのルーティング」セクション: 高フラストレーション → encouragement_agent

### サブエージェントプロンプト追加セクション

- 「感情への配慮」セクション: session.state["emotion"] を参照したトーン調整ガイダンス
- 具体的な対応例（フラストレーション高い場合、自信がある場合など）

## エラーハンドリング

- `update_emotion_tool` の引数バリデーション（0.0-1.0 範囲チェック）
- `primary_emotion` の許可値チェック
- session.state["emotion"] が存在しない場合のフォールバック（既存動作を維持）

## 代替案と採用理由

| 代替案 | 不採用理由 |
|-------|-----------|
| 別途 Emotion Agent を作成 | LLM 追加コール不要。Router が自然に分析可能 |
| before_agent_callback で感情分析 | ADK のコールバック API が不安定。ツールの方が確実 |
| session.state ではなく Firestore に保存 | session.state で十分。セッション内で完結する情報 |
