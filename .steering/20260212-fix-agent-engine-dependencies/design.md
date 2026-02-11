# Design - Fix Agent Engine Dependencies and Enable Dashboard/Tracing

## アーキテクチャ概要

Agent Engine のダッシュボードとトレースを有効化するため、以下の2つのファイルを更新する：

1. **backend/agent_engine_requirements.txt**: ランタイム依存関係
2. **backend/scripts/deploy_agent_engine.py**: デプロイスクリプトの requirements

Terraform での環境変数設定については、調査の結果、明確なドキュメントが見つからなかったため、依存関係のバージョン更新のみで対応する。

## 技術選定

### 依存関係のバージョン

Google の要求に基づき、以下のバージョンを使用：

- `google-cloud-aiplatform[agent_engines,adk]>=1.126.1`
- `google-adk>=1.18.0`

### Terraform での環境変数設定

調査の結果、Terraform の `google_vertex_ai_reasoning_engine` リソースでは、環境変数を設定するフィールドが明示的にドキュメント化されていない。Google の警告メッセージは Python SDK で直接デプロイする場合を指している可能性が高く、Terraform の場合は依存関係のバージョンが正しければ自動的にダッシュボードとトレースが有効になると考えられる。

## データ設計

変更なし（依存関係のバージョン更新のみ）。

## API設計

変更なし（依存関係のバージョン更新のみ）。

## ファイル構成

### 変更対象ファイル

1. **backend/agent_engine_requirements.txt**
   ```
   google-cloud-aiplatform[agent_engines,adk]>=1.126.1
   google-adk>=1.18.0
   cloudpickle==3.0.0
   google-cloud-firestore>=2.19.0
   pydantic>=2.12.0
   ```

2. **backend/scripts/deploy_agent_engine.py**
   - L80-82: `requirements` を更新
   - L121-124: `requirements` を更新
   ```python
   "requirements": [
       "google-cloud-aiplatform[adk,agent_engines]>=1.126.1",
       "google-adk>=1.18.0",
       "google-cloud-firestore>=2.19.0",
   ]
   ```

## 依存関係

- Google Cloud Vertex AI SDK: v1.126.1+
- Google ADK: v1.18.0+

## エラーハンドリング

- 依存関係のバージョン互換性エラー: CI/CD パイプラインで検出
- Terraform apply エラー: 手動介入が必要

## セキュリティ考慮事項

- 依存関係のバージョン更新による脆弱性修正の恩恵を受ける

## パフォーマンス考慮事項

- ダッシュボードとトレースの有効化により、モニタリングとデバッグが改善される

## 代替案と採用理由

### 代替案1: Terraform での環境変数設定を実装

調査したが、明確なドキュメントが見つからなかったため、実装を見送る。

### 採用案: 依存関係のバージョン更新のみ

まず依存関係のバージョンを更新し、実際にデプロイしてダッシュボードとトレースが有効になるかを確認する。必要に応じて追加対応を行う。
