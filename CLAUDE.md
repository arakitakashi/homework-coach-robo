# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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

- **Frontend**: Next.js 14+ (App Router) + Bun
- **Backend**: FastAPI + Python 3.10+ + uv
- **Infrastructure**: Google Cloud Run
- **Database**: Cloud Firestore (リアルタイムデータ), BigQuery (分析用データ), Redis (キャッシュ)
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

## Documentation

- `docs/product-requirements.md`: プロダクト要求仕様書（ビジネス要件、機能要件、KPI）
- `docs/functional-design.md`: 機能設計書（システムアーキテクチャ、API仕様、データフロー）
- `docs/architecture.md`: 技術仕様書（技術スタック、インフラ設計、パフォーマンス要件）
- `docs/development-guidelines.md`: 開発ガイドライン（TDD原則、コーディング規約、テスト規約）
- `docs/firestore-design.md`: Firestoreスキーマ設計（データ構造、セキュリティルール）
- `docs/repository-structure.md`: リポジトリ構造定義（ディレクトリ構成、命名規則）

## Development Context

このプロジェクトは現在、**設計フェーズ完了・実装準備中**の段階です。

### 完了済み

- プロダクト要求仕様書の作成
- 機能設計書の作成（システムアーキテクチャ、API設計）
- 技術仕様書の作成（技術スタック確定、インフラ設計）
- 開発ガイドラインの策定（TDD原則、コーディング規約）
- データベース設計（Firestore、BigQuery）
- リポジトリ構造の定義

### 実装開始時の順序

1. **リポジトリセットアップ**: モノレポ構造の作成、CI/CD設定
2. **技術検証（PoC）**: Google ADK + Gemini Live APIの動作確認
3. **コア機能の実装**: ソクラテス式対話エンジン、3段階ヒントシステム（TDD実践）
4. **パイロットテスト**: 小規模グループでのβテスト

### 開発方針

- **テスト駆動開発（TDD）を徹底**: t_wadaが提唱するRed-Green-Refactorサイクルを実践
- **小さく始める**: MVPに必要な機能のみを実装
- **品質を優先**: テストカバレッジ80%以上を維持

## Important Notes

- **ターゲットユーザーは小学校低学年**: UIやメッセージは平易な日本語で
- **学習効果の最大化**: 単なる回答提供ツールではなく、思考プロセスを育てることが目的
- **成長マインドセット**: 正解だけでなく、挑戦したこと、間違いから学んだことを称賛

## Development Guidelines

実装時は必ず `docs/development-guidelines.md` を参照してください。

### 必須事項

1. **テスト駆動開発（TDD）の徹底**
   - 実装コードを書く前に必ずテストを書く
   - Red-Green-Refactorサイクルを守る
   - テストカバレッジ80%以上を維持

2. **コーディング規約の遵守**
   - フロントエンド: TypeScript + React (関数コンポーネント)
   - バックエンド: Python + FastAPI (型ヒント必須)
   - 命名規則: camelCase (TS), snake_case (Python)

3. **Git規約**
   - ブランチ戦略: Git Flow
   - コミットメッセージ: Conventional Commits形式
   - PR前に自己レビュー必須

## Available Skills

実装時に活用できるスキルが用意されています。スキルを使用することで、ベストプラクティスに従った実装が可能になります。

### TDD Skill

**使用方法**: `/tdd` コマンド

**内容**:
- 和田卓人（t_wada）が提唱するTDD原則（完全版）
- Red-Green-Refactorサイクルの詳細解説
- 仮実装・三角測量・明白な実装の3つの戦略
- TODOリスト駆動開発
- ベイビーステップの実践方法
- TDDチェックリスト

**使用タイミング**:
- 新機能の実装開始時
- テストファーストで進めたい時
- TDDのベストプラクティスを確認したい時

### Frontend Skill

**使用方法**: `/frontend` コマンド

**内容**:
- Next.js 14+ (App Router) + TypeScript + React
- プロジェクト構造とファイル配置
- TypeScript型定義とUtility Types
- React コンポーネントパターン（Server/Client Component）
- 命名規則（PascalCase/camelCase）
- Tailwind CSS スタイリング
- アクセシビリティ（ARIA、キーボードナビゲーション）
- Vitest + Testing Library
- Zod バリデーション

**使用タイミング**:
- フロントエンド実装開始時
- Next.js App Routerでの開発時
- React コンポーネント作成時
- UI/UXテスト作成時

### FastAPI Skill

**使用方法**: `/fastapi` コマンド

**内容**:
- FastAPI 0.128.0 + Pydantic v2のベストプラクティス
- Firestore統合パターン
- JWT認証の実装方法
- プロジェクト構造（ドメインベース）
- 7つの既知の問題と予防策
- CORS、バリデーション、非同期処理のパターン

**使用タイミング**:
- バックエンドAPI実装時
- Firestore連携の実装時
- JWT認証の実装時
- FastAPIのエラー対処時

### Google ADK Basics Skill

**使用方法**: `/google-adk-basics` コマンド

**内容**:
- Agent Development Kit (ADK) の基礎
- Agent構造規約（root_agent/App patterns）
- プロジェクトセットアップ（uv + Python 3.11+）
- Simple Agent vs App Pattern
- ツール統合（定義、ハンドラー、使用方法）
- セッション管理（InMemoryRunner/VertexAIRunner）
- マルチエージェントシステム
- ベストプラクティスとよくある問題

**使用タイミング**:
- ADK開発の基礎を学ぶとき
- Agentの構造を設計するとき
- ADKプロジェクトのセットアップ時
- ツール統合の実装時

### Google ADK Live Skill

**使用方法**: `/google-adk-live` コマンド

**内容**:
- Gemini Live API（Bidi-streaming）の完全ガイド
- リアルタイム音声・動画インタラクション
- LiveRequestQueue + RunConfig
- FastAPI + WebSocket統合（production sample準拠）
- 音声トランスクリプション（入力/出力）
- セッション再開機能
- イベント処理パターン
- 音声アクティビティ検出
- ツール実行（Liveモード）

**使用タイミング**:
- Gemini Live API実装時
- リアルタイム音声AIの構築時
- WebSocketベースの会話型AI開発時
- 双方向ストリーミング実装時
- 本プロジェクトの音声対話エンジン実装時

**注意**: このスキルは `/google-adk-basics` の知識が前提です。

### Git Workflow Skill

**使用方法**: `/git-workflow` コマンド

**内容**:
- Git Flow ブランチ戦略（main/develop/feature/hotfix）
- ブランチ命名規則（feature/fix/refactor/docs）
- Conventional Commits形式（`<type>(<scope>): <subject>`）
- コミット粒度のベストプラクティス
- プルリクエストテンプレート
- コードレビューチェックリスト
- レビュープロセスとマージ基準
- 一般的なGitワークフロー（feature/bugfix/hotfix）
- Git設定推奨事項
- トラブルシューティング（reset/rebase/conflicts）

**使用タイミング**:
- ブランチ作成時
- コミットメッセージを書くとき
- プルリクエスト作成時
- コードレビュー時
- Git操作で困ったとき

### Security Review Skill

**使用方法**: `/security-review` コマンド

**内容**:
- OWASP Top 10対策の実装パターン
- Secrets Management（環境変数、クラウドシークレット管理）
- Input Validation（Zod、Pydantic、ファイルアップロード検証）
- SQL Injection Prevention（パラメータ化クエリ、ORM安全使用）
- Authentication & Authorization（JWT、httpOnly cookies、RLS）
- XSS Prevention（HTMLサニタイズ、CSP）
- CSRF Protection（トークン、SameSite cookies）
- Rate Limiting（API制限、高負荷操作保護）
- Sensitive Data Exposure（ログリダクション、エラー安全化）
- Dependency Security（npm audit、定期更新）
- Cloud Infrastructure Security（IAM、ネットワーク、CI/CD、WAF）
- Pre-Deployment Checklist（本番デプロイ前チェック項目）

**使用タイミング**:
- 認証・認可機能の実装時
- ユーザー入力処理の実装時
- API エンドポイント作成時
- 秘密情報・クレデンシャルの管理時
- クラウドインフラ設定時
- 本番デプロイ前のセキュリティレビュー時
