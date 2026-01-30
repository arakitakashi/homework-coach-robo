# 宿題コーチロボット - 開発ガイドライン

**Document Version**: 1.9
**Last Updated**: 2026-01-31
**Status**: Active

---

## 目次

1. [開発の基本方針](#1-開発の基本方針)
   - 1.1 [全ての開発はテストから始める](#11-全ての開発はテストから始める)
   - 1.2 [なぜTDDなのか](#12-なぜtddなのか)
   - 1.3 [必ずブランチを切ってプルリクエストを作成する](#13-必ずブランチを切ってプルリクエストを作成する)
2. [テスト駆動開発（TDD）](#2-テスト駆動開発tdd)
3. [コーディング規約](#3-コーディング規約)
4. [命名規則](#4-命名規則)
5. [スタイリング規約](#5-スタイリング規約)
6. [テスト規約](#6-テスト規約)
7. [Git規約とレビュープロセス](#7-git規約とレビュープロセス)
8. [セキュリティガイドライン](#8-セキュリティガイドライン)

---

## 1. 開発の基本方針

### 1.1 全ての開発はテストから始める

このプロジェクトでは、**テスト駆動開発（TDD）を徹底**します。コードを書く前に必ずテストを書き、テストファーストの開発を実践します。

**基本原則:**

- **テストなしにコードを書かない**: 実装コードを書く前に、必ず失敗するテストを書く
- **小さいステップで進める**: 一度に多くの機能を実装せず、小さく確実に進める
- **リファクタリングを恐れない**: テストがあるからこそ、安心してリファクタリングできる
- **動作するきれいなコード**: テストを通すだけでなく、きれいなコードを保つ

### 1.2 なぜTDDなのか

TDDを実践することで、以下のメリットが得られます：

1. **高品質なコード**: バグの早期発見、仕様の明確化
2. **設計の改善**: テストしやすいコードは、疎結合で保守性が高い
3. **安心感**: リファクタリングや機能追加時に既存機能の破壊を防ぐ
4. **ドキュメント**: テストコードが仕様書・ドキュメントとして機能する
5. **開発速度の向上**: 長期的にはデバッグ時間が減り、開発が加速する

### 1.3 必ずブランチを切ってプルリクエストを作成する

**基本原則:**

- **機能開発は必ず専用ブランチで行う**: `main`や`develop`ブランチに直接コミットしない
- **すべての変更はプルリクエストを経由する**: レビュープロセスを省略しない
- **Git Workflow skillを参照する**: ブランチ作成、コミット、PR作成時は必ず `/git-workflow` スキルを参照

**実施方法:**

1. 新機能開発や修正を始める前に、適切な命名規則でブランチを作成
   ```bash
   git checkout -b feature/awesome-new-feature
   ```

2. Git Workflow skillを参照して、適切なブランチ戦略とコミットメッセージを確認
   ```
   /git-workflow
   ```

3. 実装完了後、プルリクエストを作成してコードレビューを依頼

4. レビュー承認後、マージを実行

**詳細は `/git-workflow` スキルを参照してください。**

---

## 2. テスト駆動開発（TDD）

**重要**: 実装開始時は、必ず**TDD skill**を参照してください。

### 2.1 TDD Skillの使用

このプロジェクトでは、和田卓人（t_wada）が提唱するテスト駆動開発を徹底します。

実装時は以下のコマンドでTDD skillを呼び出してください：

```
/tdd
```

TDD skillには以下が含まれます：

- **Red-Green-Refactor**サイクルの詳細解説
- **仮実装・三角測量・明白な実装**の3つの戦略
- **TODOリスト駆動開発**
- **ベイビーステップ**の実践方法
- 3段階ヒントシステムの実装例（完全なコード付き）
- TDDベストプラクティス
- バックエンド（FastAPI + pytest）でのTDD
- TDDで困った時のQ&A
- TDDチェックリスト

**テストカバレッジ目標: 80%以上**

---

## 3. コーディング規約

### 3.1 フロントエンド（TypeScript / React）

**重要**: フロントエンド実装時は、必ず**Frontend skill**を参照してください。

#### Frontend Skillの使用

フロントエンド開発の詳細なガイドラインは専用スキルに分離されています。

以下のコマンドでFrontend skillを呼び出してください：

```
/frontend
```

Frontend skillには以下が含まれます：

- **プロジェクト構造**: Next.js App Routerのディレクトリ構成
- **TypeScript型定義**: 型安全性、Utility Types、型エクスポート
- **React コンポーネント規約**: 関数コンポーネント、Server/Client Components、カスタムフック
- **命名規則**: ファイル、変数、関数、型・インターフェースの命名
- **Tailwind CSS**: ユーティリティクラス、レスポンシブデザイン、ダークモード対応
- **アクセシビリティ**: ARIA属性、キーボードナビゲーション
- **Vitest + Testing Library**: コンポーネントテスト、フックテスト
- **Zod バリデーション**: フォームバリデーション、型推論
- **状態管理**: Jotai atoms、派生atom、永続化
- **エラーハンドリング**: Error Boundaries、非同期エラー処理

#### 基本原則

このプロジェクトでは、以下のフロントエンド開発原則を常に遵守します：

1. **型安全性を最優先**: `any`型の使用を避け、明示的な型定義を行う
2. **関数型プログラミング**: 副作用を最小化し、純粋関数を優先
3. **宣言的なコード**: 命令的ではなく宣言的なコードを書く
4. **コンポーネントの単一責任**: 1つのコンポーネントは1つの責任のみを持つ
5. **パフォーマンス最適化**: Vercelのベストプラクティスに従う（`/vercel-react-best-practices` も参照）

**詳細な実装パターンとコード例は `/frontend` skillを参照してください。**

### 3.2 バックエンド（Python / FastAPI）

**重要**: FastAPI実装時は、必ず**FastAPI skill**を参照してください。

#### FastAPI Skillの使用

実装時は以下のコマンドでFastAPI skillを呼び出してください：

```
/fastapi
```

FastAPI skillには以下が含まれます：

- **プロジェクト構造**（ドメインベース）
- **Firestore統合**パターン
- **JWT認証**の実装方法
- **Pydantic v2**のベストプラクティス
- **7つの既知の問題**と予防策
- CORS、バリデーション、非同期処理のパターン
- テストとデプロイメント

#### 基本原則

- **型ヒントを必ず使用**: 全ての関数・メソッドに型ヒント
- **非同期処理**: I/O処理は`async/await`を使用
- **依存性注入**: FastAPIのDependency Injectionを活用
- **エラーハンドリング**: 適切な例外処理とHTTPステータスコード

#### Pythonコーディング規約

**PEP 8準拠:**

```python
# ✅ 良い例: PEP 8準拠
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class DialogueTurn(BaseModel):
    """対話のターンを表すモデル"""
    turn_id: str
    speaker: str
    content: str
    timestamp: datetime
    emotion: Optional[str] = None

def create_dialogue_turn(
    speaker: str,
    content: str,
    emotion: Optional[str] = None
) -> DialogueTurn:
    """
    新しい対話ターンを作成する

    Args:
        speaker: 話者（'child' or 'ai'）
        content: 発話内容
        emotion: 感情状態（オプション）

    Returns:
        作成された DialogueTurn インスタンス
    """
    return DialogueTurn(
        turn_id=generate_id(),
        speaker=speaker,
        content=content,
        timestamp=datetime.now(),
        emotion=emotion
    )

# ❌ 悪い例: PEP 8違反
def createDialogueTurn(speaker,content,emotion=None):
    return DialogueTurn(turn_id=generate_id(),speaker=speaker,content=content,timestamp=datetime.now(),emotion=emotion)
```

**型ヒントの徹底:**

```python
from typing import Optional, List, Dict, Any

# ✅ 良い例: 完全な型ヒント
async def get_session(session_id: str, db: FirestoreClient) -> Optional[Session]:
    """セッションを取得する"""
    # 実装は FastAPI skill を参照

# ❌ 悪い例: 型ヒントなし
async def get_session(session_id, db):
    # 型情報が欠落
```

**詳細な実装例は `/fastapi` skillを参照してください。**

---

## 4. 命名規則

**注**: フロントエンドの命名規則については `/frontend` スキルを参照してください。

### 4.1 バックエンド（Python）

#### ファイル命名

```
app/
├── dialogue_engine.py          # snake_case
├── hint_system.py              # snake_case
└── emotion_analyzer.py         # snake_case
```

#### 変数・関数命名

```python
# 変数: snake_case
session_id = 'abc123'
is_recording = False
audio_level = 0.5

# 定数: UPPER_SNAKE_CASE
MAX_AUDIO_LEVEL = 100
DEFAULT_CHARACTER = 'robot'
API_BASE_URL = os.getenv('API_BASE_URL')

# 関数: snake_case
def create_session(user_id: str) -> Session:
    pass

async def fetch_user_data(user_id: str) -> User:
    pass

# Boolean変数: is/has/canプレフィックス
is_loading = True
has_error = False
can_submit = True

# プライベート関数・変数: _プレフィックス
def _internal_helper(data: str) -> str:
    pass

_private_constant = 'internal'
```

#### クラス命名

```python
# クラス: PascalCase
class DialogueEngine:
    pass

class HintSystem:
    pass

# 例外クラス: Error/Exceptionサフィックス
class SessionNotFoundError(Exception):
    pass

class ValidationError(ValueError):
    pass

# Pydanticモデル: PascalCase
class SessionCreate(BaseModel):
    user_id: str
    character: str

class SessionResponse(BaseModel):
    id: str
    user_id: str
    status: str
```

---

## 5. スタイリング規約

**注**: フロントエンドのスタイリング規約（Tailwind CSS、アクセシビリティ）については `/frontend` スキルを参照してください。

### 5.1 コードフォーマット

#### フロントエンド（Prettier）

```json
// .prettierrc
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "arrowParens": "always"
}
```

#### バックエンド（Black + isort）

```toml
# pyproject.toml
[tool.black]
line-length = 100
target-version = ['py310']
include = '\.pyi?$'

[tool.isort]
profile = "black"
line_length = 100
multi_line_output = 3
include_trailing_comma = true
```

---

## 6. テスト規約

**注**: フロントエンドのテスト規約（Vitest、Testing Library、テストパターン）については `/frontend` スキルと `/tdd` スキルを参照してください。

### 6.1 バックエンドテスト

#### テストファイル構成

```
tests/
├── unit/
│   ├── test_dialogue_engine.py
│   └── test_hint_system.py
├── integration/
│   └── test_api_sessions.py
└── conftest.py
```

#### ユニットテスト（pytest）

```python
# tests/unit/test_dialogue_engine.py
import pytest
from app.services.dialogue_engine import DialogueEngine
from app.models.session import Session

@pytest.fixture
def mock_session():
    return Session(
        id='test-session-id',
        user_id='test-user-id',
        character='robot',
        grade_level=2,
        status='active'
    )

@pytest.mark.asyncio
async def test_create_session(mock_db):
    """セッション作成のテスト"""
    engine = DialogueEngine(db=mock_db)
    session = await engine.create_session(
        user_id='test-user-id',
        character='robot',
        grade_level=2
    )

    assert session.id is not None
    assert session.user_id == 'test-user-id'
    assert session.character == 'robot'
    assert session.status == 'active'

@pytest.mark.asyncio
async def test_generate_hint_level_1(mock_session):
    """レベル1ヒント生成のテスト"""
    engine = DialogueEngine(db=mock_db)
    hint = await engine.generate_hint(
        session=mock_session,
        problem="3 + 5 = ?",
        hint_level=1
    )

    assert hint is not None
    assert "問題" in hint or "何" in hint  # 問題理解の確認
    assert len(hint) > 0
```

#### 統合テスト（pytest + TestClient）

```python
# tests/integration/test_api_sessions.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_session():
    """セッション作成APIのテスト"""
    response = client.post(
        "/api/v1/sessions",
        json={
            "userId": "test-user-id",
            "character": "robot",
            "gradeLevel": 2
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["userId"] == "test-user-id"
    assert data["character"] == "robot"
    assert "id" in data

def test_get_session_not_found():
    """存在しないセッションの取得テスト"""
    response = client.get(
        "/api/v1/sessions/nonexistent-id",
        headers={"Authorization": f"Bearer {test_token}"}
    )

    assert response.status_code == 404
    assert "見つかりません" in response.json()["detail"]

def test_get_session_forbidden():
    """他人のセッションへのアクセステスト"""
    # 他のユーザーのセッションを作成
    other_session_response = client.post(
        "/api/v1/sessions",
        json={"userId": "other-user-id", "character": "wizard", "gradeLevel": 1},
        headers={"Authorization": f"Bearer {other_user_token}"}
    )
    other_session_id = other_session_response.json()["id"]

    # 別のユーザーでアクセスを試みる
    response = client.get(
        f"/api/v1/sessions/{other_session_id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )

    assert response.status_code == 403
```

#### テストカバレッジ目標

```bash
# カバレッジ測定
pytest --cov=app --cov-report=html --cov-report=term

# 目標
# - ユニットテスト: 80%以上
# - 統合テスト: 主要API 100%
```

---


## 7. Git規約とレビュープロセス

**重要**: Git操作、ブランチ作成、コミット、プルリクエスト、コードレビューを行う際は、必ず**Git Workflow skill**を参照してください。

### Git Workflow Skillの使用

Git規約とレビュープロセスの詳細は専用スキルに分離されています。

以下のコマンドでGit Workflow skillを呼び出してください：

```
/git-workflow
```

Git Workflow skillには以下が含まれます：

- **Git Flow**ブランチ戦略（main/develop/feature/hotfix）
- **ブランチ命名規則**（feature/fix/refactor/docs）
- **Conventional Commits**形式のコミットメッセージ
- **コミット粒度**のベストプラクティス
- **プルリクエストテンプレート**とタイトル規則
- **コードレビューチェックリスト**
- **レビュープロセス**とマージ基準
- **一般的なGitワークフロー**（feature/bugfix/hotfix）
- **Git設定**推奨事項
- **トラブルシューティング**（reset/rebase/conflicts）

---
## 8. セキュリティガイドライン

**重要**: 認証実装、ユーザー入力処理、API作成、秘密情報管理、クラウドインフラ設定を行う際は、必ず**Security Review skill**を参照してください。

### Security Review Skillの使用

セキュリティガイドラインの詳細は専用スキルに分離されています。

以下のコマンドでSecurity Review skillを呼び出してください：

```
/security-review
```

Security Review skillには以下が含まれます：

- **Secrets Management**: 環境変数、クラウドシークレット管理、ローテーション
- **Input Validation**: Zod/Pydanticバリデーション、ファイルアップロード検証
- **SQL Injection Prevention**: パラメータ化クエリ、ORMの安全な使用
- **Authentication & Authorization**: JWT、httpOnly cookies、Row Level Security
- **XSS Prevention**: HTMLサニタイズ、Content Security Policy
- **CSRF Protection**: トークン検証、SameSite cookies
- **Rate Limiting**: API制限、高負荷操作の保護
- **Sensitive Data Exposure**: ログのリダクション、エラーメッセージの安全化
- **Dependency Security**: npm audit、定期的な更新
- **Pre-Deployment Checklist**: 本番環境デプロイ前の必須チェック項目

### Cloud Infrastructure Security

クラウドインフラ、CI/CD、デプロイ設定に関するセキュリティは、別途以下のドキュメントを参照してください：

```
.claude/skills/security-review/cloud-infrastructure-security.md
```

クラウドセキュリティには以下が含まれます：

- **IAM & Access Control**: 最小権限の原則、MFA
- **Network Security**: VPC、ファイアウォール、セキュリティグループ
- **Logging & Monitoring**: CloudWatch、監査ログ
- **CI/CD Pipeline Security**: OIDC認証、シークレットスキャン、依存関係監査
- **Cloudflare & CDN Security**: WAF、DDoS保護
- **Backup & Disaster Recovery**: 自動バックアップ、復旧テスト

### 基本原則

このプロジェクトでは、以下のセキュリティ原則を常に遵守します：

1. **機密情報はコードに含めない**: すべてのAPIキー、パスワード、トークンは環境変数またはクラウドシークレット管理サービスで管理
2. **すべての入力を検証**: ユーザー入力は必ずバリデーションスキーマで検証
3. **最小権限の原則**: IAMロール、データベースアクセスは必要最小限に
4. **多層防御**: セキュリティは一つの層に依存せず、複数の防御層を構築
5. **セキュアデフォルト**: デフォルト設定は常に最も安全な設定に

**詳細な実装パターンとチェックリストは `/security-review` skillを参照してください。**

---

## 付録

### A. 推奨ツール

**フロントエンド:**
- VS Code Extensions: ESLint, Prettier, Tailwind CSS IntelliSense
- Bun: パッケージマネージャー
- Vitest: テストフレームワーク

**バックエンド:**
- VS Code Extensions: Python, Pylance, Black Formatter
- uv: パッケージマネージャー
- pytest: テストフレームワーク

**共通:**
- Git: バージョン管理
- GitHub Actions: CI/CD
- Cloud Build: デプロイ

### B. 参考資料

**TDD関連:**
- [t_wada: テスト駆動開発](https://twitter.com/t_wada)
- [Test Driven Development: By Example (Kent Beck)](https://www.amazon.co.jp/dp/0321146530)
- [テスト駆動開発 (Kent Beck著、和田卓人訳)](https://www.amazon.co.jp/dp/4274217884)

**フロントエンド:**
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [React Documentation](https://react.dev/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Vitest Documentation](https://vitest.dev/)
- [Testing Library Documentation](https://testing-library.com/)

**バックエンド:**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [pytest Documentation](https://docs.pytest.org/)
- [PEP 8 -- Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

**AI/ML:**
- [Google ADK Documentation](https://google.github.io/adk-docs)
- [Gemini Live API](https://ai.google.dev/gemini-api/docs/live)
- [ADK Python Repository](https://github.com/google/adk-python)
- [ADK Samples](https://github.com/google/adk-samples)

---

## 利用可能なスキル

このプロジェクトには、実装時に活用できるClaudeスキルが用意されています。スキルを使用することで、ベストプラクティスに従った実装が可能になります。

### 開発プロセス

**TDD Skill** (`/tdd`)
- 和田卓人（t_wada）が提唱するTDD原則（完全版）
- Red-Green-Refactorサイクル、仮実装・三角測量・明白な実装
- TODOリスト駆動開発、ベイビーステップ
- **使用タイミング**: 新機能実装開始時、テストファースト開発時

**Git Workflow Skill** (`/git-workflow`)
- Git Flow + Conventional Commits
- ブランチ戦略（feature/fix/hotfix/refactor/docs）
- コミットメッセージ規約（`<type>(<scope>): <subject>`）
- PRテンプレート、コードレビューチェックリスト
- **使用タイミング**: ブランチ作成時、コミット時、PR作成時、レビュー時

**Security Review Skill** (`/security-review`)
- OWASP Top 10対策、セキュリティチェックリスト
- Secrets Management、Input Validation、SQL/XSS/CSRF対策
- 認証・認可、レート制限、データ保護
- 依存関係セキュリティ、デプロイ前チェックリスト
- Cloud Infrastructure Security（IAM、ネットワーク、CI/CD、WAF）
- **使用タイミング**: 認証実装時、API作成時、ユーザー入力処理時、デプロイ前

### フロントエンド開発

**Frontend Skill** (`/frontend`)
- Next.js 14+ (App Router) + TypeScript + React
- コンポーネント規約、命名規則、Tailwind CSS
- Vitest + Testing Library、Zod バリデーション
- **使用タイミング**: フロントエンド実装時、UI開発時、テスト作成時

### バックエンド開発

**FastAPI Skill** (`/fastapi`)
- FastAPI 0.128.0 + Pydantic v2のベストプラクティス
- Firestore統合、JWT認証、プロジェクト構造
- 7つの既知の問題と予防策
- **使用タイミング**: バックエンドAPI実装時、Firestore連携時、認証実装時

**Google ADK Basics Skill** (`/google-adk-basics`)
- Agent Development Kit (ADK) の基礎
- Agent構造規約（root_agent/App patterns）
- プロジェクトセットアップ（uv + Python 3.11+）
- ツール統合、セッション管理、マルチエージェント
- **使用タイミング**: ADKプロジェクトのセットアップ時、Agent構造設計時

**Google ADK Live Skill** (`/google-adk-live`)
- Gemini Live API（Bidi-streaming）の完全ガイド
- リアルタイム音声・動画インタラクション
- LiveRequestQueue + RunConfig、FastAPI + WebSocket統合
- 音声トランスクリプション、セッション再開
- **使用タイミング**: 音声対話エンジン実装時、リアルタイムAI構築時
- **前提**: `/google-adk-basics` の知識が必要

### 推奨される実装フロー

1. **機能設計** → `/tdd` で仕様をテストコードとして記述
2. **バックエンドAPI** → `/fastapi` でAPI実装
3. **フロントエンド** → `/frontend` でUI/UX実装（Next.js + React + TypeScript）
4. **AIエージェント基礎** → `/google-adk-basics` でAgent構造設計
5. **音声対話機能** → `/google-adk-live` でリアルタイム対話実装
6. **セキュリティレビュー** → `/security-review` でセキュリティチェック（認証、入力検証、秘密管理）
7. **テスト実行** → `/tdd` のRed-Green-Refactorサイクルで品質確保
8. **コミット・PR** → `/git-workflow` でGit操作・レビュー

---

## 変更履歴

### v1.9 (2026-01-31)
- **フロントエンド関連記述のスキル分離**
  - フロントエンド規約（TypeScript、React、Tailwind CSS、命名規則、テスト）を`frontend` skillに分離
  - 詳細なコード例（型定義、コンポーネント、フック、Jotai、スタイリング、アクセシビリティ、テスト）を削除
  - セクション3.1を基本原則とskill参照のみに簡素化
  - セクション4.1（命名規則）、5.1（スタイリング規約）、6.1（テスト規約）のフロントエンド部分を削除
  - vercel-react-best-practicesスキルへの参照を追加
  - フロントエンドの5つの基本原則を明記

### v1.8 (2026-01-31)
- **セキュリティガイドラインのスキル分離**
  - セキュリティセクション（旧9.1〜9.6）を`security-review` skillに分離
  - 詳細なコード例（Secrets、Input Validation、XSS、SQL Injection、認証・認可、Rate Limiting）をskillに移行
  - development-guidelines.mdは基本原則のみに簡素化
  - Cloud Infrastructure Securityドキュメントへの参照を追加
  - セキュリティの5つの基本原則を明記
  - 利用可能なスキルセクションに`security-review`を追加
  - 推奨実装フローを8ステップに拡張（セキュリティレビューステップを追加）

### v1.7 (2026-01-31)
- **ブランチ戦略とプルリクエストの必須化**
  - セクション1.3「必ずブランチを切ってプルリクエストを作成する」を追加
  - 機能開発時のブランチ運用ルールを明文化
  - Git Workflow skillの参照を明示
  - 目次にサブセクション詳細を追加

### v1.6 (2026-01-31)
- **スキル分離によるコンパクト化**
  - Git規約とレビュープロセス（旧7,8章）を`git-workflow` skillに分離
  - フロントエンド詳細ガイドラインを`frontend` skillに分離
  - development-guidelines.mdを1488行→1300行程度に削減
  - 利用可能なスキルセクションに`frontend`と`git-workflow`を追加
  - 推奨実装フローを更新（7ステップに拡張）

### v1.5 (2026-01-31)
- **利用可能なスキルセクションを追加**
  - TDD、FastAPI、Google ADK Basics、Google ADK Live skillの説明を追加
  - 推奨される実装フローを記載
  - AI/ML関連の参考資料を追加

### v1.4 (2026-01-31)
- **FastAPI重複記述の削除**
  - development-guidelines.mdからFastAPIの詳細実装例を削除
  - ファイル構成、APIエンドポイント、WebSocket、非同期処理、エラーハンドリングの例を削除
  - FastAPI skillへの参照のみに簡素化
  - FastAPI skill (v1.0) にFirestore統合を含む完全なガイドラインを集約

### v1.3 (2026-01-31)
- **TDD重複記述の削除**
  - development-guidelines.mdからTDDの詳細な記述を削除
  - TDD skillへの参照のみに簡素化
  - TDD skill (v2.0) に完全な和田卓人準拠のガイドラインを集約

### v1.2 (2026-01-29)
- **TDDセクションをskillに移行**
  - TDDの詳細を `.claude/skills/tdd/skill.md` に分離
  - development-guidelines.mdには概要とskill参照方法を記載
  - TDDの実装例、ベストプラクティス、Q&Aをskillに集約

### v1.1 (2026-01-29)
- **TDD（テスト駆動開発）セクションを追加**
  - t_wadaが提唱するTDDの原則を詳細に記載
  - Red-Green-Refactorサイクルの説明
  - 3段階ヒントシステムの実装例
  - TDDベストプラクティス
  - TDD実践のルール（3つの絶対ルール）
  - バックエンドでのTDD実践例
  - TDDチェックリスト
- 開発の基本方針セクションを追加
- 全セクション番号を再構成（TDD追加により繰り下げ）

### v1.0 (2026-01-29)
- 初版作成
- コーディング規約、命名規則、スタイリング規約を定義
- テスト規約、Git規約、レビュープロセスを策定
- セキュリティガイドラインを記載

---

**最終更新**: 2026-01-31
**次回レビュー**: MVP開発開始時
