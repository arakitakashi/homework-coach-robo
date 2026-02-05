# Design - ADK MemoryBank統合

## アーキテクチャ概要

```
┌─────────────────────────────────────────────────────────────────┐
│                         ADK Runner                               │
│  ┌─────────────────────┐    ┌─────────────────────────────────┐ │
│  │ FirestoreSession    │    │ FirestoreMemoryService          │ │
│  │ Service             │    │ (BaseMemoryService準拠)         │ │
│  │                     │    │                                 │ │
│  │ - create_session    │    │ - add_session_to_memory         │ │
│  │ - get_session       │    │ - search_memory                 │ │
│  │ - append_event      │    │                                 │ │
│  └──────────┬──────────┘    └──────────┬──────────────────────┘ │
└─────────────┼───────────────────────────┼───────────────────────┘
              │                           │
              ▼                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Firestore                                 │
│  ┌─────────────────────┐    ┌─────────────────────────────────┐ │
│  │ /sessions/{id}      │    │ /memories/{app}/users/{user}/   │ │
│  │   └─/events/{id}    │    │   └─entries/{id}                │ │
│  │                     │    │                                 │ │
│  │ /app_state/{app}    │    │                                 │ │
│  │ /user_state/{app}/  │    │                                 │ │
│  │   └─users/{id}      │    │                                 │ │
│  └─────────────────────┘    └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 技術選定

| コンポーネント | 選定技術 | 理由 |
|--------------|---------|------|
| 永続化 | Firestore | 既存のSessionServiceと一貫性、リアルタイム機能 |
| 検索 | キーワードマッチング | InMemoryMemoryServiceと同等、将来RAGに拡張可能 |
| 非同期処理 | asyncio | Firestore AsyncClientとの整合性 |

---

## データ設計

### Firestoreコレクション構造

```
/memories/{app_name}/users/{user_id}/entries/{entry_id}
```

#### MemoryEntry ドキュメント

```json
{
  "id": "entry-uuid",
  "session_id": "session-uuid",
  "author": "user" | "model",
  "content": {
    "role": "user" | "model",
    "parts": [
      {"text": "..."}
    ]
  },
  "custom_metadata": {
    "memory_type": "learning_insight" | "thinking_pattern" | "effective_approach",
    "tags": ["math", "addition"],
    "session_summary": {...}
  },
  "timestamp": 1707123456.789,
  "created_at": 1707123456.789
}
```

### インデックス設計

```
memories/{app_name}/users/{user_id}/entries
  - timestamp DESC (最新順取得)
  - custom_metadata.memory_type + timestamp (タイプ別取得)
```

---

## API設計

### FirestoreMemoryService

```python
class FirestoreMemoryService(BaseMemoryService):
    """Firestore-backed ADK MemoryService"""

    def __init__(
        self,
        project_id: str | None = None,
        database: str = "(default)",
    ) -> None:
        """初期化

        Args:
            project_id: GCPプロジェクトID
            database: Firestoreデータベース名
        """

    async def add_session_to_memory(
        self,
        session: Session,
    ) -> None:
        """セッションを記憶に追加

        Args:
            session: ADK Session
        """

    async def search_memory(
        self,
        *,
        app_name: str,
        user_id: str,
        query: str,
    ) -> SearchMemoryResponse:
        """記憶を検索

        Args:
            app_name: アプリ名
            user_id: ユーザーID
            query: 検索クエリ

        Returns:
            SearchMemoryResponse: マッチした記憶のリスト
        """
```

### コンバーター関数

```python
def event_to_memory_entry(event: Event, session_id: str) -> dict[str, Any]:
    """ADK EventをFirestore用dictに変換"""

def dict_to_memory_entry(data: dict[str, Any]) -> MemoryEntry:
    """Firestore dictをADK MemoryEntryに変換"""

def extract_text_from_event(event: Event) -> str | None:
    """イベントからテキストを抽出"""
```

---

## ファイル構成

```
backend/app/services/adk/memory/
├── __init__.py                    # パッケージエクスポート
├── converters.py                  # ADK ↔ Firestore変換
└── firestore_memory_service.py    # FirestoreMemoryService

backend/tests/unit/services/adk/memory/
├── __init__.py
├── test_converters.py
└── test_firestore_memory_service.py
```

---

## 依存関係

### 既存モジュール

- `google.adk.memory.base_memory_service.BaseMemoryService`
- `google.adk.memory.base_memory_service.SearchMemoryResponse`
- `google.adk.memory.memory_entry.MemoryEntry`
- `google.adk.sessions.session.Session`
- `google.adk.events.event.Event`
- `google.cloud.firestore.AsyncClient`

### 新規追加なし

既存の依存関係で実装可能。

---

## エラーハンドリング

| エラー | 対処 |
|--------|------|
| Firestore接続エラー | ログ出力、リトライ（3回） |
| 無効なセッション | 警告ログ、スキップ |
| 検索タイムアウト | 部分結果を返却 |

---

## セキュリティ考慮事項

1. **データアクセス制御**: user_id単位で記憶を分離
2. **個人情報**: 記憶内容に個人情報が含まれる可能性あり、暗号化検討
3. **データ保持期間**: GDPR準拠のため、削除機能を将来実装

---

## パフォーマンス考慮事項

1. **バッチ書き込み**: 複数イベントを一括でFirestoreに書き込み
2. **キャッシュ**: 頻繁に検索されるクエリ結果をRedisにキャッシュ（将来）
3. **インデックス**: 検索パフォーマンスのためのFirestoreインデックス

---

## 代替案と採用理由

### 代替案1: Vertex AI RAG Memory Service

- **メリット**: セマンティック検索、より高精度な検索
- **デメリット**: 追加コスト、セットアップ複雑
- **採用しない理由**: MVP段階ではキーワード検索で十分

### 代替案2: InMemoryMemoryService + 手動永続化

- **メリット**: シンプル
- **デメリット**: アプリ再起動で消失、スケーラビリティなし
- **採用しない理由**: 本番環境での使用に適さない

### 採用案: FirestoreMemoryService

- **メリット**: 永続化、スケーラビリティ、既存インフラ活用
- **デメリット**: InMemoryより若干遅い
- **採用理由**: SessionServiceと一貫性、将来のRAG統合に備えた設計
