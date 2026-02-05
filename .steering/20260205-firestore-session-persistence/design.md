# Design - Firestore Session Persistence (ADK統合)

## アーキテクチャ概要

```
┌──────────────────────────────────────────────────────────────┐
│                    ADK Runner / Agent                        │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│              FirestoreSessionService                         │
│              (BaseSessionService継承)                        │
│                                                              │
│  ┌─────────────┐ ┌─────────────┐ ┌───────────────────────┐  │
│  │create_session│ │get_session  │ │append_event           │  │
│  │list_sessions │ │delete_session│ │(状態更新+永続化)      │  │
│  └─────────────┘ └─────────────┘ └───────────────────────┘  │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                   Cloud Firestore                            │
│                                                              │
│  /sessions/{session_id}                                      │
│    ├─ メタデータ (userId, appName, state, lastUpdateTime)   │
│    └─ /dialogue_turns/{turn_id}                              │
│                                                              │
│  /app_state/{app_name}                                       │
│    └─ state: map                                             │
│                                                              │
│  /user_state/{app_name}/users/{user_id}                      │
│    └─ state: map                                             │
└──────────────────────────────────────────────────────────────┘
```

---

## 技術選定

| 項目 | 選定 | 理由 |
|------|------|------|
| ベースクラス | `google.adk.sessions.BaseSessionService` | ADK標準インターフェース |
| Firestoreクライアント | `google.cloud.firestore.AsyncClient` | 非同期対応、ADKと整合 |
| シリアライズ | Pydantic + dict変換 | ADK Sessionモデルと整合 |
| テスト | pytest + pytest-asyncio | 非同期テスト対応 |

---

## データ設計

### Firestoreコレクション構造

#### 1. sessions コレクション

```
/sessions/{session_id}
  ├─ id: string                    # セッションID
  ├─ app_name: string              # アプリ名 ("homework_coach")
  ├─ user_id: string               # ユーザーID
  ├─ state: map                    # セッションスコープの状態
  │   ├─ problem: string           # 現在の問題
  │   ├─ current_hint_level: number
  │   ├─ tone: string
  │   └─ ...その他
  ├─ created_at: timestamp
  ├─ last_update_time: float       # ADK互換 (Unix timestamp)
  └─ is_active: boolean
```

#### 2. events サブコレクション

```
/sessions/{session_id}/events/{event_id}
  ├─ id: string                    # イベントID (auto-generated)
  ├─ invocation_id: string         # ADK呼び出しID
  ├─ author: string                # "user" or "agent"
  ├─ timestamp: float              # Unix timestamp
  ├─ partial: boolean              # 部分イベントか
  ├─ actions: array                # ADK Actionリスト
  └─ state_delta: map              # 状態変更差分
```

#### 3. app_state コレクション

```
/app_state/{app_name}
  └─ state: map                    # アプリスコープの状態
```

#### 4. user_state コレクション

```
/user_state/{app_name}/users/{user_id}
  └─ state: map                    # ユーザースコープの状態
```

### インデックス設計

```json
{
  "indexes": [
    {
      "collectionGroup": "sessions",
      "queryScope": "COLLECTION",
      "fields": [
        { "fieldPath": "app_name", "order": "ASCENDING" },
        { "fieldPath": "user_id", "order": "ASCENDING" },
        { "fieldPath": "created_at", "order": "DESCENDING" }
      ]
    },
    {
      "collectionGroup": "events",
      "queryScope": "COLLECTION",
      "fields": [
        { "fieldPath": "timestamp", "order": "ASCENDING" }
      ]
    }
  ]
}
```

---

## API設計

### FirestoreSessionService クラス

```python
from google.adk.sessions.base_session_service import BaseSessionService
from google.adk.sessions.session import Session
from google.cloud.firestore import AsyncClient

class FirestoreSessionService(BaseSessionService):
    """Firestore-backed ADK SessionService"""

    def __init__(
        self,
        project_id: str | None = None,
        database: str = "(default)",
    ) -> None:
        """初期化

        Args:
            project_id: GCPプロジェクトID（Noneでデフォルト）
            database: Firestoreデータベース名
        """
        self._db = AsyncClient(project=project_id, database=database)

    async def create_session(
        self,
        *,
        app_name: str,
        user_id: str,
        state: dict[str, Any] | None = None,
        session_id: str | None = None,
    ) -> Session:
        """セッション作成"""
        ...

    async def get_session(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        config: GetSessionConfig | None = None,
    ) -> Session | None:
        """セッション取得"""
        ...

    async def list_sessions(
        self,
        *,
        app_name: str,
        user_id: str | None = None,
    ) -> ListSessionsResponse:
        """セッション一覧"""
        ...

    async def delete_session(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
    ) -> None:
        """セッション削除"""
        ...

    async def append_event(
        self,
        session: Session,
        event: Event,
    ) -> Event:
        """イベント追加（永続化付き）"""
        ...
```

### 状態マージロジック

```python
def _merge_state(
    self,
    app_state: dict[str, Any],
    user_state: dict[str, Any],
    session_state: dict[str, Any],
) -> dict[str, Any]:
    """3層状態をマージ

    優先順位: session > user > app
    プレフィックス付きで返却
    """
    merged = {}

    # アプリ状態 (app:* プレフィックス)
    for key, value in app_state.items():
        merged[f"app:{key}"] = value

    # ユーザー状態 (user:* プレフィックス)
    for key, value in user_state.items():
        merged[f"user:{key}"] = value

    # セッション状態 (プレフィックスなし)
    for key, value in session_state.items():
        merged[key] = value

    return merged
```

### イベント永続化ロジック

```python
async def append_event(self, session: Session, event: Event) -> Event:
    """イベント追加と永続化"""

    # 部分イベントは永続化しない
    if event.partial:
        return event

    # temp:* キーを除去
    event = self._trim_temp_delta_state(event)

    # インメモリ状態更新（親クラス呼び出し）
    self._update_session_state(session, event)
    session.events.append(event)
    session.last_update_time = event.timestamp

    # Firestore永続化（トランザクション）
    async with self._db.transaction() as txn:
        session_ref = self._db.collection("sessions").document(session.id)

        # 状態差分を適切なスコープに振り分け
        await self._persist_state_delta(txn, session, event.state_delta)

        # イベントを保存
        event_ref = session_ref.collection("events").document()
        txn.set(event_ref, self._event_to_dict(event))

        # セッションのlast_update_timeを更新
        txn.update(session_ref, {"last_update_time": event.timestamp})

    return event
```

---

## ファイル構成

```
backend/app/services/adk/
├── __init__.py
├── sessions/                          # NEW: セッション管理
│   ├── __init__.py
│   ├── firestore_session_service.py   # FirestoreSessionService
│   ├── models.py                      # Firestore用モデル
│   └── converters.py                  # ADK ↔ Firestore変換
└── dialogue/
    ├── __init__.py
    ├── manager.py
    ├── models.py                      # 既存（変更なし）
    ├── learning_profile.py
    ├── gemini_client.py
    └── session_store.py               # 既存（インメモリ、維持）
```

---

## 依存関係

### 新規依存パッケージ

```toml
# pyproject.toml に追加
[project.dependencies]
google-adk = ">=1.23.0"
google-cloud-firestore = ">=2.11.0"
```

### 内部依存

```
FirestoreSessionService
  ├── google.adk.sessions.BaseSessionService
  ├── google.adk.sessions.Session
  ├── google.adk.sessions.Event
  ├── google.cloud.firestore.AsyncClient
  └── app.services.adk.sessions.converters
```

---

## エラーハンドリング

### 例外クラス

| 例外 | 発生条件 | 対処 |
|------|---------|------|
| `AlreadyExistsError` | 既存session_idで作成 | クライアントにエラー返却 |
| `google.api_core.exceptions.NotFound` | 存在しないセッション取得 | Noneを返却 |
| `google.api_core.exceptions.Aborted` | トランザクション競合 | 自動リトライ |
| `google.api_core.exceptions.DeadlineExceeded` | タイムアウト | リトライ後エラー |

### リトライ戦略

```python
from google.api_core import retry

# Firestoreクエリ用リトライ設定
RETRY_CONFIG = retry.AsyncRetry(
    initial=0.1,
    maximum=10.0,
    multiplier=2.0,
    deadline=60.0,
)
```

---

## セキュリティ考慮事項

### Firestore Security Rules

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // セッションは所有者のみアクセス可能
    match /sessions/{sessionId} {
      allow read, write: if request.auth != null &&
        request.auth.uid == resource.data.user_id;

      match /events/{eventId} {
        allow read, write: if request.auth != null &&
          request.auth.uid == get(/databases/$(database)/documents/sessions/$(sessionId)).data.user_id;
      }
    }

    // ユーザー状態は所有者のみ
    match /user_state/{appName}/users/{userId} {
      allow read, write: if request.auth != null &&
        request.auth.uid == userId;
    }

    // アプリ状態は認証済みユーザーが読み取り可能
    match /app_state/{appName} {
      allow read: if request.auth != null;
      allow write: if false; // サーバーサイドのみ
    }
  }
}
```

---

## パフォーマンス考慮事項

### 読み取り最適化

1. **プロジェクション**: 必要なフィールドのみ取得
2. **インデックス**: 頻繁なクエリ用に複合インデックス
3. **バッチ読み取り**: 複数ドキュメントを並列取得

### 書き込み最適化

1. **バッチ書き込み**: 複数ドキュメントをトランザクションで
2. **差分更新**: `update()`で変更フィールドのみ
3. **非同期**: イベント永続化を非同期で

### キャッシュ戦略（将来）

- **Redis**: ホットセッションのキャッシュ
- **TTL**: 5分でFirestoreと同期

---

## 代替案と採用理由

### 案1: Firebase Admin SDK + Firestore

**採用**: ADK互換性、非同期サポート、既存設計との整合

### 案2: Cloud SQL (PostgreSQL)

**不採用**: リアルタイム同期なし、ADKのDatabaseSessionServiceはSQLAlchemyベースで重い

### 案3: Redis + 永続化バックアップ

**不採用**: トランザクション整合性の保証が難しい、本格永続化には不向き

---

## テスト戦略

### ユニットテスト

- Firestoreクライアントをモック
- 状態マージロジックのテスト
- イベント永続化ロジックのテスト

### 統合テスト

- Firestore Emulatorを使用
- 実際のCRUD操作をテスト
- 並行操作のテスト

### テストカバレッジ目標

- 全体: 80%以上
- 主要メソッド: 90%以上
