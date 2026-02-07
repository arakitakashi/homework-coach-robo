# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 🚨 実装タスク開始前の必須チェック

**実装タスクを開始する前に、必ず `.claude/rules/pre-implementation-checklist.md` のチェックリストを完了すること。**

完了するまでコードを書き始めてはならない。詳細はルールファイルを参照。

---

## Project Overview

**宿題コーチロボット (Homework Coach Robot)** は、小学校低学年（1〜3年生）向けのリアルタイム音声アシスタントです。答えをすぐに教えるのではなく、ソクラテス式対話で子供が自分で考え、自分で気づくプロセスを支援します。

### Core Philosophy

- **答えを教えない**: 質問で子供を導く（ソクラテス式対話）
- **プロセスを評価**: 正解/不正解ではなく、考えたプロセスを重視
- **感情に適応**: 音声トーン分析でフラストレーションレベルを検知し、サポートレベルを調整
- **対等な関係**: AIは「完璧な先生」ではなく「一緒に悩む仲間」として振る舞う

## Architecture Principles

### 3段階ヒントシステム

子供が「答えをすぐ教えて」と要求した場合でも、段階的にサポートします：

1. **レベル1: 問題理解の確認** - 問題文の再確認を促す
2. **レベル2: 既習事項の想起** - 関連する知識を思い出させる
3. **レベル3: 部分的支援** - 問題を小さく分解し、最初の部分のみ支援

実装時は、この段階を飛ばさず、必ず順番に提供すること。

### ソクラテス式対話エンジン

対話生成時の重要な原則：

- 子供の回答に応じて次の質問を**動的に生成**
- 最終的に子供自身が答えに気づくように誘導
- 質問の例:
  - 「この問題、何を聞いてると思う？」
  - 「もし○○だったらどうなるかな？」
  - 「同じような問題、前にやったよね？」

### 感情認識と適応

音声のトーン分析に基づく適応ロジック：

- **イライラしている** → より小さいステップに分解
- **楽しそう・自信がある** → 少し難易度を上げる
- **疲れている** → 休憩を提案

### 評価システム

学習プロセスの可視化：

- 「自分で気づいた」→ 3ポイント
- 「ヒントで気づいた」→ 2ポイント
- 「一緒に解いた」→ 1ポイント

正解/不正解だけでなく、プロセスを記録すること。

## Technical Stack

### MVP Phase (フェーズ1)

- **Frontend**: Next.js 16 (App Router) + Bun + Biome
- **Backend**: FastAPI + Python 3.10+ + uv + Ruff
- **Infrastructure**: Google Cloud Run
- **Database**: Cloud Firestore (リアルタイムデータ), BigQuery (分析用データ)
- **Session Management**: Vertex AI / ADK SessionService
- **AI/ML**: Google ADK + Gemini Live API
- **STT**: Cloud Speech-to-Text API
- **TTS**: Cloud Text-to-Speech API
- **Vision**: Gemini Vision + Cloud Vision API (画像認識)

### Phase 2 Extensions

- 音声感情認識AI
- ゲーミフィケーション要素（冒険ストーリー型の宿題進行）
- 保護者向けダッシュボード

## Key Design Decisions

### UI/UX Principles

1. **ハンズフリー操作**: 低学年の児童はキーボード操作が苦手なため、音声のみで完結
2. **声のトーン変化**: 励ます時、説明する時、一緒に考える時でトーンを変化
3. **キャラクター設定**: 子供が好きなキャラクター（ロボット、魔法使い、宇宙飛行士など）を選択可能
4. **ゲーム演出**: ヒントは「宝箱を開ける」演出でゲーム感覚に

### Privacy & Security

- 子供のデータを扱うため、プライバシー保護は最優先
- 学習履歴の記録: 問題ごとの正答率、ヒント使用回数
- データ暗号化、GDPR/個人情報保護法準拠

## Repository Structure

**モノレポ (Monorepo)** 構成を採用しています。

```
homework-coach-robo/
├── frontend/                 # Next.js 16 (App Router)
│   ├── src/app/              # ページ・ルート（Next.js 16デフォルト構造）
│   ├── components/           # Reactコンポーネント
│   │   ├── ui/               # 汎用UI
│   │   ├── features/         # 機能別
│   │   └── layouts/          # レイアウト
│   ├── lib/                  # ユーティリティ
│   │   ├── api/              # APIクライアント
│   │   └── hooks/            # カスタムフック
│   ├── store/                # Jotai atoms
│   └── types/                # TypeScript型定義
│
├── backend/                  # FastAPI + Python
│   └── app/
│       ├── api/v1/           # APIエンドポイント
│       ├── services/         # ビジネスロジック
│       │   └── adk/          # Google ADK関連
│       ├── models/           # データモデル
│       ├── schemas/          # APIスキーマ
│       └── db/               # DB接続
│
├── poc/                      # 技術検証（PoC）実装
│   ├── server/               # FastAPI + ADK + Gemini Live API
│   └── client/               # Web Audio APIテストUI
│
├── shared/                   # 共通リソース
├── infrastructure/           # Terraform, Cloud Build
├── docs/                     # 設計ドキュメント
└── .claude/
    ├── rules/                # 開発ルール（自動読み込み）
    └── skills/               # スキルファイル
```

**命名規則・配置ルールの詳細は `.claude/rules/file-structure-rules.md` を参照。**

## Documentation

- `docs/product-requirements.md`: プロダクト要求仕様書（ビジネス要件、機能要件、KPI）
- `docs/functional-design.md`: 機能設計書（システムアーキテクチャ、API仕様、データフロー）
- `docs/architecture.md`: 技術仕様書（技術スタック、インフラ設計、パフォーマンス要件）
- `docs/firestore-design.md`: Firestoreスキーマ設計（データ構造、セキュリティルール）
- `docs/agent-architecture.md`: エージェントアーキテクチャ設計書（ツール、マルチエージェント、RAG、感情適応、Agent Engine）
- `docs/implementation-status.md`: 実装済み機能の詳細記録（コンポーネント、API仕様、デプロイ環境）

## Development Context

このプロジェクトは現在、**MVP実装完了・Phase 2（エージェントアーキテクチャ拡張）準備中**の段階です。

- 実装済み機能の詳細: [`docs/implementation-status.md`](docs/implementation-status.md)
- Phase 2〜3 ロードマップ: [GitHub Milestones](https://github.com/arakitakashi/homework-coach-robo/milestones)
- エージェントアーキテクチャ設計: [`docs/agent-architecture.md`](docs/agent-architecture.md)

### ADK エージェントアーキテクチャ（Phase 2 計画）

MVP（Phase 1）ではシステムプロンプトのみの単一エージェント（`tools=[]`）だが、Phase 2ではADKの高度な機能をフル活用する。

| Phase | 内容 | 主要変更 |
|-------|------|---------|
| **2a** | ツール導入（Function Calling） | `calculate_tool`, `manage_hint_tool`, `record_progress_tool`, `check_curriculum_tool`, `analyze_image_tool` |
| **2b** | マルチエージェント | Router Agent → Math/Japanese/Encouragement/Review Agent |
| **2c** | Vertex AI RAG | セマンティック記憶検索（キーワード検索を置換） |
| **2d** | 感情適応 | 音声トーン分析 → 対話トーン・サポートレベル適応 |
| **3** | Agent Engine | Vertex AI Agent Engineへのマネージドデプロイ |

**Phase 2 ファイル構成（計画）:**
```
backend/app/services/adk/
├── agents/                   # マルチエージェント定義
│   ├── router.py             # Router Agent
│   ├── math_coach.py         # 算数コーチ
│   ├── japanese_coach.py     # 国語コーチ
│   ├── encouragement.py      # 励まし
│   ├── review.py             # 振り返り
│   └── prompts/              # エージェント別プロンプト
├── tools/                    # ADK Function Tools
│   ├── calculate.py          # 計算検証
│   ├── hint_manager.py       # ヒント段階管理
│   ├── curriculum.py         # カリキュラム参照
│   ├── progress_recorder.py  # 進捗記録
│   └── image_analyzer.py     # 画像分析
├── runner/                   # 既存
├── sessions/                 # 既存
└── memory/                   # → Phase 2cでRAGに移行
```

詳細は `docs/agent-architecture.md` を参照。

### インフラストラクチャ概要

```
infrastructure/terraform/
├── bootstrap/                 # State Bucket + API有効化
├── shared/                    # Provider設定
├── modules/                   # vpc, iam, secret_manager, firestore, bigquery,
│                              # cloud_storage, cloud_run, github_wif
└── environments/dev/          # 開発環境設定
```

**CI/CD:**
- `.github/workflows/ci-backend.yml` - バックエンドCI（lint, type check, test）
- `.github/workflows/ci-frontend.yml` - フロントエンドCI（lint, type check, test）
- `.github/workflows/ci-e2e.yml` - E2Eテスト（Docker Compose + Playwright）
- `.github/workflows/cd.yml` - 自動デプロイ（push to main）
- `.github/workflows/deploy.yml` - マニュアルデプロイ（workflow_dispatch）

詳細は [`docs/implementation-status.md`](docs/implementation-status.md) を参照。

### 開発方針

- **テスト駆動開発（TDD）を徹底**: t_wadaが提唱するRed-Green-Refactorサイクルを実践
- **小さく始める**: MVPに必要な機能のみを実装
- **品質を優先**: テストカバレッジ80%以上を維持

## Important Notes

- **ターゲットユーザーは小学校低学年**: UIやメッセージは平易な日本語で
- **学習効果の最大化**: 単なる回答提供ツールではなく、思考プロセスを育てることが目的
- **成長マインドセット**: 正解だけでなく、挑戦したこと、間違いから学んだことを称賛

## Rules

開発ルールは `.claude/rules/` に配置されており、Claude Code が自動的に読み込みます。

| ルール | 内容 |
|--------|------|
| `pre-implementation-checklist.md` | 実装前チェック（ブランチ、ステアリングディレクトリ）、**PR前CI必須チェック** |
| `steering-workflow.md` | ワークフロー（requirements/design/tasklist作成） |
| `tdd-requirement.md` | TDD必須（Red-Green-Refactor、カバレッジ80%）、**Vitest importルール** |
| `coding-standards.md` | コーディング規約 |
| `security-requirement.md` | セキュリティ要件 |
| `file-structure-rules.md` | ファイル配置・命名規則 |
| `frontend.md` | フロントエンド開発ルール、**Biome a11yルール、Jotaiテストパターン** |
| `auto-format-hooks.md` | 自動フォーマット（Ruff/Biome）との共存方法 |
| `pr-checklist.md` | PR作成前のローカルCIチェックリスト |

### 🔴 PR作成前の必須コマンド

```bash
# フロントエンド
cd frontend && bun lint && bun typecheck && bun test

# バックエンド
cd backend && uv run ruff check . && uv run mypy . && uv run pytest
```

**CIで実行される全チェックをローカルで事前実行すること。**

## Available Skills

実装時に活用できるスキルが `.claude/skills/` に用意されています。

| カテゴリ | スキル |
|----------|--------|
| 開発プロセス | `/tdd`, `/git-workflow`, `/security-review` |
| フロントエンド | `/frontend`, `/frontend-design`, `/vercel-react-best-practices` |
| バックエンド | `/fastapi`, `/google-adk-basics`, `/google-adk-live` |

**注意**: `/google-adk-live` は `/google-adk-basics` の知識が前提です。
