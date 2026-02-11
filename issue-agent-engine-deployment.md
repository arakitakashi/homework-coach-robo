# Agent Engine デプロイの実装と本番環境修正

## 概要
現在、本番環境で以下のエラーが発生しており、アプリケーションが正常に動作していません：

1. `ValueError: Missing key inputs argument!` - Google GenAI API初期化エラー
2. `AttributeError: 'BaseApiClient' object has no attribute '_async_httpx_client'`
3. `NotFound: 404 The ReasoningEngine does not exist.` - Agent Engineリソースが存在しない

## 根本原因
Terraformで `enable_agent_engine = true` に設定されているが、実際のAgent Engineリソースがデプロイされていない。

**現在の状態**:
- ✅ Terraform設定は完了（`modules/agent_engine`）
- ❌ Agent Engineアーティファクト（pickle.pkl, requirements.txt, dependencies.tar.gz）が未作成
- ❌ CI/CDパイプラインにAgent Engineデプロイジョブが存在しない
- ❌ Phase 2フラグ（tools/multi-agent/emotion）が無効のため、環境変数が不足

## 期待動作
1. Agent Engineが正しくデプロイされ、`AGENT_ENGINE_RESOURCE_NAME`が有効なリソースを参照
2. フォールバック：Agent Engineが利用できない場合、ローカルRunnerに自動的にフォールバック
3. Phase 2機能が有効化され、必要な環境変数が設定される

## 対応タスク

### 1. 緊急対応（即座の修正）
- [ ] `terraform.tfvars`でPhase 2フラグを有効化
  ```hcl
  enable_phase2_tools = true
  enable_phase2_multi_agent = true
  enable_phase2_emotion = true
  ```
- [ ] 一時的に`enable_agent_engine = false`に設定（ローカルRunnerで動作確認）
- [ ] Terraform apply実行
- [ ] 本番環境で動作確認

### 2. Agent Engineアーティファクト作成
- [ ] `backend/scripts/build_agent_artifacts.py`スクリプト作成
  - Router Agent、Math Coach、Japanese Coach、Encouragement、Review Agentのpickle化
  - requirements.txt生成（google-genai、google-adk等）
  - dependencies.tar.gz作成（カスタムモジュール）
- [ ] GCS URIへのアップロード自動化
  - `gs://homework-coach-assets-{suffix}/agent-engine/pickle.pkl`
  - `gs://homework-coach-assets-{suffix}/agent-engine/requirements.txt`
  - `gs://homework-coach-assets-{suffix}/agent-engine/dependencies.tar.gz`

### 3. CI/CDパイプライン拡張
- [ ] `.github/workflows/cd.yml`に`deploy-agent-engine`ジョブ追加
  - トリガー：backendディレクトリの変更検知（`paths: backend/**`）
  - 処理：
    1. アーティファクトビルドスクリプト実行
    2. GCSへアップロード
    3. Terraform apply（Agent Engineリソース更新）
- [ ] バックエンドデプロイ完了後にAgent Engineデプロイを実行

### 4. Terraform変数管理
- [ ] `environments/dev/terraform.tfvars`にPhase 2/3フラグの明示的な設定追加
- [ ] Terraform outputで`AGENT_ENGINE_RESOURCE_NAME`を出力
- [ ] Cloud Run環境変数に確実に反映されるよう検証

### 5. エラーハンドリング改善
- [ ] `dialogue_runner.py`のエラーハンドリング強化
  - Agent Engine接続失敗時のフォールバック処理
  - より詳細なエラーログ
- [ ] `session_factory.py`のVertex AI初期化エラーハンドリング

### 6. ドキュメント更新
- [ ] Agent Engineデプロイ手順をREADME.mdに追加
- [ ] `docs/implementation-status.md`の「CI/CD」セクション更新
- [ ] トラブルシューティングガイド作成

## 関連ファイル
- `infrastructure/terraform/modules/agent_engine/main.tf`
- `infrastructure/terraform/environments/dev/main.tf`
- `infrastructure/terraform/environments/dev/terraform.tfvars`
- `backend/app/api/v1/dialogue_runner.py`
- `backend/app/services/adk/sessions/session_factory.py`
- `.github/workflows/cd.yml`

## 優先度
**P0 (Critical)** - 本番環環境が動作していないため、緊急対応が必要

## ラベル
- infrastructure
- bug
- Phase 3

## Milestone
Phase 3: Agent Engine デプロイ基盤
