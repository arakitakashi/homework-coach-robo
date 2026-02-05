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

## Development Context

このプロジェクトは現在、**コア機能実装準備中**の段階です。

### 完了済み

- プロダクト要求仕様書の作成
- 機能設計書の作成（システムアーキテクチャ、API設計）
- 技術仕様書の作成（技術スタック確定、インフラ設計）
- 開発ガイドラインの策定（TDD原則、コーディング規約）
- データベース設計（Firestore、BigQuery）
- リポジトリ構造の定義
- **リポジトリセットアップ**: モノレポ構造、CI/CD、開発環境構築完了
- **技術検証（PoC）**: Google ADK + Gemini Live APIの動作確認完了
- **ソクラテス式対話エンジン（基盤）**: データモデル、対話マネージャ実装完了
- **FirestoreSessionService**: ADK BaseSessionService準拠のセッション永続化実装完了
- **FirestoreMemoryService**: ADK BaseMemoryService準拠のメモリ永続化実装完了
- **ADK Runner統合**: SocraticDialogueAgent + AgentRunnerService実装完了
- **対話API統合**: SSEストリーミングエンドポイント（`/api/v1/dialogue/run`）実装完了
- **フロントエンドUI**: コンポーネント、状態管理、カスタムフック実装完了（70-75%）

### 技術検証（PoC）の成果

`poc/` ディレクトリに技術検証の実装があります。

| 検証項目 | 結果 | 備考 |
|----------|------|------|
| Live API接続 | ✅ 成功 | ADK + google-genaiで正常接続 |
| 日本語音声入出力 | ✅ 動作 | 音声認識・合成ともに日本語対応 |
| ソクラテス式対話 | ✅ 動作 | システムプロンプトで実現 |
| レイテンシ | ⚠️ 約5秒 | プレビュー版の制約（目標2秒） |

**使用モデル**: `gemini-2.5-flash-native-audio-preview-12-2025`

詳細は `.steering/20260131-gemini-live-api-poc/COMPLETED.md` を参照。

### ソクラテス式対話エンジン

`backend/app/services/adk/dialogue/` に対話エンジンの基盤を実装しました。

| コンポーネント | 説明 |
|--------------|------|
| `models.py` | データモデル（DialogueContext, DialogueTurn, ResponseAnalysis など） |
| `learning_profile.py` | 学習プロファイル（ChildLearningProfile, LearningMemory など） |
| `manager.py` | SocraticDialogueManager（プロンプト構築、回答分析、質問生成） |
| `gemini_client.py` | GeminiClient（Google Gemini API統合、LLMClientプロトコル準拠） |
| `session_store.py` | SessionStore（インメモリセッション管理） |

**主要機能:**
- `build_question_prompt()`: 質問タイプ・トーンに応じたプロンプト生成
- `analyze_response()`: 子供の回答をLLMで分析
- `determine_question_type()`: 理解度に基づく次の質問タイプ決定
- `determine_tone()`: 状況に応じた対話トーン決定
- `generate_question()`: LLMで質問を生成
- `generate_hint_response()`: ヒントレベルに応じたレスポンス生成
- `should_move_to_next_phase()`: 次のヒントレベルへの遷移判定

**LLM統合:**
- `GeminiClient`: Vertex AI 経由で Gemini API (`gemini-2.5-flash`) を使用
- 開発/本番ともに Vertex AI を使用（Application Default Credentials）
- プロジェクトID未設定時はテンプレートベースのフォールバック応答

**環境変数:**
| 変数名 | 必須 | 説明 |
|--------|------|------|
| `GOOGLE_CLOUD_PROJECT` | ✅ | GCPプロジェクトID |
| `GOOGLE_CLOUD_LOCATION` | ❌ | リージョン（デフォルト: us-central1） |

**ローカル開発セットアップ:**
```bash
# 1. gcloud CLI をインストール（未インストールの場合）
# https://cloud.google.com/sdk/docs/install

# 2. 認証情報を設定
gcloud auth application-default login

# 3. プロジェクトIDを設定
export GOOGLE_CLOUD_PROJECT=your-project-id

# 4. バックエンドを起動
cd backend && uv run uvicorn app.main:app --reload
```

**テストカバレッジ**: 96%（309テスト）

### Firestore Session Persistence

`backend/app/services/adk/sessions/` に ADK 準拠のセッション永続化サービスを実装しました。

| コンポーネント | 説明 |
|--------------|------|
| `converters.py` | ADK Session/Event ↔ Firestore dict 変換関数 |
| `firestore_session_service.py` | FirestoreSessionService（ADK BaseSessionService準拠） |

**主要機能:**
- `create_session()`: セッション作成（3層状態の分離保存）
- `get_session()`: セッション取得（3層状態のマージ）
- `list_sessions()`: セッション一覧取得
- `delete_session()`: セッション削除（サブコレクション含む）
- `append_event()`: イベント追加（temp:*除去、partial非永続化）

**Firestoreコレクション構造:**
```
/sessions/{session_id}              - セッションメタデータと状態
/sessions/{session_id}/events/{id}  - イベント
/app_state/{app_name}               - アプリスコープの状態
/user_state/{app_name}/users/{id}   - ユーザースコープの状態
```

詳細は `.steering/20260205-firestore-session-persistence/COMPLETED.md` を参照。

### Firestore Memory Service

`backend/app/services/adk/memory/` に ADK 準拠のメモリ永続化サービスを実装しました。

| コンポーネント | 説明 |
|--------------|------|
| `converters.py` | ADK Event ↔ Firestore dict 変換関数 |
| `firestore_memory_service.py` | FirestoreMemoryService（ADK BaseMemoryService準拠） |

**主要機能:**
- `add_session_to_memory()`: セッションのイベントを記憶に追加
- `search_memory()`: キーワードベースの記憶検索

**Firestoreコレクション構造:**
```
/memories/{app_name}/users/{user_id}/entries/{entry_id}
```

詳細は `.steering/20260205-adk-memory-bank-integration/COMPLETED.md` を参照。

### ADK Runner Service

`backend/app/services/adk/runner/` に ADK Runner を使用したエージェント実行サービスを実装しました。

| コンポーネント | 説明 |
|--------------|------|
| `agent.py` | SOCRATIC_SYSTEM_PROMPT, create_socratic_agent() |
| `runner_service.py` | AgentRunnerService（SessionService/MemoryService統合） |

**主要機能:**
- `create_socratic_agent()`: 3段階ヒントシステム原則を組み込んだADK Agent作成
- `AgentRunnerService.run()`: 非同期イベントストリームでエージェント実行
- `AgentRunnerService.extract_text()`: イベントからテキスト抽出

**アーキテクチャ:**
```
AgentRunnerService
├── Runner (ADK)
│   ├── SocraticDialogueAgent
│   ├── FirestoreSessionService
│   └── FirestoreMemoryService
└── types (google.genai)
```

詳細は `.steering/20260205-adk-runner-integration/COMPLETED.md` を参照。

### Dialogue API Integration

`backend/app/api/v1/dialogue_runner.py` に SSE ストリーミングエンドポイントを実装しました。

| コンポーネント | 説明 |
|--------------|------|
| `schemas/dialogue_runner.py` | SSEイベントスキーマ（Request, Text, Error, Done） |
| `api/v1/dialogue_runner.py` | ストリーミングエンドポイント（FastAPI Depends + SSE） |

**APIエンドポイント:**
```
POST /api/v1/dialogue/run
Content-Type: application/json
Accept: text/event-stream

Request:
{
  "user_id": "string",
  "session_id": "string",
  "message": "string"
}

Response (SSE):
event: text
data: {"text": "..."}

event: done
data: {"session_id": "..."}

event: error
data: {"error": "...", "code": "INTERNAL_ERROR"}
```

詳細は `.steering/20260205-dialogue-api-integration/COMPLETED.md` を参照。

### Frontend Implementation（進行中）

`frontend/` に Next.js 16 ベースのフロントエンドを実装中です。

**進捗: 約70-75% 完了**

#### 完了済みコンポーネント

| カテゴリ | コンポーネント | 説明 |
|---------|--------------|------|
| **ページ** | `src/app/page.tsx` | ホーム（キャラクター選択UI） |
| | `src/app/session/page.tsx` | セッションページ（対話インターフェース） |
| **UI** | `CharacterDisplay` | ロボットキャラクター（状態別アニメーション） |
| | `VoiceInterface` | 録音ボタン＋音量レベル表示 |
| | `DialogueHistory` | 対話履歴（吹き出し形式） |
| | `ProgressDisplay` | 学習進捗（ポイント表示） |
| | `HintIndicator` | 宝箱型ヒントレベル表示 |
| | `Button`, `Card`, `LoadingSpinner`, `ErrorMessage` | 基本UIコンポーネント |
| **状態管理** | `store/atoms/dialogue.ts` | 対話履歴、ヒントレベル、キャラクター状態 |
| | `store/atoms/session.ts` | セッション、学習進捗、ポイント計算 |
| **フック** | `useVoiceRecorder` | Web Audio API録音（PCM 16-bit変換） |
| | `useAudioPlayer` | 音声再生（AudioContext管理） |
| | `useWebSocket` | WebSocket通信（JSON/ArrayBuffer対応） |
| **型定義** | `types/` | dialogue, session, audio, websocket |

#### 未実装（残り25-30%）

| 項目 | 状況 | 説明 |
|------|------|------|
| **APIクライアント** | ❌ 未実装 | `lib/api/index.ts` は空 |
| **SSEクライアント** | ❌ 未実装 | バックエンドはSSE、フロントはWebSocketフックのみ |
| **バックエンド接続** | ❌ 未実装 | 録音機能はあるが送信なし |
| **追加キャラクター** | ⏸️ 低優先度 | 魔法使い、宇宙飛行士、動物（選択UIは実装済み） |

#### テストカバレッジ

- 14テストファイル（コンポーネント9、フック3、ページ2）
- Vitest + Testing Library
- 適切なモック（MediaDevices, AudioContext, WebSocket）

#### 技術スタック

| 技術 | バージョン |
|------|----------|
| Next.js | 16 (App Router) |
| Bun | 最新 |
| TypeScript | strict mode |
| Tailwind CSS | v4 |
| Jotai | 状態管理 |
| Vitest | テスト |
| Biome | リンター/フォーマッター |

#### 次に実装すべき項目

1. **SSEクライアント** - `lib/api/dialogueClient.ts`
2. **セッションAPI** - セッション作成/管理
3. **SessionContent統合** - SSEクライアントをページに接続

### 次のステップ

1. ~~リポジトリセットアップ~~ ✅ 完了
2. ~~技術検証（PoC）~~ ✅ 完了
3. ~~**コア機能の実装**: ソクラテス式対話エンジン基盤、API統合、3段階ヒントシステム~~ ✅ 完了
4. ~~**LLM統合**: 回答分析、質問生成、ヒント生成にLLMを活用~~ ✅ 完了
5. ~~**FirestoreSessionService**: ADK SessionService準拠の永続化~~ ✅ 完了
6. ~~**FirestoreMemoryService**: ADK MemoryService準拠の永続化~~ ✅ 完了
7. ~~**ADK Runner統合**: SocraticDialogueAgent + AgentRunnerService~~ ✅ 完了
8. ~~**API統合**: SSEストリーミングエンドポイント実装~~ ✅ 完了
9. **フロントエンド実装**（進行中 70-75%）← 現在地
   - ~~UIコンポーネント~~ ✅ 完了
   - ~~状態管理（Jotai）~~ ✅ 完了
   - ~~カスタムフック~~ ✅ 完了
   - SSEクライアント実装 ← 次のタスク
   - バックエンド接続統合
10. **E2Eテスト**: 実際のADK Runnerとの統合テスト
11. **パイロットテスト**: 小規模グループでのβテスト

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

### 🔴 PR作成前の必須コマンド

```bash
# フロントエンド
cd frontend && bun lint && bun typecheck && bun test

# バックエンド
cd backend && uv run ruff check . && uv run mypy . && uv run pytest
```

**CIで実行される全チェックをローカルで事前実行すること。**
| `frontend.md` | フロントエンド開発ルール（`/frontend`, `/frontend-design`スキル必須） |
| `auto-format-hooks.md` | 自動フォーマット（Ruff/Biome）との共存方法 |
| `pr-checklist.md` | PR作成前のローカルCIチェックリスト |

## Available Skills

実装時に活用できるスキルが `.claude/skills/` に用意されています。

| カテゴリ | スキル |
|----------|--------|
| 開発プロセス | `/tdd`, `/git-workflow`, `/security-review` |
| フロントエンド | `/frontend`, `/frontend-design`, `/vercel-react-best-practices` |
| バックエンド | `/fastapi`, `/google-adk-basics`, `/google-adk-live` |

**注意**: `/google-adk-live` は `/google-adk-basics` の知識が前提です。
