# 宿題コーチロボット - 開発ガイドライン

**Document Version**: 2.0
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

バックエンド開発の詳細なガイドラインは専用スキルに分離されています。

以下のコマンドでFastAPI skillを呼び出してください：

```
/fastapi
```

FastAPI skillには以下が含まれます：

- **プロジェクト構造**: ドメインベースのディレクトリ構成
- **Firestore統合**: 接続パターン、CRUD操作、トランザクション
- **JWT認証**: Firebase Admin SDK、認証・認可パターン
- **Pydantic v2**: モデル定義、バリデーション、型変換
- **7つの既知の問題**: よくある問題と予防策
- **CORS・バリデーション・非同期処理**: ベストプラクティス
- **テストとデプロイメント**: pytest、TestClient、Cloud Run

#### 基本原則

このプロジェクトでは、以下のバックエンド開発原則を常に遵守します：

1. **型ヒントを必ず使用**: 全ての関数・メソッドに型ヒントを付与
2. **非同期処理**: I/O処理は`async/await`を使用
3. **依存性注入**: FastAPIのDependency Injectionを活用
4. **エラーハンドリング**: 適切な例外処理とHTTPステータスコード
5. **PEP 8準拠**: Pythonコーディング規約を遵守

**詳細な実装パターンとコード例は `/fastapi` skillを参照してください。**

---

## 4. 命名規則

**注**:
- フロントエンドの命名規則については `/frontend` スキルを参照
- バックエンド（Python）の命名規則については `/fastapi` スキルを参照

---

## 5. スタイリング規約

**注**:
- フロントエンドのスタイリング規約（Tailwind CSS、アクセシビリティ、Prettier）については `/frontend` スキルを参照
- バックエンドのコードフォーマット（Black、isort）については `/fastapi` スキルを参照

---

## 6. テスト規約

**重要**: テスト実装時は、必ず**TDD skill**と各技術スタックのskillを参照してください。

### テストの基本方針

このプロジェクトでは、以下のテスト方針を常に遵守します：

1. **テスト駆動開発（TDD）**: 実装前に必ずテストを書く（Red-Green-Refactorサイクル）
2. **テストカバレッジ**: 80%以上を維持
3. **3層のテスト**: ユニットテスト、統合テスト、E2Eテスト
4. **テストの独立性**: 各テストは独立して実行可能
5. **意図の明確化**: テストコードが仕様書として機能する

### 6.1 フロントエンドテスト

**参照先**:
- `/tdd` skill: TDDの基本原則とRed-Green-Refactorサイクル
- `/frontend` skill: Vitest + Testing Library、コンポーネントテスト、フックテスト

**テストフレームワーク**: Vitest + Testing Library

### 6.2 バックエンドテスト

**参照先**:
- `/tdd` skill: TDDの基本原則とRed-Green-Refactorサイクル
- `/fastapi` skill: pytest、TestClient、非同期テスト、Firestoreモック

**テストフレームワーク**: pytest

**詳細なテストパターンとコード例は `/tdd` と `/fastapi` skillを参照してください。**

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

