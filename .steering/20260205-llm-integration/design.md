# Design - LLM統合

## アーキテクチャ概要

```
┌─────────────────────────────────────────────────────────┐
│                    API Layer                             │
│  dialogue.py (エンドポイント)                            │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                Service Layer                             │
│  SocraticDialogueManager                                │
│    - analyze_response()                                 │
│    - generate_question()                                │
│    - generate_hint_response()                           │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                LLM Client Layer                          │
│  GeminiClient (implements LLMClient Protocol)           │
│    - generate(prompt: str) -> str                       │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              External Service                            │
│  Google Gemini API (gemini-2.5-flash)                   │
└─────────────────────────────────────────────────────────┘
```

## 技術選定

| 項目 | 選定 | 理由 |
|------|------|------|
| LLMモデル | `gemini-2.5-flash` | 高速・低コスト・日本語対応 |
| SDK | `google-genai` | 公式SDK、非同期対応 |
| 非同期 | `client.aio.models.generate_content` | FastAPIとの親和性 |

## クラス設計

### GeminiClient

```python
class GeminiClient:
    """Google Gemini APIクライアント（LLMClientプロトコル準拠）"""

    DEFAULT_MODEL = "gemini-2.5-flash"

    def __init__(
        self,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
    ) -> None:
        """
        Args:
            api_key: Google API Key（Noneの場合は環境変数から取得）
            model: 使用するモデル名
        """

    async def generate(self, prompt: str) -> str:
        """プロンプトからテキストを生成する（LLMClientプロトコル）"""
```

### 設定クラス

```python
class GeminiSettings(BaseSettings):
    """Gemini API設定"""

    google_api_key: str | None = None
    gemini_api_key: str | None = None  # 後方互換性
    gemini_model: str = "gemini-2.5-flash"

    @property
    def api_key(self) -> str | None:
        """APIキーを取得（GOOGLE_API_KEY優先）"""
        return self.google_api_key or self.gemini_api_key

    model_config = SettingsConfigDict(env_file=".env")
```

## ファイル構成

```
backend/app/
├── core/
│   └── config.py              # 設定（既存ファイルに追加）
└── services/
    └── adk/
        └── dialogue/
            ├── gemini_client.py   # 新規: GeminiClient
            └── manager.py         # 既存: LLMクライアント注入
```

## API統合設計

### 依存性注入パターン

```python
# dialogue.py

def get_llm_client() -> LLMClient | None:
    """LLMクライアントのファクトリー（依存性注入用）"""
    settings = GeminiSettings()
    if settings.api_key:
        return GeminiClient(api_key=settings.api_key)
    return None


def get_dialogue_manager(
    llm_client: LLMClient | None = Depends(get_llm_client),
) -> SocraticDialogueManager:
    """SocraticDialogueManagerの依存性注入"""
    return SocraticDialogueManager(llm_client=llm_client)
```

### エラーハンドリング

| エラー | 対応 |
|--------|------|
| APIキー未設定 | フォールバック応答を返す（HTTP 200） |
| LLM応答エラー | HTTPException(503) |
| JSON解析エラー | デフォルト値でResponseAnalysisを構築 |
| タイムアウト | HTTPException(504) |

## セキュリティ考慮事項

1. **APIキー管理**: 環境変数から取得、コードにハードコードしない
2. **ログ出力**: プロンプト・応答をログに出力しない（子供のデータ保護）
3. **入力検証**: プロンプトの長さを制限（DoS防止）

## パフォーマンス考慮事項

1. **モデル選択**: `gemini-2.5-flash` を使用（低レイテンシ）
2. **タイムアウト**: 10秒でタイムアウト
3. **リトライ**: 初回失敗時に1回リトライ

## 代替案と採用理由

### 代替案1: OpenAI GPT-4

**不採用理由**: Google ADKとの統合を見据え、Geminiで統一

### 代替案2: google-cloud-aiplatform (Vertex AI)

**不採用理由**:
- 認証が複雑（サービスアカウント必要）
- `google-genai` SDKがシンプルで開発速度優先

### 代替案3: 同期APIの使用

**不採用理由**: FastAPIの非同期処理と親和性が低い
