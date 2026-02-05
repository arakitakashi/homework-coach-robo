# Task List - リポジトリセットアップ

## Phase 1: ディレクトリ構造作成

- [x] フロントエンドディレクトリ構造作成（`frontend/`）
- [x] バックエンドディレクトリ構造作成（`backend/`）
- [x] 共通リソースディレクトリ作成（`shared/`）
- [x] インフラディレクトリ作成（`infrastructure/`）- 既存
- [x] プロジェクトスクリプトディレクトリ作成（`scripts/`）
- [x] GitHubディレクトリ作成（`.github/`）- 既存

## Phase 2: フロントエンド初期化

- [x] Next.js 16 プロジェクト初期化（Bun使用）- 最新版を採用
- [x] TypeScript設定（`tsconfig.json`）
- [x] Biome設定（ESLint/Prettierを置換）
- [x] 環境変数テンプレート作成（`.env.local.example`）
- [x] `next.config.ts` 設定
- [x] Jotai初期設定（ストアの雛形）
- [x] Vitest + Testing Library設定

## Phase 3: バックエンド初期化

- [x] Python 3.10+ 設定（`.python-version`）
- [x] `pyproject.toml` 作成（依存関係、Ruff, mypy設定）
- [x] uv でプロジェクト初期化
- [x] FastAPI基本構造作成（`app/main.py`）
- [x] 環境変数テンプレート作成（`.env.example`）
- [x] pytest設定（`conftest.py`）
- [x] 各ディレクトリに`__init__.py`配置

## Phase 4: 共通リソース・スクリプト

- [x] 共通型定義ファイル作成（TypeScript/Python）
- [x] エラーコード定数作成（TypeScript/Python）
- [x] プロジェクトスクリプト作成（`setup.sh`, `dev.sh`, `test.sh`）

## Phase 5: GitHub設定・CI

- [x] フロントエンドCIワークフロー作成（`.github/workflows/ci-frontend.yml`）
- [x] バックエンドCIワークフロー作成（`.github/workflows/ci-backend.yml`）
- [x] Issueテンプレート作成（bug_report.md, feature_request.md）
- [x] PRテンプレート作成（PULL_REQUEST_TEMPLATE.md）

## Phase 6: 開発環境設定

- [x] VS Code設定（`.vscode/settings.json`）
- [x] VS Code推奨拡張機能（`.vscode/extensions.json`）
- [x] EditorConfig（`.editorconfig`）
- [x] `.gitignore` 更新（既存に追加）

## Phase 7: 動作確認・テスト

- [x] フロントエンド: `bun install` 成功確認
- [x] フロントエンド: `bun run lint` 成功確認
- [x] フロントエンド: `bun run dev` 起動確認 - 手動確認完了
- [x] バックエンド: `uv sync` 成功確認
- [x] バックエンド: lint（Ruff, mypy）成功確認
- [x] バックエンド: `uvicorn app.main:app` 起動確認 - 手動確認完了
- [x] GitHub Actions: CIワークフローの構文チェック

## Phase 8: 品質チェック

- [x] コードレビュー（セルフレビュー）
- [x] セキュリティレビュー（機密情報がコミットされていないか確認）
- [x] CLAUDE.mdの構造定義との整合性確認
- [x] コーディング規約準拠確認
- [x] frontend/CLAUDE.mdと.claude/skillsの競合チェック・解消

## 備考

- 各フェーズは順番に実行
- 問題が発生した場合は前のフェーズに戻って修正
- CIは最小限の設定から始め、必要に応じて拡張

## 変更点（design.mdからの差異）

- ESLint/Prettier → **Biome** に変更（高速、統一ツール）
- Black/isort → **Ruff** に変更（高速、統一ツール）
- Next.js 14 → **Next.js 16** に更新（最新版）
