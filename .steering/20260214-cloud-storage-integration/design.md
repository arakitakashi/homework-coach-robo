# Design - Cloud Storage画像保存統合

## アーキテクチャ概要

### システム構成

```
Frontend (Next.js)
    ↓ Base64 画像データ
Backend API (FastAPI)
    ↓
StorageService
    ├→ Cloud Storage (画像保存)
    └→ Firestore (メタデータ保存)
```

### レイヤー構成

1. **サービス層**: `StorageService` - Cloud Storage 操作を抽象化
2. **データ層**: Firestore - 画像メタデータの永続化
3. **インフラ層**: Cloud Storage - 画像ファイルの永続化

## 技術選定

### Cloud Storage クライアント

**選択**: `google-cloud-storage` Python ライブラリ

**理由**:
- Google 公式ライブラリで信頼性が高い
- 非同期操作（async/await）をサポート
- Signed URL 生成機能を標準提供
- 型ヒント対応

**代替案**: REST API 直接呼び出し → 冗長で保守性が低い

### ファイル検証

**選択**: `python-magic` ライブラリ

**理由**:
- ファイルの magic number を正確に検証
- 拡張子偽装を検知可能
- セキュリティ要件を満たす

**代替案**: MIME type のみで判定 → 拡張子偽装に脆弱

### Signed URL vs Public URL

**選択**: Signed URL（有効期限付き）

**理由**:
- 子供の個人情報保護
- アクセス制御の強化
- 有効期限切れで自動的にアクセス不可

**代替案**: Public URL → セキュリティリスクが高い

## データ設計

### Cloud Storage ファイルパス構造

```
homework-coach-assets/
└── sessions/
    └── {session_id}/
        └── images/
            └── {timestamp}_{uuid}.{ext}
```

**命名規則**:
- `{session_id}`: Firestore セッションID
- `{timestamp}`: アップロード日時（ISO 8601形式）
- `{uuid}`: ランダムなUUID（衝突回避）
- `{ext}`: ファイル拡張子（jpg, png, webp）

**例**: `sessions/abc123/images/20260214T120000_a1b2c3d4.jpg`

### Firestore スキーマ拡張

既存の `sessions/{session_id}` ドキュメントに `uploaded_images` フィールドを追加:

```typescript
{
  session_id: string;
  child_id: string;
  problem: string;
  // ... 既存フィールド
  uploaded_images: [
    {
      storage_path: string;        // Cloud Storage 上のパス
      signed_url: string;           // 一時アクセスURL
      signed_url_expires_at: Timestamp; // URL有効期限
      uploaded_at: Timestamp;       // アップロード日時
      file_size: number;            // バイト単位
      mime_type: string;            // "image/jpeg" など
      width: number | null;         // 将来の拡張用
      height: number | null;        // 将来の拡張用
    }
  ];
}
```

**注意**: `uploaded_images` は配列型で、複数画像のアップロードに対応（将来拡張）

## ファイル構成

### 新規ファイル

```
backend/app/services/
└── storage_service.py           # Cloud Storage サービス実装

backend/app/schemas/
└── storage.py                   # ストレージ関連のスキーマ定義

backend/tests/unit/services/
└── test_storage_service.py      # ユニットテスト
```

### 変更予定ファイル

```
backend/app/core/config.py       # GCS_BUCKET_NAME 環境変数追加
backend/app/core/dependencies.py # StorageService の DI 設定
infrastructure/terraform/modules/iam/main.tf  # IAM権限追加（必要な場合）
```

## クラス設計

### StorageService

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol

@dataclass
class UploadedImage:
    """アップロードされた画像のメタデータ"""
    storage_path: str
    signed_url: str
    signed_url_expires_at: datetime
    uploaded_at: datetime
    file_size: int
    mime_type: str
    width: int | None = None
    height: int | None = None

class StorageService(Protocol):
    """Cloud Storage サービスのインターフェース"""

    async def upload_image(
        self,
        session_id: str,
        image_data: bytes,
        filename: str,
    ) -> UploadedImage:
        """画像をアップロードし、メタデータを返す"""
        ...

    async def generate_signed_url(
        self,
        storage_path: str,
        expires_in: timedelta = timedelta(hours=1),
    ) -> str:
        """Signed URL を生成"""
        ...

    async def validate_image(
        self,
        image_data: bytes,
        max_size_mb: int = 10,
    ) -> tuple[str, int]:
        """画像を検証し、(mime_type, file_size) を返す"""
        ...

class CloudStorageService(StorageService):
    """Cloud Storage 実装"""

    def __init__(
        self,
        bucket_name: str,
        project_id: str | None = None,
    ):
        self.bucket_name = bucket_name
        self.project_id = project_id
        self.client = storage.Client(project=project_id)
        self.bucket = self.client.bucket(bucket_name)

    # 実装...

class MockStorageService(StorageService):
    """テスト用モック実装"""

    # 実装...
```

## 依存関係

### 新規追加パッケージ

```toml
# pyproject.toml
[project.dependencies]
google-cloud-storage = "^2.14.0"
python-magic = "^0.4.27"
Pillow = "^10.2.0"  # 画像サイズ取得用（オプショナル）
```

### 環境変数

```bash
# .env
GCS_BUCKET_NAME="homework-coach-assets"
GCS_PROJECT_ID="homework-coach-robo"  # オプショナル（デフォルト認証から取得）
```

## エラーハンドリング

### カスタム例外

```python
class StorageError(Exception):
    """ストレージ関連のベース例外"""
    pass

class InvalidImageError(StorageError):
    """不正な画像ファイル"""
    pass

class ImageTooLargeError(StorageError):
    """ファイルサイズ超過"""
    pass

class UploadFailedError(StorageError):
    """アップロード失敗"""
    pass
```

### エラーハンドリング戦略

1. **バリデーションエラー**: 即座に拒否、明確なエラーメッセージ
2. **ネットワークエラー**: 3回までリトライ（exponential backoff）
3. **権限エラー**: ログ記録、500エラーで返却

## セキュリティ考慮事項

### 1. 入力検証

- **ファイルタイプ**: magic number で検証（拡張子だけでは不十分）
- **ファイルサイズ**: 10MB制限（メモリ枯渇攻撃防止）
- **ファイル名**: サニタイズ（パストラバーサル攻撃防止）

### 2. アクセス制御

- **Signed URL**: 有効期限1時間
- **最小権限**: サービスアカウントに `storage.objectCreator` のみ付与
- **バケットポリシー**: プライベートバケット（Public Access 禁止）

### 3. データ保護

- **暗号化**: Cloud Storage のデフォルト暗号化を使用
- **個人情報**: 画像に含まれる可能性のある個人情報を考慮
- **ログ**: 画像データ本体をログに出力しない

### 4. IAM 権限

**必要な権限**:
```hcl
# infrastructure/terraform/modules/iam/main.tf
resource "google_project_iam_member" "backend_storage_creator" {
  project = var.project_id
  role    = "roles/storage.objectCreator"
  member  = "serviceAccount:${google_service_account.backend.email}"
}

resource "google_project_iam_member" "backend_storage_viewer" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.backend.email}"
}
```

## パフォーマンス考慮事項

### 1. 非同期処理

- すべての Cloud Storage 操作を `async/await` で実装
- ネットワークI/O中に他のリクエストを処理可能

### 2. ストリーミングアップロード

- 大きな画像（>1MB）はストリーミングアップロードを使用
- メモリ効率的

### 3. リトライロジック

```python
from google.api_core import retry

@retry.Retry(
    initial=1.0,
    maximum=10.0,
    multiplier=2.0,
    predicate=retry.if_transient_error,
)
async def upload_with_retry(...):
    # アップロード処理
```

## テスト戦略

### ユニットテスト

1. **モックテスト**: `MockStorageService` を使用
2. **検証ロジックテスト**: 各種バリデーション
3. **エラーハンドリングテスト**: 異常系

### テストケース

```python
# test_storage_service.py
async def test_upload_valid_jpeg():
    """正常系: JPEG画像のアップロード"""
    ...

async def test_upload_valid_png():
    """正常系: PNG画像のアップロード"""
    ...

async def test_reject_invalid_file_type():
    """異常系: 不正なファイルタイプの拒否"""
    ...

async def test_reject_too_large_file():
    """異常系: ファイルサイズ超過の拒否"""
    ...

async def test_generate_signed_url():
    """正常系: Signed URL生成"""
    ...

async def test_signed_url_expiration():
    """正常系: Signed URL有効期限"""
    ...
```

## 代替案と採用理由

### 代替案1: Firebase Storage を使用

**理由で却下**:
- GCP との統合が Cloud Storage の方が優れている
- Terraform での管理が容易
- コスト効率が良い

### 代替案2: Firestore に画像データを直接保存

**理由で却下**:
- Firestore の1ドキュメント1MB制限
- コストが高い
- パフォーマンスが悪い

### 代替案3: Public URL を使用

**理由で却下**:
- セキュリティリスク（子供の個人情報）
- アクセス制御不可
- Signed URL の方が柔軟

## 実装の優先順位

### Phase 1: コアサービス実装（高優先度）

- `StorageService` インターフェース定義
- `CloudStorageService` 実装
- `MockStorageService` 実装
- ファイル検証ロジック

### Phase 2: 統合（中優先度）

- Firestore 統合
- 環境変数設定
- DI 設定

### Phase 3: セキュリティ強化（高優先度）

- IAM 権限設定
- Signed URL 生成
- エラーハンドリング

### Phase 4: テスト（必須）

- ユニットテスト
- カバレッジ確認
- 品質チェック
