# Requirements - Fix Agent Engine Dependencies and Enable Dashboard/Tracing

## 背景・目的

Agent Engine のダッシュボードとトレースが使用不可の状態になっている。GCP コンソールで以下の警告が表示される：

> このエージェントではダッシュボードとトレースを使用できません。考えられる理由は次のいずれかです。
>
> - 古い依存関係: エージェントが v1.126.1 以上の google-cloud-aiplatform と v1.18.0 以上の google-adk を使用していることを確認してください
> - 手動 API デプロイ: エージェントが新しいバージョンを使用している場合でも、API を介してデプロイするときは、環境変数を明示的に設定する必要があります

本作業では、依存関係のバージョンを更新し、必要に応じて環境変数を設定して、ダッシュボードとトレースを有効化する。

## 要求事項

### 機能要件

1. **依存関係のバージョン更新**
   - `google-cloud-aiplatform[agent_engines,adk]>=1.126.1`
   - `google-adk>=1.18.0`
   - 以下のファイルを更新：
     - `backend/agent_engine_requirements.txt`
     - `backend/scripts/deploy_agent_engine.py`

2. **Terraform での環境変数設定（必要に応じて）**
   - `google_vertex_ai_reasoning_engine` リソースに環境変数を追加する方法を調査
   - 必要に応じて `spec.environment_variables` などを追加

3. **Agent Engine 再デプロイ**
   - CI/CD パイプラインで自動デプロイ（`.github/workflows/cd.yml`）
   - Terraform apply で Agent Engine 更新

### 非機能要件

1. **後方互換性**: 既存の機能に影響を与えない
2. **検証可能性**: GCP コンソールでダッシュボードとトレースが表示されることを確認

### 制約条件

1. Terraform google-beta provider の機能に依存
2. GCP のドキュメントに従った環境変数設定が必要な場合がある

## 対象範囲

### In Scope

- `backend/agent_engine_requirements.txt` のバージョン更新
- `backend/scripts/deploy_agent_engine.py` の requirements 更新
- Terraform での環境変数設定の調査と実装（必要に応じて）
- CI/CD パイプラインでの自動デプロイ

### Out of Scope

- Agent Engine の機能追加・変更
- バックエンドコードの変更

## 成功基準

- [ ] `agent_engine_requirements.txt` のバージョンが最新（`>=1.126.1`, `>=1.18.0`）
- [ ] `deploy_agent_engine.py` の requirements が最新
- [ ] Terraform で環境変数が設定されている（必要に応じて）
- [ ] CI/CD パイプラインで新しいアーティファクトがデプロイされる
- [ ] `terraform apply` で Agent Engine が更新される
- [ ] GCP コンソールでダッシュボードとトレースが使用可能になる
