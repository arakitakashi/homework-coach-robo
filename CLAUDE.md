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

## Development Context

このプロジェクトは現在、**MVP実装完了・Phase 2（エージェントアーキテクチャ拡張）準備中**の段階です。

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
- **インフラストラクチャ（IaC）**: Terraformモジュール、Cloud Build、Docker設定完了
- **フロントエンドUI**: コンポーネント、状態管理、カスタムフック、SSEクライアント、音声入力実装完了
- **インフラデプロイ**: GCPプロジェクト（homework-coach-robo）にTerraformでデプロイ完了
- **アプリケーションデプロイ**: Backend/Frontend を Cloud Run にデプロイ完了
- **WebSocket音声ストリーミング**: バックエンドWebSocketエンドポイント + フロントエンド統合完了
- **E2Eテスト**: Playwright によるスモーク・機能・統合テスト（9テストファイル）実装完了
- **GitHub WIF Terraform**: GitHub Actions 向け Workload Identity Federation をIaC化完了

### 技術検証（PoC）の成果

`poc/` ディレクトリに技術検証の実装があります。

| 検証項目 | 結果 | 備考 |
|----------|------|------|
| Live API接続 | ✅ 成功 | ADK + google-genaiで正常接続 |
| 日本語音声入出力 | ✅ 動作 | 音声認識・合成ともに日本語対応 |
| ソクラテス式対話 | ✅ 動作 | システムプロンプトで実現 |
| レイテンシ | ⚠️ 約5秒 | プレビュー版の制約（目標2秒） |

**PoCで使用したモデル**: `gemini-2.5-flash-native-audio-preview-12-2025`
**本番使用モデル**: `gemini-live-2.5-flash-native-audio`（Vertex AI 安定版）

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

**テストカバレッジ**: 96%（352テスト）

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

### WebSocket Voice Streaming（完了）

`backend/app/services/voice/` および `backend/app/api/v1/voice_stream.py` に双方向音声ストリーミングを実装しました。

| コンポーネント | 説明 |
|--------------|------|
| `services/voice/streaming_service.py` | VoiceStreamingService（ADK Runner.run_live() + LiveRequestQueue） |
| `schemas/voice_stream.py` | WebSocketメッセージスキーマ（Audio, Text, Config, Error） |
| `api/v1/voice_stream.py` | WebSocketエンドポイント（Full-duplex） |

**WebSocketエンドポイント:**
```
WebSocket /ws/{user_id}/{session_id}

Client → Server:
  - Binary: PCM音声データ（16kHz 16-bit）
  - JSON: {"type": "text", "text": "..."} テキストメッセージ
  - JSON: {"type": "config", ...} 設定変更

Server → Client:
  - Binary: PCM音声データ（24kHz）
  - JSON: {"type": "transcript", "text": "...", "role": "user|model"}
  - JSON: {"type": "turn_complete"}
  - JSON: {"type": "error", "message": "..."}
```

**使用モデル**: `gemini-live-2.5-flash-native-audio`（Vertex AI）

詳細は `.steering/20260207-backend-websocket-streaming/COMPLETED.md` を参照。

### Frontend Implementation（完了）

`frontend/` に Next.js 16 ベースのフロントエンドを実装しました。

**進捗: コア機能実装完了（WebSocket統合・E2Eテスト含む）**

#### 完了済みコンポーネント

| カテゴリ | コンポーネント | 説明 |
|---------|--------------|------|
| **ページ** | `src/app/page.tsx` | ホーム（キャラクター選択UI） |
| | `src/app/session/page.tsx` | セッションページ（対話インターフェース） |
| **UI** | `CharacterDisplay` | ロボットキャラクター（状態別アニメーション） |
| | `VoiceInterface` | 録音ボタン＋音量レベル表示（プレゼンテーションコンポーネント） |
| | `DialogueHistory` | 対話履歴（吹き出し形式） |
| | `ProgressDisplay` | 学習進捗（ポイント表示） |
| | `HintIndicator` | 宝箱型ヒントレベル表示 |
| | `Button`, `Card`, `LoadingSpinner`, `ErrorMessage`, `TextInput` | 基本UIコンポーネント |
| **状態管理** | `store/atoms/dialogue.ts` | 対話履歴、ヒントレベル、キャラクター状態 |
| | `store/atoms/session.ts` | セッション、学習進捗、ポイント計算 |
| **フック** | `useVoiceRecorder` | Web Audio API録音（PCM 16-bit変換） |
| | `useAudioPlayer` | 音声再生（AudioContext管理） |
| | `usePcmPlayer` | AudioWorkletベースPCMストリーミング再生（24kHz） |
| | `useWebSocket` | WebSocket通信（JSON/ArrayBuffer対応） |
| | `useVoiceStream` | 音声ストリーミング統合（WebSocket + AudioWorklet） |
| | `useSession` | セッション管理（作成/削除） |
| | `useDialogue` | 対話管理（SSEストリーミング） |
| **APIクライアント** | `SessionClient` | セッションCRUD操作 |
| | `DialogueClient` | SSEストリーミング対話 |
| | `VoiceWebSocketClient` | WebSocket音声通信 |
| **AudioWorklet** | `pcm-recorder-processor.js` | 録音用Processor（16kHz 16-bit） |
| | `pcm-player-processor.js` | 再生用Processor（24kHz） |
| **型定義** | `types/` | dialogue, session, audio, websocket |

#### 未実装（MVP後）

| 項目 | 状況 | 説明 |
|------|------|------|
| **追加キャラクター** | ⏸️ 低優先度 | 魔法使い、宇宙飛行士、動物（選択UIは実装済み） |

#### テストカバレッジ

- **ユニットテスト**: 23テストファイル、194テスト（Vitest + Testing Library）
- **E2Eテスト**: 9テストファイル（Playwright）- スモーク・機能・統合
- 適切なモック（MediaDevices, AudioContext, WebSocket, AudioWorklet）

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

#### 音声入力アーキテクチャ

```
SessionContent
└── useVoiceStream (hook)
    ├── VoiceWebSocketClient (WebSocket管理)
    │   └── WebSocket → Backend → Gemini Live API
    ├── AudioWorklet (録音)
    │   └── PCM Recorder Processor (16kHz 16-bit)
    └── AudioWorklet (再生)
        └── PCM Player Processor (24kHz)
```

詳細は `.steering/20260206-voice-input-implementation/COMPLETED.md` を参照。

#### 今後の実装予定（MVP後）

1. **追加キャラクター** - 魔法使い、宇宙飛行士、動物の実装

### E2Eテスト（完了）

`frontend/e2e/` に Playwright ベースの E2E テストを実装しました。

| カテゴリ | テストファイル | 内容 |
|---------|-------------|------|
| **Smoke** | `health-check.spec.ts` | ヘルスチェックエンドポイント確認 |
| | `navigation.spec.ts` | ページ遷移の動作確認 |
| **Functional** | `home-page.spec.ts` | ホームページUI・キャラクター選択 |
| | `session-creation.spec.ts` | セッション作成フロー |
| | `session-cleanup.spec.ts` | セッション終了・クリーンアップ |
| | `text-dialogue.spec.ts` | テキスト対話（SSEストリーミング） |
| | `voice-ui.spec.ts` | 音声UIの表示・状態遷移 |
| **Integration** | `dialogue-stream.spec.ts` | 対話ストリーム統合テスト |
| | `session-api.spec.ts` | セッションAPI統合テスト |

**テスト基盤:**
- `E2E_MODE` 環境変数でバックエンドのモックサービスを有効化（DI overrides）
- Docker Compose でバックエンド・フロントエンドを起動
- `global-setup.ts` / `global-teardown.ts` でサーバーのライフサイクル管理
- CI: `.github/workflows/ci-e2e.yml`

詳細は `.steering/20260207-e2e-tests/` 配下を参照。

### インフラストラクチャ（IaC）

`infrastructure/` ディレクトリにGCPインフラのIaC実装があります。

#### Terraform モジュール構成

```
infrastructure/terraform/
├── bootstrap/                 # State Bucket + API有効化（ローカルstate）
├── shared/                    # Provider設定
├── modules/
│   ├── vpc/                   # VPC + VPC Connector
│   ├── iam/                   # Service Accounts + Roles
│   ├── secret_manager/        # Secret定義
│   ├── firestore/             # Database + Indexes
│   ├── bigquery/              # Dataset + Tables
│   ├── cloud_storage/         # Assets Bucket + CDN
│   ├── cloud_run/             # Backend/Frontend Services
│   └── github_wif/            # GitHub Actions WIF（Workload Identity Federation）
└── environments/
    └── dev/                   # 開発環境設定
```

**注意**: Redis モジュールは除外。セッション管理は Vertex AI / ADK で対応。

#### Cloud Run 設定

| Service | CPU | Memory | Min | Max | Timeout |
|---------|-----|--------|-----|-----|---------|
| Frontend | 1 | 512Mi | 0 (dev) / 1 (prod) | 10 | 60s |
| Backend | 2 | 1Gi | 0 (dev) / 1 (prod) | 20 | 300s |

#### Docker & CI/CD

- `infrastructure/docker/backend/Dockerfile` - FastAPI + uv
- `infrastructure/docker/frontend/Dockerfile` - Next.js + Bun
- `infrastructure/cloud-build/` - Cloud Build パイプライン
- `.github/workflows/ci-backend.yml` - バックエンドCI（lint, type check, test）
- `.github/workflows/ci-frontend.yml` - フロントエンドCI（lint, type check, test）
- `.github/workflows/ci-e2e.yml` - E2Eテスト（Docker Compose + Playwright）
- `.github/workflows/cd.yml` - 自動デプロイ（push to main）
- `.github/workflows/deploy.yml` - マニュアルデプロイ（workflow_dispatch）

**CI/CDの前提条件:** Workload Identity Federation (WIF) の設定が必要。
`infrastructure/terraform/modules/github_wif/` でTerraform管理。

#### インフラデプロイ手順

```bash
# 1. GCPプロジェクト作成後、bootstrap/terraform.tfvarsを更新
cd infrastructure/terraform/bootstrap
# project_id を実際のプロジェクトIDに変更

# 2. Bootstrap実行（State Bucket + API有効化）
terraform init
terraform apply

# 3. メインインフラデプロイ
cd ../environments/dev
terraform init
terraform plan
terraform apply

# 4. Secret値を手動設定（Secret Manager）

# 5. WIF設定（GitHub Actions連携）
# → Terraformで自動作成: modules/github_wif
# → GitHub Secrets に GCP_WORKLOAD_IDENTITY_PROVIDER, GCP_SERVICE_ACCOUNT を設定
```

詳細は `.steering/20260205-infrastructure-implementation/COMPLETED.md` を参照。

### デプロイ済み環境（Dev）

GCPプロジェクト `homework-coach-robo` にデプロイ済みです。

| サービス | URL | 状態 |
|---------|-----|------|
| **Frontend** | https://homework-coach-frontend-652907685934.asia-northeast1.run.app | ✅ 稼働中 |
| **Backend** | https://homework-coach-backend-652907685934.asia-northeast1.run.app | ✅ 稼働中 |

**ヘルスチェック:**
- Backend `/health`: `{"status":"healthy"}`
- Frontend `/api/health`: `{"status":"ok"}`

詳細は `.steering/20260206-application-deploy/COMPLETED.md` を参照。

### 次のステップ

1. ~~リポジトリセットアップ~~ ✅ 完了
2. ~~技術検証（PoC）~~ ✅ 完了
3. ~~**コア機能の実装**: ソクラテス式対話エンジン基盤、API統合、3段階ヒントシステム~~ ✅ 完了
4. ~~**LLM統合**: 回答分析、質問生成、ヒント生成にLLMを活用~~ ✅ 完了
5. ~~**FirestoreSessionService**: ADK SessionService準拠の永続化~~ ✅ 完了
6. ~~**FirestoreMemoryService**: ADK MemoryService準拠の永続化~~ ✅ 完了
7. ~~**ADK Runner統合**: SocraticDialogueAgent + AgentRunnerService~~ ✅ 完了
8. ~~**API統合**: SSEストリーミングエンドポイント実装~~ ✅ 完了
9. ~~**インフラストラクチャ（IaC）**: Terraform、Cloud Build、Docker~~ ✅ 完了
10. ~~**フロントエンド実装**~~ ✅ 完了
    - ~~UIコンポーネント~~ ✅ 完了
    - ~~状態管理（Jotai）~~ ✅ 完了
    - ~~カスタムフック~~ ✅ 完了
    - ~~SSEクライアント実装~~ ✅ 完了
    - ~~音声入力実装~~ ✅ 完了
11. ~~**インフラデプロイ**~~ ✅ 完了
12. ~~**アプリケーションデプロイ**~~ ✅ 完了
13. ~~**WebSocket音声ストリーミング実装**~~ ✅ 完了
    - ~~バックエンドWebSocketエンドポイント（`/ws/{user_id}/{session_id}`）~~ ✅ 完了
    - ~~Gemini Live API統合（`poc/`の成果を本実装に移植）~~ ✅ 完了
    - ~~双方向音声ストリーミング（録音→STT→LLM→TTS→再生）~~ ✅ 完了
    - ~~フロントエンドとの接続確認~~ ✅ 完了
14. ~~**E2Eテスト**~~ ✅ 完了
15. ~~**GitHub WIF Terraform**~~ ✅ 完了
16. **Phase 2a: ADKツール導入（Function Calling）** ← 現在地
    - `calculate_tool`: 計算検証（LLM幻覚リスク排除）
    - `manage_hint_tool`: ヒント段階の厳密な状態管理
    - `record_progress_tool`: 学習進捗記録・ポイント付与
    - `check_curriculum_tool`: カリキュラム・教科書参照
    - `analyze_image_tool`: 宿題写真の読み取り（Vision API）
17. **Phase 2b: マルチエージェント構成**
    - Router Agent（教科・状況に応じた振り分け）
    - Math Coach Agent（算数専門コーチ）
    - Japanese Coach Agent（国語専門コーチ）
    - Encouragement Agent（励まし・休憩提案）
    - Review Agent（振り返り・保護者レポート）
18. **Phase 2c: Vertex AI RAG（セマンティック記憶）**
    - RAG Corpus作成・インデクシング
    - `search_memory_tool` 統合
    - FirestoreMemoryService からの移行
19. **Phase 2d: 感情適応エージェント**
    - テキストベース感情分析（Gemini）
    - 感情 → 対話トーン適応ロジック
    - 音声トーン分析の高度化（AutoML）
20. **Phase 3: Vertex AI Agent Engine デプロイ**
    - Agent Engine へのエージェントデプロイ
    - セッション管理の移行（自前 → マネージド）
    - A/Bテスト環境構築
21. **パイロットテスト**: 小規模グループでのβテスト

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
