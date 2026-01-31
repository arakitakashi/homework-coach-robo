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

## Rules

開発ルールは `.claude/rules/` に配置されており、Claude Code が自動的に読み込みます。

| ルール | 内容 |
|--------|------|
| `pre-implementation-checklist.md` | 実装前チェック（ブランチ、ステアリングディレクトリ） |
| `steering-workflow.md` | ワークフロー（requirements/design/tasklist作成） |
| `tdd-requirement.md` | TDD必須（Red-Green-Refactor、カバレッジ80%） |
| `coding-standards.md` | コーディング規約 |
| `security-requirement.md` | セキュリティ要件 |

## Available Skills

実装時に活用できるスキルが `.claude/skills/` に用意されています。

| カテゴリ | スキル |
|----------|--------|
| 開発プロセス | `/tdd`, `/git-workflow`, `/security-review` |
| フロントエンド | `/frontend`, `/frontend-design`, `/vercel-react-best-practices` |
| バックエンド | `/fastapi`, `/google-adk-basics`, `/google-adk-live` |

**注意**: `/google-adk-live` は `/google-adk-basics` の知識が前提です。
