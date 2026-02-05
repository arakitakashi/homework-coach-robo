# Design - ソクラテス式対話API統合

## アーキテクチャ概要

```
┌─────────────┐     ┌────────────────┐     ┌────────────────────────┐
│  Frontend   │────▶│  FastAPI API   │────▶│  SocraticDialogue      │
│  (Next.js)  │     │  /api/v1/      │     │  Manager               │
└─────────────┘     └────────────────┘     └────────────────────────┘
                           │                          │
                           ▼                          ▼
                    ┌────────────┐           ┌────────────────┐
                    │  Schemas   │           │  LLM Client    │
                    │  (Pydantic)│           │  (Mock/Real)   │
                    └────────────┘           └────────────────┘
```

## API設計

### エンドポイント一覧

| メソッド | パス | 説明 |
|----------|------|------|
| POST | `/api/v1/dialogue/sessions` | セッション開始 |
| GET | `/api/v1/dialogue/sessions/{session_id}` | セッション取得 |
| DELETE | `/api/v1/dialogue/sessions/{session_id}` | セッション終了 |
| POST | `/api/v1/dialogue/sessions/{session_id}/analyze` | 回答分析 |
| POST | `/api/v1/dialogue/sessions/{session_id}/question` | 質問生成 |
| POST | `/api/v1/dialogue/sessions/{session_id}/hint` | ヒント生成 |
| POST | `/api/v1/dialogue/analyze-answer-request` | 答えリクエスト検出（セッション不要） |

### スキーマ設計

#### セッション開始

**Request: `CreateSessionRequest`**
```python
{
    "problem": str,           # 問題文（必須）
    "child_grade": int,       # 学年（1-3）
    "character_type": str     # キャラクタータイプ（オプション）
}
```

**Response: `SessionResponse`**
```python
{
    "session_id": str,
    "problem": str,
    "current_hint_level": int,
    "tone": str,
    "turns_count": int,
    "created_at": datetime
}
```

#### 回答分析

**Request: `AnalyzeRequest`**
```python
{
    "child_response": str     # 子供の回答（必須）
}
```

**Response: `AnalyzeResponse`**
```python
{
    "understanding_level": int,      # 0-10
    "is_correct_direction": bool,
    "needs_clarification": bool,
    "key_insights": list[str],
    "recommended_question_type": str,
    "recommended_tone": str,
    "should_advance_hint_level": bool,
    "answer_request_detected": bool,
    "answer_request_type": str
}
```

#### 質問生成

**Request: `GenerateQuestionRequest`**
```python
{
    "question_type": str | None,  # オプション（未指定時は自動決定）
    "tone": str | None            # オプション（未指定時は自動決定）
}
```

**Response: `QuestionResponse`**
```python
{
    "question": str,
    "question_type": str,
    "tone": str
}
```

#### ヒント生成

**Request: `GenerateHintRequest`**
```python
{
    "force_level": int | None    # オプション（未指定時は現在レベル）
}
```

**Response: `HintResponse`**
```python
{
    "hint": str,
    "hint_level": int,
    "hint_level_name": str,
    "is_answer_request_response": bool
}
```

## ファイル構成

```
backend/app/
├── api/
│   └── v1/
│       ├── __init__.py
│       ├── router.py           # APIルーター集約
│       └── dialogue.py         # 対話エンドポイント
├── schemas/
│   ├── __init__.py
│   └── dialogue.py             # 対話関連スキーマ
└── services/
    └── adk/
        └── dialogue/
            ├── manager.py      # 既存（変更なし）
            ├── models.py       # 既存（変更なし）
            └── session_store.py # 新規：セッション管理

backend/tests/
├── unit/
│   └── api/
│       └── v1/
│           └── test_dialogue.py
└── integration/
    └── api/
        └── v1/
            └── test_dialogue_flow.py
```

## 依存関係

### 新規パッケージ

なし（既存のFastAPI、Pydanticを使用）

### 内部依存

```
api/v1/dialogue.py
  └── schemas/dialogue.py
  └── services/adk/dialogue/manager.py
  └── services/adk/dialogue/session_store.py
```

## エラーハンドリング

| HTTPステータス | 使用場面 |
|----------------|----------|
| 400 Bad Request | バリデーションエラー |
| 404 Not Found | セッションが見つからない |
| 422 Unprocessable Entity | リクエストは正しいが処理できない |
| 500 Internal Server Error | 予期しないエラー |

### エラーレスポンス形式

```python
{
    "detail": {
        "error_code": str,    # "SESSION_NOT_FOUND" など
        "message": str,       # 人間が読めるメッセージ
        "field": str | None   # バリデーションエラー時のフィールド名
    }
}
```

## セキュリティ考慮事項

1. **入力バリデーション**: Pydanticで全入力を検証
2. **レート制限**: 後続フェーズで実装予定
3. **認証**: 後続フェーズで実装予定

## パフォーマンス考慮事項

1. **非同期処理**: すべてのエンドポイントをasync/awaitで実装
2. **セッション管理**: インメモリ辞書で高速アクセス
3. **LLM呼び出し**: タイムアウト設定（30秒）

## 代替案と採用理由

### セッション管理

| 案 | メリット | デメリット | 採用 |
|----|----------|------------|------|
| インメモリ辞書 | シンプル、高速 | サーバー再起動で消失 | ✅ MVP向け |
| Redis | 永続化、スケーラブル | 追加インフラ | 後続フェーズ |
| Firestore | 永続化、サーバーレス | レイテンシ | 後続フェーズ |

### API設計

| 案 | メリット | デメリット | 採用 |
|----|----------|------------|------|
| REST API | シンプル、標準的 | リアルタイム通信に不向き | ✅ MVP向け |
| WebSocket | リアルタイム | 複雑 | 後続フェーズ |
| gRPC | 高速、型安全 | ブラウザサポート限定 | 不採用 |
