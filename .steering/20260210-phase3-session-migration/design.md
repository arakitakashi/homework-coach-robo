# Design - Phase 3: セッション管理の移行

## アーキテクチャ概要

### 現在のアーキテクチャ（Phase 3完了時）

```
FastAPI Endpoints
├── POST /api/v1/dialogue/run (SSE)
│   ├── [AGENT_ENGINE_RESOURCE_NAME 設定時]
│   │   └── AgentEngineClient → Agent Engine
│   └── [未設定時] → AgentRunnerService (in-process)
│
└── WebSocket /ws/{user_id}/{session_id}
    └── VoiceStreamingService → Runner.run_live()

Session Management:
├── session_factory.create_session_service()
│   ├── [AGENT_ENGINE_ID 設定時] → VertexAiSessionService
│   └── [未設定時] → FirestoreSessionService
│
└── 環境変数による一括切り替え（全ユーザー同時）
```

### 移行後のアーキテクチャ（Issue #54完了時）

```
FastAPI Endpoints
├── POST /api/v1/dialogue/run (SSE)
│   └── AgentEngineClient → Agent Engine (managed)
│
└── WebSocket /ws/{user_id}/{session_id}
    └── VoiceStreamingService → Runner.run_live()
        └── FirestoreSessionService (音声専用、フォールバック)

Session Management:
├── session_factory.create_session_service(user_id)
│   ├── should_use_managed_session(user_id)
│   │   ├── [AGENT_ENGINE_ID 未設定] → False
│   │   ├── [MIGRATED_USER_IDS に含まれる] → True
│   │   └── [MIGRATION_PERCENTAGE でハッシュ判定] → True/False
│   │
│   ├── [True] → VertexAiSessionService (managed)
│   └── [False] → FirestoreSessionService (フォールバック)
│
└── ユーザー単位の段階的移行

Data Migration:
├── scripts/migrate_sessions.py
│   └── Firestore → Agent Engine 一括移行
│
└── scripts/validate_sessions.py
    └── 移行前後のデータ整合性検証
```

## 技術選定

### 段階的移行の実装方式

**採用: 環境変数ベースのフィーチャーフラグ**

理由:
- インフラ変更なしで実装可能（Firebase Remote Configなどの追加サービス不要）
- 環境変数はCloud Runで即座に変更可能
- ロールバックが簡単（環境変数削除→再起動）

| 環境変数 | 説明 | 例 |
|---------|------|-----|
| `AGENT_ENGINE_ID` | Agent Engine ID（全体スイッチ） | `agent-engine-123` |
| `MIGRATED_USER_IDS` | 移行済みユーザーID（カンマ区切り） | `user1,user2,user3` |
| `MIGRATION_PERCENTAGE` | 移行率（0-100%） | `10` |

### データ移行方式

**採用: オフライン一括移行 + オンデマンド移行**

| 方式 | タイミング | 対象 |
|------|----------|------|
| **オフライン一括移行** | デプロイ前 | 既存の全セッション |
| **オンデマンド移行** | 初回アクセス時 | まだ移行されていないセッション |

理由:
- オフライン移行で大部分を事前に移行（サービス影響なし）
- オンデマンド移行で漏れをカバー（ユーザー体験の連続性）

## ファイル構成

### 新規ファイル

```
backend/
├── scripts/
│   ├── migrate_sessions.py          # データ移行スクリプト
│   └── validate_sessions.py         # データ検証ツール
│
├── docs/
│   └── session-migration-rollback.md # ロールバック手順書
│
└── tests/
    ├── integration/
    │   └── test_session_migration.py # 統合テスト（移行フロー）
    └── unit/
        └── services/
            └── adk/
                └── sessions/
                    └── test_session_factory_migration.py # 段階的移行テスト
```

### 変更ファイル

```
backend/
└── app/
    └── services/
        └── adk/
            └── sessions/
                ├── session_factory.py     # 段階的移行ロジック追加
                └── __init__.py            # should_use_managed_session エクスポート
```

## データ設計

### Firestoreセッションスキーマ（移行元）

```python
# コレクション: sessions/{session_id}
{
    "user_id": "user123",
    "created_at": Timestamp,
    "updated_at": Timestamp,
    "state": {
        "app:": {...},      # アプリケーション状態
        "user:": {...},     # ユーザー状態
        "temp:": {...},     # 一時状態
    }
}
```

### Agent Engineセッションスキーマ（移行先）

```python
# VertexAiSessionService.store_session()
{
    "id": "session_abc123",
    "user_id": "user123",
    "created_at": "2026-02-10T12:00:00Z",
    "updated_at": "2026-02-10T12:30:00Z",
    "state": {
        "app:key1": "value1",
        "user:key2": "value2",
        "temp:key3": "value3",
    }
}
```

**差分**:
- スコープ区切り: Firestoreは`{"app:": {...}}`、Agent Engineは`{"app:key1": "value1"}`
- Timestamp形式: FirestoreはTimestamp型、Agent EngineはISO 8601文字列

### 移行ログスキーマ

```python
# ファイル: migration_{timestamp}.log
{
    "session_id": "session_abc123",
    "status": "success" | "failed" | "skipped",
    "error": "エラーメッセージ（失敗時のみ）",
    "timestamp": "2026-02-10T12:00:00Z"
}
```

## API設計

### session_factory.py の拡張

```python
def create_session_service(user_id: str | None = None) -> BaseSessionService:
    """環境変数とユーザーIDに基づいてセッションサービスを作成する

    Args:
        user_id: ユーザーID（段階的移行判定に使用）

    Returns:
        BaseSessionService: セッションサービスインスタンス
    """
    if should_use_managed_session(user_id):
        return _create_vertex_ai_session_service()
    return FirestoreSessionService()


def should_use_managed_session(user_id: str | None) -> bool:
    """ユーザーIDに基づいてマネージドセッションを使用するか判定する

    判定順序:
    1. AGENT_ENGINE_ID が未設定 → False
    2. MIGRATED_USER_IDS にユーザーIDが含まれる → True
    3. MIGRATION_PERCENTAGE によるハッシュ判定 → True/False
    4. デフォルト → False

    Args:
        user_id: ユーザーID

    Returns:
        bool: マネージドセッションを使用する場合 True
    """
    agent_engine_id = os.environ.get("AGENT_ENGINE_ID", "").strip()
    if not agent_engine_id:
        return False

    # 明示的に移行済みとマークされたユーザー
    migrated_users = os.environ.get("MIGRATED_USER_IDS", "").split(",")
    if user_id and user_id in migrated_users:
        logger.info("User %s is in MIGRATED_USER_IDS, using managed session", user_id)
        return True

    # パーセンテージベースのロールアウト
    percentage_str = os.environ.get("MIGRATION_PERCENTAGE", "0").strip()
    try:
        percentage = int(percentage_str)
    except ValueError:
        logger.warning("Invalid MIGRATION_PERCENTAGE: %s", percentage_str)
        return False

    if percentage > 0 and user_id:
        user_hash = hash(user_id) % 100
        use_managed = user_hash < percentage
        logger.info(
            "User %s hash %d, percentage %d, using managed: %s",
            user_id,
            user_hash,
            percentage,
            use_managed,
        )
        return use_managed

    return False


def _create_vertex_ai_session_service() -> BaseSessionService:
    """VertexAiSessionService を作成する（内部ヘルパー）"""
    from google.adk.sessions import VertexAiSessionService

    project = os.environ.get("GCP_PROJECT_ID") or None
    location = os.environ.get("GCP_LOCATION") or None
    agent_engine_id = os.environ.get("AGENT_ENGINE_ID", "").strip()

    return VertexAiSessionService(
        project=project,
        location=location,
        agent_engine_id=agent_engine_id,
    )
```

### scripts/migrate_sessions.py

```python
#!/usr/bin/env python3
"""Firestoreセッションを Agent Engine に移行するスクリプト"""

import asyncio
import logging
from datetime import datetime

from app.services.adk.sessions.firestore_session_service import FirestoreSessionService
from app.services.adk.sessions.session_factory import _create_vertex_ai_session_service

logger = logging.getLogger(__name__)


async def migrate_sessions(dry_run: bool = False) -> dict[str, int]:
    """全セッションを移行する

    Args:
        dry_run: True の場合、実際には移行せず検証のみ

    Returns:
        統計情報 {"success": 10, "failed": 1, "skipped": 2}
    """
    firestore_service = FirestoreSessionService()
    vertex_service = _create_vertex_ai_session_service()

    # Firestoreから全セッションIDを取得（ヘルパーメソッド追加が必要）
    session_ids = await firestore_service.list_all_session_ids()

    stats = {"success": 0, "failed": 0, "skipped": 0}

    for session_id in session_ids:
        try:
            # Firestoreからセッション読み取り
            session_data = await firestore_service.get_session(session_id)
            if session_data is None:
                logger.warning("Session %s not found, skipping", session_id)
                stats["skipped"] += 1
                continue

            if not dry_run:
                # Agent Engineに保存
                await vertex_service.store_session(session_id, session_data)

            logger.info("Migrated session %s", session_id)
            stats["success"] += 1

        except Exception as e:
            logger.error("Failed to migrate session %s: %s", session_id, e)
            stats["failed"] += 1

    return stats


if __name__ == "__main__":
    import sys

    dry_run = "--dry-run" in sys.argv

    logging.basicConfig(level=logging.INFO)
    logger.info("Starting session migration (dry_run=%s)", dry_run)

    stats = asyncio.run(migrate_sessions(dry_run=dry_run))

    logger.info("Migration complete: %s", stats)
    sys.exit(0 if stats["failed"] == 0 else 1)
```

### scripts/validate_sessions.py

```python
#!/usr/bin/env python3
"""Firestoreセッションと Agent Engine セッションの整合性を検証する"""

import asyncio
import logging

from app.services.adk.sessions.firestore_session_service import FirestoreSessionService
from app.services.adk.sessions.session_factory import _create_vertex_ai_session_service

logger = logging.getLogger(__name__)


async def validate_sessions() -> dict[str, any]:
    """セッションデータの整合性を検証する

    Returns:
        検証結果 {"total": 10, "matched": 9, "mismatched": 1, "details": [...]}
    """
    firestore_service = FirestoreSessionService()
    vertex_service = _create_vertex_ai_session_service()

    session_ids = await firestore_service.list_all_session_ids()

    result = {
        "total": len(session_ids),
        "matched": 0,
        "mismatched": 0,
        "details": [],
    }

    for session_id in session_ids:
        try:
            firestore_data = await firestore_service.get_session(session_id)
            vertex_data = await vertex_service.get_session(session_id)

            if _sessions_match(firestore_data, vertex_data):
                result["matched"] += 1
            else:
                result["mismatched"] += 1
                result["details"].append(
                    {
                        "session_id": session_id,
                        "firestore": firestore_data,
                        "vertex": vertex_data,
                    }
                )

        except Exception as e:
            logger.error("Failed to validate session %s: %s", session_id, e)
            result["mismatched"] += 1

    return result


def _sessions_match(firestore_data: dict, vertex_data: dict) -> bool:
    """2つのセッションデータが一致するか確認する"""
    # セッションIDの一致
    if firestore_data.get("id") != vertex_data.get("id"):
        return False

    # ユーザーIDの一致
    if firestore_data.get("user_id") != vertex_data.get("user_id"):
        return False

    # 状態の一致（キー・値の比較）
    # NOTE: スコープ区切りの差分を考慮
    firestore_state = firestore_data.get("state", {})
    vertex_state = vertex_data.get("state", {})

    # TODO: スコープ区切り変換後の比較ロジック
    return firestore_state == vertex_state


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting session validation")

    result = asyncio.run(validate_sessions())

    logger.info("Validation result: %s", result)
    print(f"Total: {result['total']}, Matched: {result['matched']}, Mismatched: {result['mismatched']}")

    if result["mismatched"] > 0:
        print("\nMismatched sessions:")
        for detail in result["details"]:
            print(f"  - {detail['session_id']}")
```

## エラーハンドリング

### 移行スクリプトのエラー処理

| エラー種別 | 対応 |
|-----------|------|
| **セッション読み取り失敗** | 警告ログ + スキップ（stats["skipped"]++） |
| **セッション変換失敗** | 警告ログ + スキップ |
| **セッション保存失敗** | リトライ（最大3回）、失敗時はエラーログ（stats["failed"]++） |
| **Agent Engine API接続失敗** | 即座に中断、ロールバック指示 |

### セッションファクトリのエラー処理

| エラー種別 | 対応 |
|-----------|------|
| **AGENT_ENGINE_ID 形式不正** | 警告ログ + FirestoreSessionService にフォールバック |
| **VertexAiSessionService初期化失敗** | エラーログ + FirestoreSessionService にフォールバック |
| **MIGRATION_PERCENTAGE 不正値** | 警告ログ + 0% として扱う |

## セキュリティ考慮事項

| 項目 | 対応 |
|------|------|
| **セッションデータの暗号化** | Firestore・Agent Engine共に保存時暗号化（GCPデフォルト） |
| **IAM権限** | Agent EngineサービスアカウントにFirestore読み取り権限（`roles/datastore.user`） |
| **移行ログの保護** | ログにセッションIDのみ記録（セッション内容は含めない） |
| **環境変数の管理** | Secret Managerではなく環境変数（機密情報ではないため） |

## パフォーマンス考慮事項

### 移行スクリプトのパフォーマンス

- **並列処理**: `asyncio.gather()`で最大10セッション同時移行
- **バッチ処理**: 1000セッションごとに進捗ログ出力
- **推定時間**: 10,000セッション → 約5-10分（並列度10の場合）

### セッションファクトリのパフォーマンス

- **ハッシュ計算**: Python標準`hash()`は高速（O(1)）
- **環境変数読み取り**: キャッシュなし（毎回`os.environ.get()`）→ 変更即座に反映
- **オーバーヘッド**: 判定ロジックは< 1ms、無視できるレベル

## 代替案と採用理由

| 案 | メリット | デメリット | 採用 |
|---|---------|-----------|------|
| **A: 環境変数ベースのフィーチャーフラグ** | 実装簡単、インフラ不要、即座に変更可能 | 高度なターゲティング不可 | ✅ |
| B: Firebase Remote Config | 高度なターゲティング、UI管理 | 追加サービス、依存関係増 | ❌ |
| C: データベースベースのフラグ | 動的変更、履歴管理 | 実装コスト大、DBアクセス増 | ❌ |
| **D: オフライン + オンデマンド移行** | 柔軟、サービス影響最小 | 実装複雑度増 | ✅ |
| E: オンデマンド移行のみ | 実装シンプル | 初回アクセス時のレイテンシ増 | ❌ |

## テスト戦略

### ユニットテスト

- `test_should_use_managed_session()`: 環境変数・ユーザーIDの組み合わせパターン（10ケース）
- `test_create_session_service()`: ファクトリの動作確認（Firestore/VertexAi切り替え）

### 統合テスト

- `test_session_migration_flow()`: Firestore → Agent Engine 移行フロー
- `test_session_validation()`: 移行前後のデータ整合性

### E2Eテスト

- 段階的移行シナリオ: 10% → 50% → 100% の段階的ロールアウト

## デプロイ計画

### Phase 1: 準備（本番前）

1. コード実装・テスト完了
2. 開発環境でスクリプト実行
3. データ検証ツールで整合性確認

### Phase 2: 段階的ロールアウト（本番環境）

1. `MIGRATION_PERCENTAGE=0` でデプロイ（コード配置のみ）
2. `MIGRATION_PERCENTAGE=1` → 1%のユーザーで動作確認（1日監視）
3. `MIGRATION_PERCENTAGE=10` → 10%（1週間監視）
4. `MIGRATION_PERCENTAGE=50` → 50%（1週間監視）
5. `MIGRATION_PERCENTAGE=100` → 100%（本番移行完了）

### Phase 3: フォールバック削除（1ヶ月後）

1. 問題なければ`AGENT_ENGINE_ID`を恒久化
2. FirestoreSessionServiceをフォールバックとして残す（削除は行わない）
