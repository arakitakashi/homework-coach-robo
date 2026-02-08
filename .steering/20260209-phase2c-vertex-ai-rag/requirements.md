# Requirements - Phase 2c+3 統合: Vertex AI Memory Bank

## 背景・目的

現在の `FirestoreMemoryService` はキーワードベースの検索で、以下の重大な問題がある：

1. **日本語非対応**: `extract_words_lower()` が英語 `[A-Za-z]+` のみ抽出
2. **低精度**: 完全一致のみ（意味的類似度を考慮しない）
3. **スケーラビリティ**: 全エントリを走査する O(n) 検索

ADK 公式推奨の `VertexAiMemoryBankService` を導入する。

### VertexAiMemoryBankService の優位性

- **LLM パワード事実抽出**: 会話から意味のある情報を自動抽出・統合
- **セマンティック検索**: 日本語対応の高精度検索
- **マネージドサービス**: Google Cloud が管理するインフラ
- ADK の `BaseMemoryService` のドロップイン置換

### Agent Engine との関係

`VertexAiMemoryBankService` は Agent Engine（Reasoning Engine）ID を必要とする。
Agent Engine はインフラとして作成するだけで、エージェント全体のデプロイは不要。

## 要求事項

### 機能要件

1. **Agent Engine 管理**（#47 拡張）
   - Agent Engine 作成スクリプト
   - 環境変数 `AGENT_ENGINE_ID` で ID を管理

2. **メモリサービスの切り替え**（#48）
   - `VertexAiMemoryBankService` を DI 経由で提供
   - `AGENT_ENGINE_ID` 設定時 → `VertexAiMemoryBankService`
   - `AGENT_ENGINE_ID` 未設定時 → `FirestoreMemoryService` にフォールバック
   - Review Agent に `load_memory` ツールを追加

3. **FirestoreMemoryService からの移行**（#49）
   - 移行ガイドの作成
   - フォールバック機構による安全な切り替え

### 非機能要件

- テストカバレッジ 80% 以上を維持
- 既存テストに影響を与えない
- Vertex AI API 呼び出しはすべてモック可能

### 制約条件

- ADK の `VertexAiMemoryBankService` をそのまま利用
- Agent Engine の作成は `vertexai.Client().agent_engines.create()` を使用
- GCP プロジェクト設定・認証は環境変数で管理

## 対象範囲

### In Scope

- メモリサービスファクトリ（設定ベースの切り替え）
- Review Agent への `load_memory` ツール追加
- DI 更新（dialogue_runner.py, voice_stream.py）
- Agent Engine 作成スクリプト
- テスト（VertexAI API モック）

### Out of Scope

- Terraform による Agent Engine インフラ構築
- エージェント全体の Agent Engine へのデプロイ
- VertexAiSessionService への移行（別途検討）
- フロントエンド変更

## 成功基準

- `VertexAiMemoryBankService` が Runner に正しく注入される
- Review Agent が `load_memory` ツールで過去の学習履歴を検索できる
- 環境変数未設定時は `FirestoreMemoryService` にフォールバック
- 全テストパス、カバレッジ 80% 以上
- Ruff / mypy エラーなし
