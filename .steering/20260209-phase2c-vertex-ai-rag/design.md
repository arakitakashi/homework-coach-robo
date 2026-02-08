# Design - Phase 2c+3 統合: Vertex AI Memory Bank

## アーキテクチャ概要

ADK 公式推奨の `VertexAiMemoryBankService` を導入し、LLM パワードの事実抽出 + セマンティック検索を実現する。

```
Runner
  │
  ├── session_service: FirestoreSessionService（変更なし）
  └── memory_service: VertexAiMemoryBankService（新規）← FirestoreMemoryService から置換
                         │
                         └── Vertex AI Agent Engine
                              └── Memory Bank（LLM 事実抽出 + セマンティック検索）
```

### VertexAiMemoryBankService の動作

**add_session_to_memory():**
1. セッションイベントを Agent Engine の `memories.generate()` API に送信
2. LLM が会話から意味のある「事実」を抽出・統合
3. 既存メモリと自動的にマージ

**search_memory():**
1. `memories.retrieve()` API にクエリを送信
2. セマンティック検索で関連する事実を返却
3. `MemoryEntry` 形式で結果を返す

## 技術選定

| コンポーネント | 選定 | 理由 |
|---|---|---|
| メモリサービス | `VertexAiMemoryBankService` | ADK 公式推奨、LLM パワード |
| メモリ検索ツール | `load_memory`（ADK 組み込み） | Runner の memory_service を自動使用 |
| Agent Engine | `vertexai.Client().agent_engines.create()` | Memory Bank のインフラ |
| フォールバック | `FirestoreMemoryService` | AGENT_ENGINE_ID 未設定時 |

## データ設計

### Memory Bank の保存形式

Memory Bank は LLM が自動的に事実を抽出する：

```
入力（セッションイベント）:
  user: "23 + 45 がわからない"
  agent: "一の位から計算してみよう。3 + 5 はいくつ？"
  user: "8！"
  agent: "すごい！じゃあ十の位は？"

↓ LLM 事実抽出

保存される事実:
  - "ユーザーは 23+45 の計算で、一の位の足し算は自力で解けた"
  - "十の位の足し算はヒントが必要だった"
```

### 設定（環境変数）

| 変数名 | 説明 | 必須 | デフォルト |
|---|---|---|---|
| `AGENT_ENGINE_ID` | Agent Engine ID（数字のみ） | No | 未設定 → Firestore フォールバック |
| `GCP_PROJECT_ID` | GCP プロジェクト ID | 条件付き | なし |
| `GCP_LOCATION` | GCP リージョン | No | `us-central1` |

## ファイル構成

### 新規ファイル

```
backend/app/services/adk/memory/
├── memory_factory.py           # メモリサービスファクトリ（新規）

backend/scripts/
└── create_agent_engine.py      # Agent Engine 作成スクリプト（新規）

backend/tests/unit/services/adk/memory/
├── test_memory_factory.py      # ファクトリテスト（新規）

backend/tests/unit/services/adk/agents/
└── test_review.py              # Review Agent テスト更新
```

### 変更ファイル

- `app/services/adk/agents/review.py` - `load_memory` ツール追加
- `app/services/adk/memory/__init__.py` - エクスポート追加
- `app/api/v1/dialogue_runner.py` - メモリサービスファクトリ使用
- `app/api/v1/voice_stream.py` - メモリサービスファクトリ使用

## エラーハンドリング

- `AGENT_ENGINE_ID` 未設定: ログ情報 + `FirestoreMemoryService` にフォールバック
- Agent Engine 接続失敗: 例外を上位に伝播（Runner が処理）
- メモリ検索失敗: 空の結果を返却（VertexAiMemoryBankService の挙動に従う）

## セキュリティ考慮事項

- Agent Engine は GCP プロジェクトの IAM で保護
- `VertexAiMemoryBankService` は `app_name` + `user_id` でスコープ分離
- 子供の学習データは GCP 内で暗号化保存
- `AGENT_ENGINE_ID` は環境変数で管理（コードにハードコードしない）

## 代替案と採用理由

| 案 | 説明 | 採否 |
|----|------|------|
| VertexAiMemoryBankService | ADK 公式推奨、LLM 事実抽出 | **採用** |
| VertexAiRagMemoryService | RAG Corpus ベース | 不採用 - ドキュメント非推奨、生テキスト保存のみ |
| カスタム実装 | 独自の embedding + 検索 | 不採用 - 車輪の再発明 |
| Firestore Vector Search | Firestore のベクトル検索 | 不採用 - ADK 非対応 |
