# Requirements - リポジトリセットアップ

## 背景・目的

PoCが完了し、Google ADK + Gemini Live APIの動作確認ができた。
次のステップとして、本番開発に向けたモノレポ構造を構築する。

現状:
- PoC: `poc/server/` にADK検証コードが存在
- ドキュメント: `docs/` に設計書一式が完成
- リポジトリ構造定義: `docs/repository-structure.md` に詳細な構造が定義済み

## 要求事項

### 機能要件

1. **モノレポ構造の作成**
   - `docs/repository-structure.md` に定義された構造を実装
   - フロントエンド、バックエンド、共通リソースのディレクトリ作成

2. **フロントエンド基盤**
   - Next.js 14+ (App Router) プロジェクト初期化
   - Bun パッケージマネージャー使用
   - TypeScript設定
   - ESLint/Prettier設定
   - Jotai状態管理の準備

3. **バックエンド基盤**
   - FastAPI プロジェクト初期化
   - Python 3.10+ / uv パッケージマネージャー
   - pyproject.toml設定（Black, isort, mypy）
   - テストフレームワーク（pytest）設定

4. **CI/CD設定**
   - GitHub Actions ワークフロー
     - フロントエンドCI（lint, test, build）
     - バックエンドCI（lint, test）
   - PR/Issueテンプレート

5. **開発環境設定**
   - VS Code設定（推奨拡張機能、デバッグ設定）
   - EditorConfig

### 非機能要件

1. **保守性**
   - 一貫した命名規則の適用
   - 明確なディレクトリ構造
   - 各ディレクトリにREADME.md

2. **セキュリティ**
   - `.gitignore` による機密ファイル除外
   - 環境変数テンプレート（`.env.example`）の提供

3. **開発効率**
   - ホットリロード対応
   - 型チェック自動実行
   - コードフォーマット自動化

### 制約条件

1. **技術スタック** - CLAUDE.mdおよびdocs/architecture.mdに定義済み
   - フロントエンド: Next.js 14+, Bun, TypeScript, Jotai
   - バックエンド: FastAPI, Python 3.10+, uv, Pydantic v2
   - インフラ: Google Cloud Run, Firestore, BigQuery, Redis

2. **構造定義** - `docs/repository-structure.md` に準拠

3. **コーディング規約** - `docs/development-guidelines.md` に準拠

## 対象範囲

### In Scope

- ディレクトリ構造の作成
- 設定ファイルの作成
- 基本的なプロジェクト初期化（Next.js, FastAPI）
- GitHub Actions CI設定
- 開発環境設定ファイル

### Out of Scope

- 実際の機能実装（ソクラテス式対話エンジン等）
- Terraformによるインフラ構築
- デプロイワークフロー（staging, production）
- Riveアニメーションファイルの作成

## 成功基準

1. `docs/repository-structure.md` に定義された構造が実装されている
2. `bun install` でフロントエンドの依存関係がインストールできる
3. `uv sync` でバックエンドの依存関係がインストールできる
4. GitHub ActionsのCIが正常に動作する
5. ESLint, Prettier, Black, isort が正しく設定されている
