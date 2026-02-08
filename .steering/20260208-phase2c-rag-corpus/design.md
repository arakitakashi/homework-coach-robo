# Design - Phase 2c: RAG Corpus作成・インデクシング

## アーキテクチャ概要

```
┌─────────────────────────────────────────────────────────┐
│                   Review Agent                          │
│  (振り返り・保護者レポート生成)                           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  search_memory_tool   │
         │  (VertexAiSearchTool) │
         └───────────┬───────────┘
                     │
                     ▼
    ┌────────────────────────────────────────┐
    │      Vertex AI RAG Engine              │
    │                                        │
    │  ┌──────────────────────────────────┐ │
    │  │  RAG Corpus:                     │ │
    │  │  homework-coach-memory-store     │ │
    │  │                                  │ │
    │  │  - 対話履歴 (dialogue_history)   │ │
    │  │  - 苦手分野 (weak_areas)         │ │
    │  │  - 成功体験 (success_stories)    │ │
    │  │  - カリキュラム (curriculum)     │ │
    │  └──────────────────────────────────┘ │
    │                                        │
    │  Embedding Model:                      │
    │  text-multilingual-embedding-002       │
    └────────────────────────────────────────┘
                     ▲
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼────────┐      ┌────────▼──────────┐
│ Indexing Service│      │ Firestore         │
│ (バッチ処理)     │      │ (fallback)        │
└────────────────┘      └───────────────────┘
```

## 技術選定

| 技術 | 用途 | 選定理由 |
|------|------|----------|
| Vertex AI RAG Engine | セマンティック検索 | マネージドサービス、日本語対応、ADK統合 |
| text-multilingual-embedding-002 | 埋め込みモデル | 日本語対応、多言語サポート、高精度 |
| VertexAiSearchTool (ADK) | ツール統合 | ADKネイティブサポート、エージェントとのシームレス統合 |
| Firestore | フォールバック検索 | 既存実装を維持、RAG障害時の代替手段 |
| BigQuery | インデクシング元データ | 学習履歴の集約・分析用データソース |

## データ設計

### RAG Corpusデータ構造

```python
# インデクシング対象ドキュメントの構造
@dataclass
class RagDocument:
    """RAG Corpusにインデクシングするドキュメント"""

    # 必須フィールド
    document_id: str  # 一意識別子
    content: str      # 検索対象テキスト（日本語）

    # メタデータ（フィルタリング・ランキングに使用）
    metadata: dict[str, Any] = field(default_factory=dict)
    # {
    #   "user_id": str,           # 子供のユーザーID
    #   "session_id": str,        # セッションID
    #   "category": str,          # "dialogue", "weak_area", "success", "curriculum"
    #   "subject": str,           # "math", "japanese"
    #   "grade": int,             # 1-3
    #   "timestamp": str,         # ISO 8601
    #   "problem_type": str,      # "addition", "kanji", etc.
    #   "difficulty": int,        # 1-5
    #   "outcome": str,           # "self_solved", "hint_solved", "guided_solved"
    # }
```

### Firestoreスキーマ（移行元・フォールバック）

```
/sessions/{session_id}/memories/{memory_id}
{
  "user_id": string,
  "content": string,
  "category": string,
  "metadata": {
    "subject": string,
    "grade": number,
    "timestamp": timestamp,
    ...
  },
  "rag_indexed": boolean,  // RAGにインデクシング済みかのフラグ
  "rag_document_id": string | null,  // RAG DocumentのID
}
```

## API設計（該当する場合）

### RagCorpusService API

```python
class RagCorpusService:
    """Vertex AI RAG Corpusを管理するサービス"""

    async def create_corpus(
        self,
        corpus_name: str,
        description: str,
    ) -> str:
        """Corpusを作成し、リソース名を返す"""
        ...

    async def index_document(
        self,
        corpus_name: str,
        document: RagDocument,
    ) -> str:
        """ドキュメントをインデクシングし、document_idを返す"""
        ...

    async def index_documents_batch(
        self,
        corpus_name: str,
        documents: list[RagDocument],
    ) -> list[str]:
        """複数ドキュメントをバッチインデクシング"""
        ...

    async def search(
        self,
        corpus_name: str,
        query: str,
        top_k: int = 5,
        filter_metadata: dict[str, Any] | None = None,
    ) -> list[RagSearchResult]:
        """セマンティック検索を実行"""
        ...
```

### search_memory_tool統合

```python
from google.adk.tools import VertexAiSearchTool

search_memory_tool = VertexAiSearchTool(
    data_store_id="homework-coach-memory-store",
    description="""
    子供の過去の学習履歴や苦手分野を検索する。

    - 対話履歴: 過去のセッションでの指導パターン
    - 苦手分野: 繰り返しつまずいたパターン
    - 成功体験: 自力で解けた問題や成長記録
    - カリキュラム: 学習指導要領、教科書の内容

    例:
    - 「繰り上がりの足し算で苦手だったパターンは？」
    - 「前回、自力で解けた問題は？」
    - 「2年生の掛け算の学習目標は？」
    """,
)
```

## ファイル構成

```
backend/app/services/adk/
├── agents/
│   └── review.py              # ← search_memory_toolを追加
├── tools/
│   ├── __init__.py            # ← search_memory_toolをエクスポート
│   └── search_memory.py       # 🆕 search_memory_tool定義
├── rag/                       # 🆕 RAG関連サービス
│   ├── __init__.py
│   ├── corpus_service.py      # 🆕 RagCorpusService
│   ├── indexing_service.py    # 🆕 IndexingService（バッチ処理）
│   └── models.py              # 🆕 RagDocument, RagSearchResult
└── memory/
    └── firestore_memory_service.py  # fallback用に維持

backend/tests/unit/services/adk/rag/
├── test_corpus_service.py     # 🆕
├── test_indexing_service.py   # 🆕
└── test_search_memory_tool.py # 🆕

backend/tests/integration/
└── test_rag_search_flow.py    # 🆕 エージェント統合テスト
```

## 依存関係

### バックエンド

```toml
[project.dependencies]
google-adk = ">=1.23.0"           # VertexAiSearchTool
google-cloud-aiplatform = ">=1.60.0"  # Vertex AI RAG API
google-genai = ">=1.0.0"          # 既存
```

## エラーハンドリング

### RAG検索失敗時のフォールバック

```python
async def search_with_fallback(
    query: str,
    user_id: str,
) -> list[SearchResult]:
    """RAG検索 → Firestore fallback"""
    try:
        # 1. Vertex AI RAG検索を試行
        results = await rag_corpus_service.search(
            corpus_name=CORPUS_NAME,
            query=query,
            filter_metadata={"user_id": user_id},
        )

        if results:
            logger.info("RAG search succeeded", extra={"count": len(results)})
            return results

        # 2. 結果が0件の場合、Firestoreフォールバック
        logger.warning("RAG returned 0 results, falling back to Firestore")
        return await firestore_memory_service.search(query, user_id)

    except Exception as e:
        # 3. RAGエラー時もFirestoreフォールバック
        logger.error(f"RAG search failed: {e}, falling back to Firestore")
        return await firestore_memory_service.search(query, user_id)
```

### リトライロジック

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
)
async def index_document_with_retry(
    corpus_name: str,
    document: RagDocument,
) -> str:
    """リトライ付きインデクシング"""
    return await rag_corpus_service.index_document(corpus_name, document)
```

## セキュリティ考慮事項

### 1. 個人情報のマスキング

```python
def sanitize_content_for_rag(content: str) -> str:
    """RAGインデクシング前に個人情報をマスキング"""
    # 子供の名前を仮名に置換
    content = re.sub(r'(太郎|花子|[ぁ-ん]{2,4}くん|[ぁ-ん]{2,4}さん)', '[子供]', content)

    # 保護者の名前を仮名に置換
    content = re.sub(r'お母さん|お父さん', '[保護者]', content)

    return content
```

### 2. IAMロール設定

```hcl
# Terraform: backend/infrastructure/terraform/modules/rag/main.tf
resource "google_project_iam_member" "rag_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${var.service_account_email}"
}

resource "google_project_iam_member" "rag_admin" {
  project = var.project_id
  role    = "roles/aiplatform.admin"
  member  = "serviceAccount:${var.admin_service_account_email}"
}
```

### 3. データ暗号化

- Vertex AI RAGは標準でデータを暗号化（Google-managed encryption keys）
- カスタムCMEK（Customer-Managed Encryption Keys）は将来のフェーズで検討

## パフォーマンス考慮事項

### 1. 検索レスポンス時間の最適化

```python
# top_kを制限してレスポンスタイムを短縮
search_memory_tool = VertexAiSearchTool(
    data_store_id="homework-coach-memory-store",
    max_results=5,  # デフォルト: 10 → 5に削減
)
```

### 2. バッチインデクシング

```python
# 100件ずつバッチ処理
BATCH_SIZE = 100

async def index_all_sessions(user_id: str):
    """ユーザーの全セッションをインデクシング"""
    sessions = await get_user_sessions(user_id)

    for i in range(0, len(sessions), BATCH_SIZE):
        batch = sessions[i:i+BATCH_SIZE]
        documents = [session_to_rag_document(s) for s in batch]
        await rag_corpus_service.index_documents_batch(CORPUS_NAME, documents)
```

### 3. キャッシュ戦略

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_curriculum_content(grade: int, subject: str, topic: str) -> str:
    """カリキュラム内容をキャッシュ（変更頻度が低いため）"""
    ...
```

## 代替案と採用理由

| 代替案 | メリット | デメリット | 採用理由 |
|--------|----------|------------|----------|
| **Vertex AI RAG Engine（採用）** | マネージド、ADK統合、日本語対応 | コスト（検索クエリ課金） | 運用負荷最小、ADKとのシームレス統合 |
| Pinecone | 高速、スケーラブル | 外部サービス、ADK統合なし | GCP内で完結させたい |
| Weaviate（セルフホスト） | コスト削減、カスタマイズ性 | 運用負荷大、インフラ管理 | マネージドサービスを優先 |
| Firestore Vector Search | GCP内で完結、低コスト | ベータ版、機能制限 | 本番環境での採用リスク |

## 補足: Corpus初期化スクリプト

```python
# backend/scripts/initialize_rag_corpus.py
"""
RAG Corpus初期化スクリプト

Usage:
  uv run python scripts/initialize_rag_corpus.py --env dev
"""

async def main():
    service = RagCorpusService()

    # 1. Corpus作成
    corpus_name = await service.create_corpus(
        corpus_name="homework-coach-memory-store",
        description="宿題コーチロボット - 学習履歴・苦手分野・成功体験の記憶",
    )

    # 2. サンプルデータのインデクシング
    sample_documents = load_sample_data()
    await service.index_documents_batch(corpus_name, sample_documents)

    print(f"✅ Corpus initialized: {corpus_name}")
    print(f"   Indexed {len(sample_documents)} documents")
```
