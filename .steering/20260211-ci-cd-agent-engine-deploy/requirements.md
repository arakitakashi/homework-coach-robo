# Requirements - CI/CD Agent Engine Artifact Deployment

## 背景・目的

### 現状の課題

現在のCD workflow（`.github/workflows/cd.yml`, `.github/workflows/deploy.yml`）では、Cloud Runコンテナイメージの更新のみを行っており、Agent Engineアーティファクトのデプロイが自動化されていません。

**影響:**
- `backend/app/services/adk/agents/`, `backend/app/services/adk/tools/` のコード変更が Agent Engine に反映されない
- 手動で以下の3ステップを実行する必要がある：
  1. `uv run python scripts/serialize_agent.py` でシリアライズ
  2. `gcloud storage cp` でGCSにアップロード
  3. `terraform taint` + `terraform apply` で Agent Engine 再作成

### 目的

バックエンドコード変更時に、Agent Engineアーティファクト（pickle.pkl、requirements.txt、dependencies.tar.gz）を自動的にデプロイすることで、手動操作を削減し、開発フローを効率化する。

---

## 要求事項

### 機能要件

#### FR1: バックエンド変更検知

- **条件**: `git diff` で `backend/` ディレクトリ配下のファイル変更を検知
- **精緻化オプション**: `backend/app/services/adk/agents/`, `backend/app/services/adk/tools/` のみを対象にするか検討

#### FR2: Agent Engineアーティファクトのビルド

バックエンド変更が検知された場合、以下を自動実行：

1. **エージェントシリアライズ**
   - `uv run python scripts/serialize_agent.py`
   - 出力: `backend/pickle.pkl`

2. **依存関係パッケージ化**
   - `tar -czf dependencies.tar.gz app/`
   - 出力: `backend/dependencies.tar.gz`

3. **requirements.txt 準備**
   - `backend/agent_engine_requirements.txt` を使用

#### FR3: GCSへのアップロード

ビルドしたアーティファクトをGCSにアップロード：

- `pickle.pkl` → `gs://${BUCKET_NAME}/agent-engine/pickle.pkl`
- `requirements.txt` → `gs://${BUCKET_NAME}/agent-engine/requirements.txt`
- `dependencies.tar.gz` → `gs://${BUCKET_NAME}/agent-engine/dependencies.tar.gz`

**BUCKET_NAME取得方法:**
```bash
gcloud storage buckets list --format="value(name)" --filter="name:homework-coach-assets"
```

#### FR4: Agent Engine再作成（オプション）

**検討事項:**
- Agent Engine再作成には5-10分かかる
- CI/CDの実行時間が大幅に増加する

**提案:**
- Phase 1: アーティファクトのアップロードのみ自動化（手動で `terraform taint` + `terraform apply`）
- Phase 2（将来）: Terraform API呼び出しで自動再作成を検討

### 非機能要件

#### NFR1: 条件付き実行

- バックエンド変更がない場合、Agent Engine関連ステップはスキップする
- 実行時間の短縮（フロントエンドのみの変更時）

#### NFR2: エラーハンドリング

- GCSアップロードが失敗した場合、CI/CDを失敗とする
- エラーメッセージを明示的に表示

#### NFR3: セキュリティ

- GCS認証はWorkload Identity Federation経由で行う（既存の `google-github-actions/auth` を利用）
- アーティファクトにはシークレット情報を含めない

### 制約条件

#### C1: 既存ワークフローとの整合性

- `.github/workflows/cd.yml` を拡張する形で実装
- 既存のCloud Runデプロイフローを壊さない

#### C2: Terraformの責務分離

- TerraformはAgent Engineリソース定義のみを管理
- アーティファクトのビルド・アップロードはCI/CDで行う
- `lifecycle { ignore_changes = [image] }` の設計思想を維持

#### C3: フォールバック機構の維持

- Agent Engineが利用不可の場合、Firestoreセッション + ローカルRunnerで動作
- フォールバック機構は壊さない

---

## 対象範囲

### In Scope

- `.github/workflows/cd.yml` への条件付きステップ追加
- バックエンド変更検知ロジック
- Agent Engineアーティファクトのビルド・GCSアップロード
- エラーハンドリング

### Out of Scope

- Agent Engine自動再作成（将来のPhase 2で検討）
- `deploy.yml` への同様の変更（必要に応じて別途実装）
- Terraform側の変更（既存の設計を維持）

---

## 成功基準

### SC1: 自動デプロイの動作確認

1. `backend/app/services/adk/agents/router.py` に小さな変更を加える
2. `main` ブランチにマージして `cd.yml` をトリガー
3. 以下が自動実行されることを確認：
   - エージェントシリアライズ
   - 依存関係パッケージ化
   - GCSへのアップロード
4. GCS上のアーティファクトが更新されていることを確認

### SC2: 条件分岐の動作確認

1. フロントエンドのみの変更で `cd.yml` をトリガー
2. Agent Engine関連ステップがスキップされることを確認
3. CI/CD実行時間が短いことを確認

### SC3: エラーハンドリング

1. 意図的にシリアライズエラーを発生させる
2. CI/CDが適切に失敗することを確認
3. エラーメッセージが明示的に表示されることを確認

---

## 優先度

**Priority: P1（中）**

- Phase 2/3機能の本番反映には必要
- フォールバック機構により、Agent Engineなしでも動作可能
- 開発効率向上のため、早期実装が望ましい

---

## 関連イシュー・ドキュメント

- [#101](https://github.com/arakitakashi/homework-coach-robo/issues/101): CI/CD: Automate Agent Engine artifact deployment in cd.yml
- [#94](https://github.com/arakitakashi/homework-coach-robo/issues/94): Phase 2: Backend WebSocket イベント送信実装
- `infrastructure/terraform/modules/agent_engine/README.md`: Agent Engineデプロイ手順
- `.github/workflows/cd.yml`: 現在のCD workflow
