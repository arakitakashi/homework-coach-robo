# Implementation Status

このドキュメントは、宿題コーチロボットの実装済み機能の詳細を記録します。

**プロジェクトステータス**: MVP実装完了・Phase 2a（ツール導入）実装完了

---

## 完了済み機能一覧

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
- **ADK Function Tools (Phase 2a)**: 5つのADKツール（calculate, hint_manager, curriculum, progress_recorder, image_analyzer）実装完了

---

## バックエンド

### ソクラテス式対話エンジン

`backend/app/services/adk/dialogue/` に対話エンジンの基盤を実装。

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
| `GOOGLE_CLOUD_PROJECT` | 必須 | GCPプロジェクトID |
| `GOOGLE_CLOUD_LOCATION` | 任意 | リージョン（デフォルト: us-central1） |

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

`backend/app/services/adk/sessions/` に ADK 準拠のセッション永続化サービスを実装。

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

`backend/app/services/adk/memory/` に ADK 準拠のメモリ永続化サービスを実装。

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

`backend/app/services/adk/runner/` に ADK Runner を使用したエージェント実行サービスを実装。

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

`backend/app/api/v1/dialogue_runner.py` に SSE ストリーミングエンドポイントを実装。

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

### WebSocket Voice Streaming

`backend/app/services/voice/` および `backend/app/api/v1/voice_stream.py` に双方向音声ストリーミングを実装。

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

### ADK Function Tools (Phase 2a)

`backend/app/services/adk/tools/` に ADK FunctionTool を5つ実装。エージェントの `tools=[]` を置き換え、LLMの幻覚リスクを排除。

| ツール | ファイル | 説明 |
|--------|---------|------|
| `calculate_tool` | `calculate.py` | 安全な算術評価（eval不使用）、子供の回答の正誤検証、学年別ヒント |
| `manage_hint_tool` | `hint_manager.py` | 3段階ヒントシステムの状態管理（ToolContext.state経由） |
| `check_curriculum_tool` | `curriculum.py` | 学年・教科に応じたカリキュラム情報参照（インメモリ静的データ） |
| `record_progress_tool` | `progress_recorder.py` | 学習プロセスのポイント付与（self_solved=3pt, hint_solved=2pt, guided_solved=1pt） |
| `analyze_image_tool` | `image_analyzer.py` | Gemini Vision API による宿題画像分析（base64入力、10MB制限） |

**エージェント統合:**
- `runner/agent.py` の `create_socratic_agent()` に5ツールを統合
- システムプロンプトに「ツールの使い方」セクションを追加
- 各ツールは `ToolContext.state` を通じてセッション状態を読み書き

**テスト:**
- 70テスト（ツール単体63 + エージェント統合7）
- ツールカバレッジ: 88%

詳細は `.steering/20260208-phase2a-adk-tools/` を参照。

---

## フロントエンド

`frontend/` に Next.js 16 ベースのフロントエンドを実装。コア機能実装完了（WebSocket統合・E2Eテスト含む）。

### コンポーネント・フック一覧

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

### 未実装（MVP後）

| 項目 | 状況 | 説明 |
|------|------|------|
| **追加キャラクター** | 低優先度 | 魔法使い、宇宙飛行士、動物（選択UIは実装済み） |

### テストカバレッジ

- **ユニットテスト**: 23テストファイル、194テスト（Vitest + Testing Library）
- **E2Eテスト**: 9テストファイル（Playwright）- スモーク・機能・統合
- 適切なモック（MediaDevices, AudioContext, WebSocket, AudioWorklet）

### 技術スタック

| 技術 | バージョン |
|------|----------|
| Next.js | 16 (App Router) |
| Bun | 最新 |
| TypeScript | strict mode |
| Tailwind CSS | v4 |
| Jotai | 状態管理 |
| Vitest | テスト |
| Biome | リンター/フォーマッター |

### 音声入力アーキテクチャ

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

---

## E2Eテスト

`frontend/e2e/` に Playwright ベースの E2E テストを実装。

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

---

## インフラストラクチャ（IaC）

`infrastructure/` ディレクトリにGCPインフラのIaC実装。

### Terraform モジュール構成

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

### Cloud Run 設定

| Service | CPU | Memory | Min | Max | Timeout |
|---------|-----|--------|-----|-----|---------|
| Frontend | 1 | 512Mi | 0 (dev) / 1 (prod) | 10 | 60s |
| Backend | 2 | 1Gi | 0 (dev) / 1 (prod) | 20 | 300s |

### Docker & CI/CD

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

### インフラデプロイ手順

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

GCPプロジェクト `homework-coach-robo` にデプロイ済み。

| サービス | URL | 状態 |
|---------|-----|------|
| **Frontend** | https://homework-coach-frontend-652907685934.asia-northeast1.run.app | 稼働中 |
| **Backend** | https://homework-coach-backend-652907685934.asia-northeast1.run.app | 稼働中 |

**ヘルスチェック:**
- Backend `/health`: `{"status":"healthy"}`
- Frontend `/api/health`: `{"status":"ok"}`

詳細は `.steering/20260206-application-deploy/COMPLETED.md` を参照。

---

## 技術検証（PoC）

`poc/` ディレクトリに技術検証の実装。

| 検証項目 | 結果 | 備考 |
|----------|------|------|
| Live API接続 | 成功 | ADK + google-genaiで正常接続 |
| 日本語音声入出力 | 動作 | 音声認識・合成ともに日本語対応 |
| ソクラテス式対話 | 動作 | システムプロンプトで実現 |
| レイテンシ | 約5秒 | プレビュー版の制約（目標2秒） |

**PoCで使用したモデル**: `gemini-2.5-flash-native-audio-preview-12-2025`
**本番使用モデル**: `gemini-live-2.5-flash-native-audio`（Vertex AI 安定版）

詳細は `.steering/20260131-gemini-live-api-poc/COMPLETED.md` を参照。

---

## ステアリングドキュメント一覧

| ディレクトリ | 内容 |
|-------------|------|
| `.steering/20260131-gemini-live-api-poc/` | Gemini Live API 技術検証 |
| `.steering/20260205-firestore-session-persistence/` | Firestore セッション永続化 |
| `.steering/20260205-adk-memory-bank-integration/` | ADK メモリバンク統合 |
| `.steering/20260205-adk-runner-integration/` | ADK Runner 統合 |
| `.steering/20260205-dialogue-api-integration/` | 対話 API 統合 |
| `.steering/20260205-infrastructure-implementation/` | インフラ実装 |
| `.steering/20260206-voice-input-implementation/` | 音声入力実装 |
| `.steering/20260206-application-deploy/` | アプリケーションデプロイ |
| `.steering/20260207-backend-websocket-streaming/` | WebSocket 音声ストリーミング |
| `.steering/20260207-frontend-websocket-integration/` | フロントエンド WebSocket 統合 |
| `.steering/20260207-e2e-tests/` | E2E テスト |
| `.steering/20260208-phase2a-adk-tools/` | Phase 2a ADK Function Tools |
