# Implementation Status

このドキュメントは、宿題コーチロボットの実装済み機能の詳細を記録します。

**プロジェクトステータス**: MVP実装完了・Phase 2d（感情適応）実装完了・Phase 2 フロントエンドWebSocketハンドラ統合完了

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
- **マルチエージェント構成 (Phase 2b)**: Router Agent + 4サブエージェント（Math Coach, Japanese Coach, Encouragement, Review）実装完了
- **フロントエンド Phase 2 型定義・状態管理**: Phase 2a-2d 対応の型定義（25型）+ Jotai atoms（12個）実装完了
- **Memory Bank 統合 (Phase 2c+3)**: VertexAiMemoryBankService ファクトリパターン + Agent Engine 作成スクリプト + Review Agent に load_memory ツール追加
- **感情適応 (Phase 2d)**: update_emotion_tool + Router Agent 感情ベースルーティング + サブエージェント感情コンテキスト参照
- **フロントエンド Phase 2a ツール実行状態UI**: ToolExecutionDisplayコンポーネント + WebSocket/フック拡張 + SessionContent統合
- **フロントエンド Phase 2 WebSocketハンドラ統合**: AgentTransition（Phase 2b）・EmotionUpdate（Phase 2d）イベントハンドラ + Jotai atoms接続（291テスト）

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

**テストカバレッジ**: 90%（526テスト）

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
| `agent.py` | SOCRATIC_SYSTEM_PROMPT, create_socratic_agent()（音声ストリーミング用） |
| `runner_service.py` | AgentRunnerService（Router Agent + SessionService/MemoryService統合） |

**主要機能:**
- `create_socratic_agent()`: 音声ストリーミング用の単一エージェント（レガシー）
- `create_router_agent()`: マルチエージェント構成のルートエージェント（Phase 2b）
- `AgentRunnerService.run()`: 非同期イベントストリームでエージェント実行
- `AgentRunnerService.extract_text()`: イベントからテキスト抽出

**アーキテクチャ:**
```
AgentRunnerService
├── Runner (ADK)
│   ├── Router Agent (AutoFlow, tools=[update_emotion])
│   │   ├── Math Coach Agent (tools=[calculate, hint, curriculum, progress])
│   │   ├── Japanese Coach Agent (tools=[hint, curriculum, progress])
│   │   ├── Encouragement Agent (tools=[progress])
│   │   └── Review Agent (tools=[progress, load_memory])
│   ├── FirestoreSessionService
│   └── BaseMemoryService (factory: Firestore or VertexAiMemoryBank)
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

### マルチエージェント構成 (Phase 2b)

`backend/app/services/adk/agents/` に ADK マルチエージェント構成を実装。Router Agent が子供の入力を分析し、ADK AutoFlow で最適なサブエージェントに委譲する。

| エージェント | ファイル | 役割 | ツール |
|-------------|---------|------|--------|
| `router_agent` | `router.py` | 感情を分析し最適なサブエージェントに委譲 | update_emotion |
| `math_coach` | `math_coach.py` | 算数専門のソクラテス式対話 | calculate, hint, curriculum, progress |
| `japanese_coach` | `japanese_coach.py` | 国語専門のソクラテス式対話 | hint, curriculum, progress |
| `encouragement_agent` | `encouragement.py` | 感情サポート・休憩提案 | progress |
| `review_agent` | `review.py` | セッション振り返り・保護者レポート | progress, load_memory |

**プロンプト構成:**

各エージェントは `agents/prompts/` 配下に専用のシステムプロンプトを持つ。すべてのプロンプトはソクラテス式対話の原則（答えを教えない、プロセスを評価）に従う。

**エージェント間委譲（ADK AutoFlow）:**

Router Agent が `sub_agents` パラメータで4つのサブエージェントを保持。LLMが入力内容に基づき `transfer_to_agent(agent_name='...')` を自動生成し、適切なエージェントに委譲する。

**統合:**
- `AgentRunnerService` が `create_router_agent()` をルートエージェントとして使用
- 既存の SSE エンドポイント（`/api/v1/dialogue/run`）は変更なしで動作
- テスト: 72テスト（エージェント単体）、カバレッジ100%

詳細は `.steering/20260208-phase2b-multi-agent/` を参照。

### Memory Bank 統合 (Phase 2c+3)

`backend/app/services/adk/memory/` にメモリサービスファクトリパターンを導入。ADK 公式の `VertexAiMemoryBankService` を使用し、LLM による事実抽出 + セマンティック検索を実現する。

| コンポーネント | ファイル | 説明 |
|--------------|---------|------|
| `memory_factory.py` | `memory/memory_factory.py` | `create_memory_service()` ファクトリ関数 |
| `create_agent_engine.py` | `scripts/create_agent_engine.py` | Agent Engine 作成 CLI スクリプト |

**メモリサービス切り替え:**

| 環境変数 | 使用サービス | 検索方式 |
|---------|------------|---------|
| `AGENT_ENGINE_ID` 未設定 | `FirestoreMemoryService` | キーワードマッチ（フォールバック） |
| `AGENT_ENGINE_ID` 設定済み | `VertexAiMemoryBankService` | LLM事実抽出 + セマンティック検索 |

**環境変数:**

| 変数名 | 必須 | 説明 |
|--------|------|------|
| `AGENT_ENGINE_ID` | 任意 | Agent Engine ID（設定時 Memory Bank 有効化） |
| `GCP_PROJECT_ID` | 任意 | GCP プロジェクト ID（Memory Bank 使用時） |
| `GCP_LOCATION` | 任意 | GCP ロケーション（Memory Bank 使用時） |

**DI 更新:**
- `dialogue_runner.py` と `voice_stream.py` の `get_memory_service()` をファクトリベースに変更
- 型を `FirestoreMemoryService` → `BaseMemoryService` に抽象化

**Review Agent 拡張:**
- ADK 組み込み `load_memory` ツールを追加（過去の学習履歴のセマンティック検索）
- ツール数: 1 → 2（`record_progress_tool` + `load_memory`）

**Agent Engine 作成手順:**
```bash
uv run python scripts/create_agent_engine.py --project <project-id> --location us-central1
# 出力された ID を環境変数に設定:
# export AGENT_ENGINE_ID=<engine-id>
```

**テスト:** 10テスト（ファクトリ8 + Review Agent 2）、カバレッジ100%

詳細は `.steering/20260209-phase2c-vertex-ai-rag/` を参照。

### 感情適応 (Phase 2d)

`backend/app/services/adk/tools/emotion_analyzer.py` に感情分析ツールを実装。Router Agent が毎ターン感情を分析し、感情ベースのルーティングを行う。サブエージェントのプロンプトにも感情コンテキスト参照セクションを追加。

| コンポーネント | ファイル | 説明 |
|--------------|---------|------|
| `update_emotion_tool` | `tools/emotion_analyzer.py` | 感情スコア記録 + support_level/action_recommended 計算 |
| Router Agent 更新 | `agents/router.py` | `tools=[update_emotion_tool]` 追加 |
| Router プロンプト更新 | `agents/prompts/router.py` | 感情分析指示 + 感情ベースルーティング基準 |
| サブエージェントプロンプト | `agents/prompts/*.py` | 感情コンテキスト参照セクション追加 |

**感情スコア（session.state["emotion"]に記録）:**

| スコア | 範囲 | 説明 |
|--------|------|------|
| `frustration` | 0.0-1.0 | イライラ度 |
| `confidence` | 0.0-1.0 | 自信度 |
| `fatigue` | 0.0-1.0 | 疲労度 |
| `excitement` | 0.0-1.0 | 興奮度 |
| `primary_emotion` | enum | frustrated/confident/confused/happy/tired/neutral |

**サポートレベル計算:**

| 条件 | support_level | action_recommended |
|------|--------------|-------------------|
| frustration > 0.7 OR fatigue > 0.6 | intensive | encourage / rest |
| frustration > 0.4 OR fatigue > 0.3 | moderate | continue |
| それ以外 | minimal | continue |

**感情ベースルーティング（内容より優先）:**
- `frustration > 0.7` → encouragement_agent に委譲
- `fatigue > 0.6` → encouragement_agent に委譲（休憩提案）

**テスト:** 22テスト（ツール20 + Router 2）、カバレッジ90%

詳細は `.steering/20260209-phase2d-emotion-adaptation/` を参照。

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
| **型定義** | `types/` | dialogue, session, audio, websocket, phase2 |
| **Phase 2 状態管理** | `store/atoms/phase2.ts` | Phase 2a-2d 対応の12個のJotai atoms |

### 未実装（MVP後）

| 項目 | 状況 | 説明 |
|------|------|------|
| **追加キャラクター** | 低優先度 | 魔法使い、宇宙飛行士、動物（選択UIは実装済み） |

### Phase 2 型定義・状態管理基盤

`frontend/types/phase2.ts` および `frontend/store/atoms/phase2.ts` に Phase 2a-2d 対応の型定義と状態管理を実装。既存の型は後方互換性を維持しつつオプショナルフィールドで拡張。

**型定義（`types/phase2.ts`）:**

| Phase | 型名 | 説明 |
|-------|------|------|
| **2a** | `ToolName`, `ToolExecutionStatus`, `ToolExecution` | ツール実行の状態管理 |
| **2a** | `CalculationResult`, `HintManagementResult`, `ProgressRecordResult`, `CurriculumCheckResult`, `ImageAnalysisResult` | 各ツールの結果型 |
| **2b** | `SubjectType`, `AgentType`, `ActiveAgent`, `AgentTransition` | マルチエージェント構成 |
| **2c** | `MemoryType`, `RetrievedMemory` | RAGセマンティック記憶 |
| **2d** | `EmotionType`, `EmotionAnalysis`, `SupportLevel`, `DialogueTone`, `EmotionAdaptation` | 感情適応 |
| **共通** | `QuestionType`, `ResponseAnalysis`, `ThinkingTendencies`, `SubjectUnderstanding`, `SessionSummary`, `ChildLearningProfile` | 学習プロファイル・分析 |

**既存型の拡張（後方互換）:**
- `DialogueTurn`（`dialogue.ts`）: `questionType?`, `responseAnalysis?`, `emotion?`, `activeAgent?`, `toolExecutions?` を追加
- `LearningProgress`（`session.ts`）: `currentSubject?`, `currentTopic?`, `thinkingTendencies?` を追加
- `WebSocketIncomingMessage`（`websocket.ts`）: `ToolExecutionMessage`, `AgentTransitionMessage`, `EmotionUpdateMessage` を追加

**Jotai Atoms（`store/atoms/phase2.ts`）:**

| Phase | Atom | 型 | 説明 |
|-------|------|---|------|
| 2a | `activeToolExecutionsAtom` | `ToolExecution[]` | 現在実行中のツール |
| 2a | `toolExecutionHistoryAtom` | `ToolExecution[]` | ツール実行履歴 |
| 2a | `isToolRunningAtom` | `boolean`（派生） | ツール実行中フラグ |
| 2b | `activeAgentAtom` | `ActiveAgent \| null` | 現在のアクティブエージェント |
| 2b | `agentTransitionHistoryAtom` | `AgentTransition[]` | エージェント切り替え履歴 |
| 2c | `retrievedMemoriesAtom` | `RetrievedMemory[]` | RAG検索結果 |
| 2d | `emotionAnalysisAtom` | `EmotionAnalysis \| null` | 現在の感情分析結果 |
| 2d | `emotionAdaptationAtom` | `EmotionAdaptation \| null` | 感情適応設定 |
| 2d | `emotionHistoryAtom` | `EmotionAnalysis[]` | 感情分析履歴 |
| 共通 | `learningProfileAtom` | `ChildLearningProfile \| null` | 学習プロファイル |

**テスト:** 37型テスト + 27 atomテスト = 64テスト

詳細は `.steering/20260208-frontend-phase2-types/COMPLETED.md` を参照。

### Phase 2a ツール実行状態UIコンポーネント

バックエンドのADK Function Tools（calculate_tool等）がリアルタイムで実行される際、その状態をフロントエンドUIに表示する機能を実装。

**新規コンポーネント:**

| コンポーネント | 説明 |
|-------------|------|
| `ToolExecutionDisplay` | ツール実行状態のリアルタイム表示（ローディング/完了/エラー） |

**ツール名の日本語マッピング:**

| ToolName | 表示名 |
|----------|--------|
| `calculate_tool` | けいさん |
| `manage_hint_tool` | ヒント |
| `record_progress_tool` | きろく |
| `check_curriculum_tool` | きょうかしょ |
| `analyze_image_tool` | しゃしん |

**WebSocket/フック拡張:**
- `ADKEvent` 型に `toolExecution` フィールド追加（`ADKToolExecutionEvent`）
- `VoiceWebSocketOptions` に `onToolExecution` コールバック追加
- `VoiceWebSocketClient.processADKEvent` でツール実行イベントをハンドリング
- `useVoiceStream` フックに `onToolExecution` パススルー追加

**SessionContent統合:**
- Jotai atoms（`activeToolExecutionsAtom`, `isToolRunningAtom`）経由で`ToolExecutionDisplay`に接続
- `CharacterDisplay`と`DialogueHistory`の間に配置
- アクセシビリティ対応（`role="status"`, `aria-live="polite"`）

**データフロー:**
```
VoiceWebSocketClient (ADKEvent) → useVoiceStream (callback) → SessionContent (Jotai atoms) → ToolExecutionDisplay (UI)
```

**テスト:** ToolExecutionDisplay(13) + VoiceWebSocket(+3) + useVoiceStream(+1) + SessionContent(+2) = 19新規テスト

詳細は `.steering/20260209-phase2a-tool-execution-ui/` を参照。

### Phase 2 WebSocketメッセージハンドラ統合（PR #77）

Phase 2a で実装した ToolExecution ハンドラと同一パターンで、残り2つの Phase 2 イベント（AgentTransition, EmotionUpdate）のWebSocketハンドラを追加。

**追加イベントハンドラ:**

| イベント | Phase | ハンドラ | 更新Jotai atoms |
|---------|-------|---------|----------------|
| AgentTransition | 2b | `handleAgentTransition` | `activeAgentAtom`, `agentTransitionHistoryAtom` |
| EmotionUpdate | 2d | `handleEmotionUpdate` | `emotionAnalysisAtom`, `emotionHistoryAtom` |

**変更ファイル:**
- `frontend/lib/api/types.ts` - `ADKAgentTransitionEvent`, `ADKEmotionUpdateEvent` 型追加、`ADKEvent`・`VoiceWebSocketOptions` 拡張
- `frontend/lib/api/voiceWebSocket.ts` - `processADKEvent()` にイベントディスパッチ追加
- `frontend/lib/hooks/useVoiceStream.ts` - コールバックパススルー追加
- `frontend/src/app/session/SessionContent.tsx` - ハンドラ実装 + Jotai atoms接続

**データフロー:**
```
VoiceWebSocketClient (ADKEvent) → useVoiceStream (callback) → SessionContent (Jotai atoms) → UI
```

**テスト:** VoiceWebSocket(+6) + useVoiceStream(+2) + SessionContent(+4) = 12新規テスト

詳細は `.steering/20260209-phase2-websocket-handlers/` を参照。

### テストカバレッジ

- **ユニットテスト**: 26テストファイル、291テスト（Vitest + Testing Library）
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
| `.steering/20260208-phase2b-multi-agent/` | Phase 2b マルチエージェント構成 |
| `.steering/20260208-frontend-phase2-types/` | フロントエンド Phase 2 型定義・状態管理基盤 |
| `.steering/20260209-phase2a-tool-execution-ui/` | Phase 2a フロントエンド ツール実行状態UI |
| `.steering/20260209-phase2c-vertex-ai-rag/` | Phase 2c Memory Bank 統合 + Agent Engine |
| `.steering/20260209-phase2d-emotion-adaptation/` | Phase 2d 感情適応（update_emotion_tool + 感情ベースルーティング） |
| `.steering/20260209-phase2-websocket-handlers/` | Phase 2 WebSocket メッセージハンドラ統合 |
