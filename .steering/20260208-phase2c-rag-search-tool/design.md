# Design - Phase 2c: RAG Search Tool 統合

## アーキテクチャ概要

Vertex AI RAG Engine を使用したセマンティック記憶検索ツールを ADK FunctionTool として実装する。既存の `FirestoreMemoryService` の `search_memory()` を内部的に置き換え、外部インターフェースは維持する。

```
子供の発言
    │
    ▼
┌──────────────────┐
│ search_memory    │
│ _tool            │
│                  │
│ ┌──────────────┐ │
│ │ Vertex AI    │ │
│ │ RAG Engine   │ │     ┌──────────────┐
│ │              │ │────▶│ セマンティック│
│ │ - Corpus:    │ │     │ 検索結果を   │
│ │   memories   │ │     │ エージェント │
│ └──────────────┘ │     │ に返却      │
└──────────────────┘     └──────────────┘
```

## 技術選定

### Vertex AI RAG API

- **使用 API**: Vertex AI RAG Engine（`google-cloud-aiplatform` SDK）
- **データストア**: Vertex AI RAG Corpus
- **埋め込みモデル**: `textembedding-gecko@003`（日本語対応）
- **検索方法**: セマンティック類似度検索

### ADK FunctionTool

- `google.adk.tools.FunctionTool` を使用
- 検索関数を `FunctionTool(func=search_memory)` でラップ

## データ設計

### Vertex AI RAG Corpus 構造

```
Corpus: homework-coach-memories
├── User-specific documents
│   ├── user_{user_id}_session_{session_id}_event_{event_id}
│   │   ├── content: "子供の発言と応答"
│   │   ├── metadata:
│   │   │   ├── user_id: string
│   │   │   ├── session_id: string
│   │   │   ├── timestamp: string
│   │   │   ├── memory_type: "dialogue" | "weakness" | "success" | "curriculum"
│   │   │   └── subject: "math" | "japanese" | ...
```

### 検索クエリと結果

**入力**:
```python
query: str  # 例: "繰り上がりの足し算"
user_id: str
top_k: int = 5
```

**出力**:
```python
{
    "memories": [
        {
            "content": "前回、繰り上がりの足し算で3回つまずいた",
            "metadata": {
                "user_id": "user_123",
                "session_id": "session_456",
                "timestamp": "2026-02-01T10:00:00Z",
                "memory_type": "weakness",
                "subject": "math"
            },
            "relevance_score": 0.95
        },
        ...
    ]
}
```

## API設計（該当する場合）

### search_memory_tool 関数シグネチャ

```python
def search_memory(
    query: str,
    user_id: str,
    top_k: int = 5,
) -> dict[str, object]:
    """記憶を検索する

    Args:
        query: 検索クエリ（例: "繰り上がりの足し算"）
        user_id: ユーザーID
        top_k: 返却する記憶の最大数

    Returns:
        dict: {
            "memories": list[{
                "content": str,
                "metadata": dict,
                "relevance_score": float
            }],
            "query": str,
            "total_results": int
        }
    """
```

### ToolContext との統合

```python
from google.adk.tools import FunctionTool, ToolContext

def search_memory_with_context(
    query: str,
    top_k: int = 5,
    ctx: ToolContext | None = None,
) -> dict[str, object]:
    """ToolContext経由でuser_idを取得する"""
    if ctx is None:
        raise ValueError("ToolContext is required")

    user_id = ctx.state.get("user_id")
    if not user_id:
        raise ValueError("user_id not found in session state")

    # Vertex AI RAG検索を実行
    return _search_rag(query, user_id, top_k)

search_memory_tool = FunctionTool(func=search_memory_with_context)
```

## ファイル構成

```
backend/app/services/adk/
├── tools/
│   ├── __init__.py                  # search_memory_tool をエクスポート
│   ├── search_memory.py             # ✨ NEW: search_memory_tool 実装
│   ├── calculate.py
│   ├── hint_manager.py
│   ├── curriculum.py
│   ├── progress_recorder.py
│   └── image_analyzer.py
├── agents/
│   ├── review.py                    # tools=[..., search_memory_tool] を追加
│   └── ...
└── memory/
    ├── firestore_memory_service.py  # search_memory() を RAG ベースに移行
    └── ...

backend/tests/unit/services/adk/tools/
├── test_search_memory.py            # ✨ NEW: search_memory_tool テスト
```

## 依存関係

### 新規パッケージ

```toml
# pyproject.toml に追加
google-cloud-aiplatform = "^1.60.0"  # Vertex AI RAG Engine
```

### 既存パッケージ

- `google-adk >= 1.23.0`
- `google-genai >= 1.0.0`
- `google-cloud-firestore >= 2.18.0`

## エラーハンドリング

```python
class RagSearchError(Exception):
    """RAG検索エラー"""

class RagCorpusNotFoundError(RagSearchError):
    """Corpusが見つからない"""

class RagSearchTimeoutError(RagSearchError):
    """検索タイムアウト"""
```

**フォールバック戦略**:
- RAG検索が失敗した場合、既存のキーワード検索にフォールバック
- エラーログを記録し、モニタリングアラートを発火

## セキュリティ考慮事項

1. **データプライバシー**
   - ユーザーごとに記憶を分離（metadata.user_id でフィルタリング）
   - 他のユーザーの記憶を検索できないよう制御

2. **API認証**
   - Vertex AI RAG API は ADC（Application Default Credentials）を使用
   - ローカル開発: `gcloud auth application-default login`
   - 本番環境: Cloud Run のサービスアカウント

3. **レート制限**
   - Vertex AI RAG API のクォータを考慮
   - 必要に応じてリトライロジックを実装

## パフォーマンス考慮事項

1. **検索速度**
   - 目標: 2秒以内
   - Vertex AI RAG のインデックスは事前構築されているため高速

2. **キャッシング**
   - 頻繁に検索されるクエリは Redis でキャッシュ（Phase 3以降）

3. **バッチインデクシング**
   - セッション終了時に一括でインデクシング
   - リアルタイムインデクシングは Phase 2c 後半で実装

## 代替案と採用理由

### 代替案1: Firestore Vector Search

**メリット**:
- 既存の Firestore インフラを使用可能
- 追加の API 統合不要

**デメリット**:
- ベクトル埋め込みの生成を自前で実装
- Vertex AI RAG より精度が低い

**不採用理由**: Vertex AI RAG の方が高精度でマネージドサービスとして運用しやすい

### 代替案2: カスタム埋め込み + pgvector

**メリット**:
- フルコントロール可能
- コスト削減

**デメリット**:
- 実装・運用コストが高い
- Google Cloud エコシステムとの統合が弱い

**不採用理由**: MVP ではマネージドサービスを優先

## 移行計画

### Phase 2c-1: search_memory_tool 実装（本タスク）

1. `search_memory.py` の実装
2. ADK FunctionTool 統合
3. ユニットテスト作成

### Phase 2c-2: RAG Corpus 作成（手動）

1. Vertex AI Console で Corpus を作成
2. 既存の Firestore memories をインポート

### Phase 2c-3: FirestoreMemoryService 移行

1. `search_memory()` を RAG ベースに置き換え
2. キーワード検索をフォールバックとして残す

### Phase 2c-4: エージェント統合

1. Review Agent に `search_memory_tool` を追加
2. 他のエージェントにも順次展開
