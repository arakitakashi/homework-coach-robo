# Design - BigQuery学習データ永続化機能の実装

## アーキテクチャ概要

### システム構成図

```
┌─────────────────┐
│  WebSocket      │
│  Handler        │
│ (dialogue_      │
│  runner.py)     │
└────────┬────────┘
         │
         │ Session End Event
         ▼
┌─────────────────┐
│ Firestore       │
│ Session Service │
└────────┬────────┘
         │
         │ Get Session Data
         ▼
┌─────────────────┐      ┌─────────────────┐
│ BigQuery        │──┬──▶│ dialogue_       │
│ Data Service    │  │   │ sessions        │
└─────────────────┘  │   └─────────────────┘
                     │
                     ├──▶┌─────────────────┐
                     │   │ learning_       │
                     │   │ history         │
                     │   └─────────────────┘
                     │
                     └──▶┌─────────────────┐
                         │ learning_       │
                         │ profile_        │
                         │ snapshots       │
                         └─────────────────┘
```

### データフロー

1. **セッション中**: Firestoreにリアルタイムデータを保存
2. **セッション終了時**: WebSocketハンドラが終了イベントを検知
3. **データ取得**: FirestoreSessionServiceからセッションデータを取得
4. **BigQuery保存**: BigQueryDataServiceが3つのテーブルに保存
5. **非同期処理**: BigQuery保存は非同期で実行（ユーザー応答をブロックしない）

---

## 技術選定

### BigQueryクライアントライブラリ

**選定**: `google-cloud-bigquery>=3.10.0`

**理由**:
- 公式Googleライブラリ（最新機能サポート）
- `insert_rows_json()` によるバッチインサート対応
- 非同期処理サポート（`asyncio`との統合）
- BigQuery Emulator対応（テスト環境）

### スキーマバリデーション

**選定**: Pydantic v2

**理由**:
- FastAPIプロジェクトで既に使用
- 型安全性、自動バリデーション
- BigQueryスキーマとの親和性

### リトライロジック

**選定**: `tenacity>=8.0.0`（既存依存関係）

**理由**:
- デコレーターベースのシンプルなAPI
- 指数バックオフ、最大試行回数の設定が容易
- 既存プロジェクトで使用実績あり

---

## データ設計

### BigQueryスキーマ（既存）

#### dialogue_sessions テーブル

**パーティション**: `start_time` (DAY)
**クラスタリング**: `user_id`

```sql
CREATE TABLE dialogue_sessions (
  session_id STRING NOT NULL,
  user_id STRING NOT NULL,
  problem STRING,
  start_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP,
  dialogue_turns ARRAY<STRUCT<
    turn_id INT64,
    speaker STRING,
    content STRING,
    timestamp TIMESTAMP,
    emotion STRING
  >>,
  total_hints_used INT64,
  self_solved_count INT64,
  total_points INT64
)
PARTITION BY DATE(start_time)
CLUSTER BY user_id;
```

#### learning_history テーブル

**パーティション**: `attempted_at` (DAY)
**クラスタリング**: `user_id`, `problem_id`

```sql
CREATE TABLE learning_history (
  id STRING NOT NULL,
  user_id STRING NOT NULL,
  problem_id STRING NOT NULL,
  subject STRING,
  grade_level INT64,
  attempted_at TIMESTAMP NOT NULL,
  solved_independently BOOL,
  hints_used INT64,
  time_spent_seconds INT64,
  points_earned INT64,
  session_id STRING
)
PARTITION BY DATE(attempted_at)
CLUSTER BY user_id, problem_id;
```

#### learning_profile_snapshots テーブル

**パーティション**: `snapshot_at` (DAY)
**クラスタリング**: `user_id`

```sql
CREATE TABLE learning_profile_snapshots (
  id STRING NOT NULL,
  user_id STRING NOT NULL,
  snapshot_at TIMESTAMP NOT NULL,
  persistence_score FLOAT64,
  independence_score FLOAT64,
  reflection_quality FLOAT64,
  hint_dependency FLOAT64,
  subject_understanding ARRAY<STRUCT<
    subject STRING,
    topic STRING,
    level STRING,
    trend STRING
  >>
)
PARTITION BY DATE(snapshot_at)
CLUSTER BY user_id;
```

### Pydanticスキーマ

#### backend/app/schemas/bigquery.py

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class DialogueTurnBQ(BaseModel):
    """BigQuery用の対話ターンスキーマ"""
    turn_id: int
    speaker: str  # 'user' | 'assistant'
    content: str
    timestamp: datetime
    emotion: Optional[str] = None


class DialogueSessionBQ(BaseModel):
    """BigQuery用のセッションスキーマ"""
    session_id: str
    user_id: str
    problem: str
    start_time: datetime
    end_time: Optional[datetime] = None
    dialogue_turns: list[DialogueTurnBQ] = Field(default_factory=list)
    total_hints_used: int = 0
    self_solved_count: int = 0
    total_points: int = 0


class LearningHistoryBQ(BaseModel):
    """BigQuery用の学習履歴スキーマ"""
    id: str
    user_id: str
    problem_id: str
    subject: str
    grade_level: int
    attempted_at: datetime
    solved_independently: bool
    hints_used: int
    time_spent_seconds: int
    points_earned: int
    session_id: str


class SubjectUnderstandingBQ(BaseModel):
    """BigQuery用の科目別理解度スキーマ"""
    subject: str
    topic: str
    level: str  # 'beginner' | 'intermediate' | 'advanced'
    trend: str  # 'improving' | 'stable' | 'declining'


class LearningProfileSnapshotBQ(BaseModel):
    """BigQuery用の学習プロファイルスナップショットスキーマ"""
    id: str
    user_id: str
    snapshot_at: datetime
    persistence_score: float
    independence_score: float
    reflection_quality: float
    hint_dependency: float
    subject_understanding: list[SubjectUnderstandingBQ] = Field(default_factory=list)
```

---

## API設計

### BigQueryDataService クラス

#### backend/app/services/bigquery/bigquery_service.py

```python
from typing import Optional
from google.cloud import bigquery
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog

from app.schemas.bigquery import (
    DialogueSessionBQ,
    LearningHistoryBQ,
    LearningProfileSnapshotBQ,
)

logger = structlog.get_logger()


class BigQueryDataService:
    """BigQueryへの学習データ永続化サービス"""

    def __init__(
        self,
        project_id: str,
        dataset_id: str = "homework_coach",
        client: Optional[bigquery.Client] = None,
    ):
        """
        Args:
            project_id: GCPプロジェクトID
            dataset_id: BigQueryデータセットID（デフォルト: homework_coach）
            client: BigQueryクライアント（テスト用にモック可能）
        """
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.client = client or bigquery.Client(project=project_id)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def save_session_data(self, session_data: DialogueSessionBQ) -> None:
        """セッションデータをBigQueryに保存

        Args:
            session_data: セッションデータ

        Raises:
            Exception: BigQuery保存失敗時
        """
        table_id = f"{self.project_id}.{self.dataset_id}.dialogue_sessions"
        rows_to_insert = [session_data.model_dump(mode="json")]

        errors = self.client.insert_rows_json(table_id, rows_to_insert)
        if errors:
            logger.error("bigquery_insert_failed", table="dialogue_sessions", errors=errors)
            raise Exception(f"BigQuery insert failed: {errors}")

        logger.info("bigquery_insert_success", table="dialogue_sessions", session_id=session_data.session_id)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def save_learning_history(self, history_data: LearningHistoryBQ) -> None:
        """学習履歴をBigQueryに保存

        Args:
            history_data: 学習履歴データ

        Raises:
            Exception: BigQuery保存失敗時
        """
        table_id = f"{self.project_id}.{self.dataset_id}.learning_history"
        rows_to_insert = [history_data.model_dump(mode="json")]

        errors = self.client.insert_rows_json(table_id, rows_to_insert)
        if errors:
            logger.error("bigquery_insert_failed", table="learning_history", errors=errors)
            raise Exception(f"BigQuery insert failed: {errors}")

        logger.info("bigquery_insert_success", table="learning_history", history_id=history_data.id)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def save_learning_profile_snapshot(
        self, snapshot_data: LearningProfileSnapshotBQ
    ) -> None:
        """学習プロファイルスナップショットをBigQueryに保存

        Args:
            snapshot_data: プロファイルスナップショットデータ

        Raises:
            Exception: BigQuery保存失敗時
        """
        table_id = f"{self.project_id}.{self.dataset_id}.learning_profile_snapshots"
        rows_to_insert = [snapshot_data.model_dump(mode="json")]

        errors = self.client.insert_rows_json(table_id, rows_to_insert)
        if errors:
            logger.error("bigquery_insert_failed", table="learning_profile_snapshots", errors=errors)
            raise Exception(f"BigQuery insert failed: {errors}")

        logger.info("bigquery_insert_success", table="learning_profile_snapshots", snapshot_id=snapshot_data.id)

    async def save_all(
        self,
        session_data: DialogueSessionBQ,
        history_data: LearningHistoryBQ,
        snapshot_data: LearningProfileSnapshotBQ,
    ) -> None:
        """セッション終了時の全データを一括保存

        Args:
            session_data: セッションデータ
            history_data: 学習履歴データ
            snapshot_data: プロファイルスナップショットデータ
        """
        await self.save_session_data(session_data)
        await self.save_learning_history(history_data)
        await self.save_learning_profile_snapshot(snapshot_data)
```

### セッション終了時の統合

#### backend/app/api/v1/dialogue_runner.py（統合ポイント）

```python
async def _save_session_to_bigquery(self, session_id: str) -> None:
    """セッション終了時にBigQueryに保存（非同期）

    Args:
        session_id: セッションID
    """
    try:
        # Firestoreからセッションデータを取得
        context = self.session_service.get_session(session_id)
        if context is None:
            logger.warning("session_not_found_for_bigquery", session_id=session_id)
            return

        # BigQueryスキーマに変換
        session_data = DialogueSessionBQ(
            session_id=session_id,
            user_id=context.user_id,
            problem=context.problem,
            start_time=context.start_time,
            end_time=datetime.utcnow(),
            dialogue_turns=[...],  # 変換ロジック
            total_hints_used=context.total_hints_used,
            self_solved_count=context.self_solved_count,
            total_points=context.total_points,
        )

        history_data = LearningHistoryBQ(...)  # 変換ロジック
        snapshot_data = LearningProfileSnapshotBQ(...)  # 変換ロジック

        # BigQueryに保存
        await self.bigquery_service.save_all(session_data, history_data, snapshot_data)

    except Exception as e:
        logger.error("bigquery_save_failed", session_id=session_id, error=str(e))
        # エラーでもセッション終了は継続（非同期処理のため）
```

---

## ファイル構成

```
backend/
├── app/
│   ├── schemas/
│   │   └── bigquery.py                  # ← NEW: BigQuery用Pydanticスキーマ
│   ├── services/
│   │   ├── bigquery/                    # ← NEW: BigQueryサービスモジュール
│   │   │   ├── __init__.py
│   │   │   └── bigquery_service.py      # ← NEW: BigQueryDataService
│   │   └── adk/
│   │       └── sessions/
│   │           └── firestore_session_service.py  # ← MODIFY: セッション終了フック追加
│   └── api/
│       └── v1/
│           └── dialogue_runner.py       # ← MODIFY: BigQuery保存統合
└── tests/
    ├── unit/
    │   ├── schemas/
    │   │   └── test_bigquery.py         # ← NEW: スキーマテスト
    │   └── services/
    │       └── bigquery/                # ← NEW: BigQueryサービステスト
    │           ├── __init__.py
    │           └── test_bigquery_service.py
    └── integration/
        └── test_bigquery_integration.py  # ← NEW: BigQuery統合テスト
```

---

## 依存関係

### 追加パッケージ

**backend/pyproject.toml**

```toml
[project]
dependencies = [
    # ... 既存の依存関係 ...
    "google-cloud-bigquery>=3.10.0",  # ← NEW
]
```

### 既存パッケージ（再利用）

- `google-cloud-firestore>=2.0.0` - Firestoreセッション取得
- `tenacity>=8.0.0` - リトライロジック
- `pydantic>=2.0.0` - スキーマバリデーション
- `structlog` - 構造化ログ

---

## エラーハンドリング

### リトライ戦略

```python
@retry(
    stop=stop_after_attempt(3),           # 最大3回試行
    wait=wait_exponential(multiplier=1, min=2, max=10),  # 指数バックオフ（2秒〜10秒）
)
async def save_session_data(self, session_data: DialogueSessionBQ) -> None:
    # ...
```

### エラーログ

```python
logger.error(
    "bigquery_insert_failed",
    table="dialogue_sessions",
    session_id=session_data.session_id,
    errors=errors,
    exc_info=True,  # スタックトレース含む
)
```

### 非同期処理での例外ハンドリング

```python
async def _save_session_to_bigquery(self, session_id: str) -> None:
    try:
        await self.bigquery_service.save_all(...)
    except Exception as e:
        logger.error("bigquery_save_failed", session_id=session_id, error=str(e))
        # エラーでもセッション終了は継続（非ブロッキング）
```

---

## セキュリティ考慮事項

### 認証・認可

1. **Service Account認証**
   - BigQueryクライアント初期化時にService Account使用
   - 環境変数 `GOOGLE_APPLICATION_CREDENTIALS` でキーファイル指定

2. **Secret Manager統合**
   - 本番環境では認証情報をSecret Managerから取得
   - ローカル開発ではローカルキーファイル使用

### 個人情報（PII）保護

1. **ログ出力制限**
   - 対話内容（`content`フィールド）はログに出力しない
   - session_id、user_idのみログ出力

2. **データ保持期間**
   - BigQueryパーティションの自動削除設定（Terraform定義）
   - 90日以上経過したデータは自動削除（GDPR対応）

### IAMロール

```hcl
# infrastructure/terraform/modules/bigquery/iam.tf
resource "google_bigquery_dataset_iam_member" "backend_writer" {
  dataset_id = google_bigquery_dataset.homework_coach.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:backend-sa@${var.project_id}.iam.gserviceaccount.com"
}
```

---

## パフォーマンス考慮事項

### 非同期処理

```python
# セッション終了応答を500ms以内に返す
asyncio.create_task(self._save_session_to_bigquery(session_id))
```

### バッチインサート

```python
# 複数行を一度にインサート（将来の最適化）
rows_to_insert = [session_data.model_dump(mode="json")]
errors = self.client.insert_rows_json(table_id, rows_to_insert)
```

### クエリ最適化（Phase 2）

```sql
-- パーティション・クラスタリング活用
SELECT *
FROM `homework_coach.dialogue_sessions`
WHERE DATE(start_time) = '2026-02-15'  -- パーティションプルーニング
  AND user_id = 'user123'              -- クラスタリング活用
```

---

## 代替案と採用理由

### 代替案1: Firestoreのみで完結

**却下理由**:
- Firestoreは分析クエリに不向き（集計コストが高い）
- 長期データ保存のコストがBigQueryより高い
- データウェアハウスとしての機能不足

### 代替案2: Cloud SQLへの保存

**却下理由**:
- 分析クエリのパフォーマンスがBigQueryに劣る
- スケーラビリティの懸念（大量データ）
- パーティショニング・クラスタリングの柔軟性が低い

### 採用: BigQuery

**理由**:
- データウェアハウスとして最適
- パーティショニング・クラスタリングによる効率的なクエリ
- コスト最適化（ストレージ＆クエリ従量課金）
- 既にTerraformで定義済み

---

## テスト戦略

### ユニットテスト

**対象**: `BigQueryDataService`クラス

```python
# tests/unit/services/bigquery/test_bigquery_service.py
@pytest.fixture
def mock_bigquery_client():
    return MagicMock(spec=bigquery.Client)

async def test_save_session_data_success(mock_bigquery_client):
    service = BigQueryDataService(
        project_id="test-project",
        client=mock_bigquery_client,
    )
    session_data = DialogueSessionBQ(...)

    mock_bigquery_client.insert_rows_json.return_value = []  # 成功

    await service.save_session_data(session_data)

    mock_bigquery_client.insert_rows_json.assert_called_once()
```

### 統合テスト（BigQuery Emulator）

**対象**: エンドツーエンドの保存・取得フロー

```python
# tests/integration/test_bigquery_integration.py
@pytest.fixture
def bigquery_emulator():
    # BigQuery Emulatorのセットアップ（Docker）
    pass

async def test_save_and_query_session_data(bigquery_emulator):
    service = BigQueryDataService(project_id="test-project")
    session_data = DialogueSessionBQ(...)

    await service.save_session_data(session_data)

    # クエリで取得して検証
    query = f"SELECT * FROM `test-project.homework_coach.dialogue_sessions` WHERE session_id = '{session_data.session_id}'"
    result = service.client.query(query).result()
    assert len(list(result)) == 1
```

### E2Eテスト

**対象**: セッション終了→BigQuery保存の確認

```python
# frontend/e2e/tests/functional/bigquery-persistence.spec.ts
test('セッション終了後にBigQueryに保存される', async ({ page }) => {
  // セッション作成→対話→終了
  await page.goto('/session')
  await page.fill('[data-testid="problem-input"]', '1 + 1 = ?')
  await page.click('[data-testid="end-session"]')

  // BigQueryに保存されることを確認（APIで検証）
  const response = await fetch('/api/v1/test/bigquery-verify')
  expect(response.ok).toBe(true)
})
```

---

## マイグレーション計画

### Phase 1: 実装（本PR）

1. `google-cloud-bigquery` 依存関係追加
2. `BigQueryDataService` 実装
3. セッション終了時の統合
4. テスト実装

### Phase 2: 統計取得API（将来）

1. `get_user_stats()` 実装
2. RESTエンドポイント追加
3. Firestoreキャッシング

### Phase 3: Phase 2テーブル統合（マルチエージェント導入後）

1. `agent_metrics` 保存
2. `emotion_analysis` 保存
3. `rag_metrics` 保存

---

## 参考実装

### FirestoreSessionService（既存）

**ファイル**: `backend/app/services/adk/sessions/firestore_session_service.py`

**参考ポイント**:
- ADK `BaseSessionService` の継承パターン
- Firestore Async Client使用
- セッション・イベント・状態の永続化実装
- エラーハンドリングパターン

---

## 承認

- **設計者**: Claude Code
- **設計日**: 2026-02-15
- **レビュー者**: （ユーザー承認）
- **承認日**: （未承認）
