# Design - Vertex AI 統一

## アーキテクチャ概要

### Before（現状）

```
┌─────────────────┐     ┌─────────────────┐
│  開発環境        │     │  本番環境        │
│                 │     │                 │
│  API Key        │     │  Vertex AI      │
│  ↓              │     │  ↓              │
│  genai.Client() │     │  genai.Client() │
│  (api_key=xxx)  │     │  (vertexai=True)│
└─────────────────┘     └─────────────────┘
```

### After（統一後）

```
┌─────────────────────────────────────────┐
│  開発環境 / 本番環境                      │
│                                         │
│  Application Default Credentials (ADC)   │
│  ↓                                       │
│  genai.Client(vertexai=True)             │
│  ↓                                       │
│  Vertex AI Gemini API                    │
└─────────────────────────────────────────┘
```

## 技術選定

### google-genai SDK の Vertex AI モード

`google-genai` SDK は以下の方法で Vertex AI を使用できる：

```python
from google import genai

# 方法1: 環境変数
# GOOGLE_GENAI_USE_VERTEXAI=TRUE
client = genai.Client()

# 方法2: 明示的な指定
client = genai.Client(vertexai=True)
```

### 認証フロー

```
1. Application Default Credentials (ADC) を検索
   ↓
2. 以下の順序で認証情報を探す:
   a. GOOGLE_APPLICATION_CREDENTIALS 環境変数
   b. gcloud auth application-default login の認証情報
   c. Compute Engine / Cloud Run のサービスアカウント
   ↓
3. 認証情報を使用して Vertex AI API を呼び出し
```

## 実装設計

### GeminiClient の変更

```python
class GeminiClient:
    DEFAULT_MODEL = "gemini-2.5-flash"

    def __init__(
        self,
        model: str | None = None,
        system_instruction: str | None = None,
        project: str | None = None,
        location: str = "us-central1",
    ) -> None:
        # プロジェクトIDの解決
        self._project = project or os.environ.get("GOOGLE_CLOUD_PROJECT")
        if not self._project:
            raise ValueError(
                "Google Cloud project is required. "
                "Set GOOGLE_CLOUD_PROJECT environment variable."
            )

        self._location = location
        self._model = model or self.DEFAULT_MODEL
        self._system_instruction = system_instruction

        # Vertex AI モードでクライアント作成
        self._client = genai.Client(
            vertexai=True,
            project=self._project,
            location=self._location,
        )
```

### 環境変数

| 変数名 | 必須 | 説明 |
|--------|------|------|
| `GOOGLE_CLOUD_PROJECT` | ✅ | GCPプロジェクトID |
| `GOOGLE_CLOUD_LOCATION` | ❌ | リージョン（デフォルト: us-central1） |
| `GOOGLE_APPLICATION_CREDENTIALS` | ❌ | サービスアカウントキーパス（ローカル開発時は不要） |

### 削除する環境変数

- `GOOGLE_API_KEY`
- `GEMINI_API_KEY`
- `GOOGLE_GENAI_USE_VERTEXAI`（常にTRUEなので不要）

## API設計

変更なし。`LLMClient` プロトコルは維持。

## ファイル構成

変更対象ファイル：

```
backend/
├── app/
│   ├── api/v1/
│   │   └── dialogue.py          # get_llm_client() の更新
│   └── services/adk/dialogue/
│       └── gemini_client.py     # 認証方式の変更
└── tests/
    ├── unit/services/adk/dialogue/
    │   └── test_gemini_client.py  # テストの更新
    └── integration/api/v1/
        └── test_dialogue_llm.py   # テストの更新
```

## エラーハンドリング

### 認証エラー

```python
try:
    client = genai.Client(vertexai=True, project=project)
except Exception as e:
    if "credentials" in str(e).lower():
        raise RuntimeError(
            "Failed to authenticate with Vertex AI. "
            "Run 'gcloud auth application-default login' to set up credentials."
        ) from e
    raise
```

### プロジェクト未設定エラー

```python
if not project:
    raise ValueError(
        "Google Cloud project is required. "
        "Set GOOGLE_CLOUD_PROJECT environment variable or pass project parameter."
    )
```

## セキュリティ考慮事項

1. **API Key の廃止** - 漏洩リスクのある API Key を使用しない
2. **ADC の使用** - GCP の推奨認証方式
3. **最小権限の原則** - Vertex AI User ロールのみ必要

## パフォーマンス考慮事項

- Vertex AI と直接 Gemini API のレイテンシ差は無視できるレベル
- 認証トークンのキャッシュは SDK が自動管理

## 代替案と採用理由

### 案1: 環境変数で切り替え（不採用）

```python
if os.environ.get("USE_VERTEX_AI"):
    client = genai.Client(vertexai=True)
else:
    client = genai.Client(api_key=api_key)
```

**不採用理由**: コードパスが分岐し、テストの複雑さが増す

### 案2: Vertex AI 統一（採用）

**採用理由**:
- コードパスが単一
- 開発/本番の差異がない
- GCP の推奨認証方式
