# File Structure Rules

**このルールは、ファイル・ディレクトリの作成・配置に対して強制的に適用されます。**

---

## ディレクトリ命名規則

| タイプ | 規則 | 例 |
|--------|------|-----|
| フロントエンド | kebab-case | `voice-interface/`, `audio-visualizer/` |
| バックエンド | snake_case | `auth_service/`, `adk_tools/` |
| Next.js ルート | kebab-case | `login/`, `session/` |
| ルートグループ | (kebab-case) | `(auth)/`, `(main)/` |

---

## ファイル命名規則

### TypeScript/TSX

| ファイルタイプ | 規則 | 例 |
|--------------|------|-----|
| コンポーネント | PascalCase | `VoiceInterface.tsx` |
| フック | camelCase（use始まり） | `useWebSocket.ts` |
| ユーティリティ | camelCase | `formatDate.ts` |
| 型定義 | camelCase | `session.ts` |
| テスト | *.test.tsx | `VoiceInterface.test.tsx` |

### Python

| ファイルタイプ | 規則 | 例 |
|--------------|------|-----|
| モジュール | snake_case | `auth_service.py` |
| テスト | test_*.py | `test_auth_service.py` |

---

## 変数命名規則

### TypeScript

```typescript
// 変数: camelCase
const sessionId = 'abc123';

// 定数: UPPER_SNAKE_CASE
const MAX_AUDIO_LENGTH = 30000;

// 型/インターフェース: PascalCase
type SessionData = { id: string };
interface VoiceInterfaceProps { }

// Enum: PascalCase
enum CharacterType { Robot = 'robot' }
```

### Python

```python
# 変数: snake_case
session_id = 'abc123'

# 定数: UPPER_SNAKE_CASE
MAX_AUDIO_LENGTH = 30000

# クラス: PascalCase
class SessionService:
    pass

# 関数: snake_case
def create_session(user_id: str) -> Session:
    pass

# Private: _で始まる
def _internal_helper():
    pass
```

---

## フロントエンド配置ルール

### コンポーネント構成

```
components/features/VoiceInterface/
├── VoiceInterface.tsx          # メインコンポーネント
├── VoiceInterface.test.tsx     # テスト
├── AudioVisualizer.tsx         # サブコンポーネント
├── useVoiceRecorder.ts         # カスタムフック
└── index.ts                    # エクスポート集約
```

**必須事項:**
- 1ファイル1コンポーネント原則
- 各フィーチャーディレクトリに `index.ts` でエクスポート集約
- テストファイルは同じディレクトリに配置

### index.ts パターン

```typescript
export { VoiceInterface } from './VoiceInterface';
export { AudioVisualizer } from './AudioVisualizer';
export { useVoiceRecorder } from './useVoiceRecorder';
```

---

## バックエンド配置ルール

### サービス層構成

```
app/services/
├── base_service.py          # 基底サービスクラス
├── auth_service.py
├── session_service.py
└── adk/
    ├── __init__.py
    ├── agent.py
    └── tools.py
```

### テスト構成

```
tests/
├── unit/
│   ├── services/
│   │   └── test_auth_service.py
│   └── api/
│       └── test_auth_endpoints.py
├── integration/
│   └── test_session_flow.py
└── conftest.py              # Pytest fixtures
```

---

## セキュリティ: .gitignore必須設定

以下のファイルは**絶対にGitにコミットしない:**

```gitignore
# 環境変数
.env
.env.local
.env.*.local

# 秘密鍵
*.key
*.pem
*.p12

# サービスアカウント
*-service-account.json
firebase-adminsdk-*.json

# ビルド成果物
frontend/.next/
backend/__pycache__/

# 依存関係
frontend/node_modules/
backend/.venv/
```

**ファイルパーミッション:**
```bash
chmod 600 *-service-account.json
chmod 600 .env .env.local
```

---

## チェックリスト

### 新規コンポーネント追加時

- [ ] コンポーネントファイル作成（`*.tsx`）
- [ ] テストファイル作成（`*.test.tsx`）
- [ ] `index.ts` でエクスポート
- [ ] 型定義を `types/` に追加（必要に応じて）

### 新規APIエンドポイント追加時

- [ ] エンドポイント実装（`app/api/v1/*.py`）
- [ ] スキーマ定義（`app/schemas/*.py`）
- [ ] サービス層実装（`app/services/*_service.py`）
- [ ] ユニットテスト作成（`tests/unit/`）

### 環境変数追加時

- [ ] `.env.example` に追加
- [ ] `.env.local.example` に追加（フロントエンド）
- [ ] `app/core/config.py` に設定項目追加（バックエンド）
- [ ] Secret Managerに登録（本番環境）

---

## 禁止事項

1. **命名規則違反** - 上記規則に従わないファイル名・変数名
2. **機密情報のコミット** - .env、秘密鍵、サービスアカウント
3. **index.tsなしのfeatureディレクトリ** - 必ずエクスポート集約
4. **テストなしのコンポーネント/サービス追加** - TDD必須
