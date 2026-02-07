# Task List - CI/CD Workflow Improvements

## Phase 1: GitHub Secrets設定

- [x] `GCP_WORKLOAD_IDENTITY_PROVIDER` Secretを設定
- [x] `GCP_SERVICE_ACCOUNT` Secretを設定
- [x] Secrets設定を確認

## Phase 2: CDワークフロー改善

- [x] CDワークフローにCI依存を追加（reusable workflowsパターン）
- [x] CI workflowsに`workflow_call`トリガーを追加

## Phase 3: マニュアルデプロイワークフロー作成

- [x] `deploy.yml`を作成（`workflow_dispatch`トリガー）
- [x] Backend/Frontend/Both選択機能
- [x] ヘルスチェック検証ステップ追加
- [x] 条件分岐ロジック（skipped依存の処理）

## Phase 4: 動作確認

- [ ] コミット・プッシュ
- [ ] PR作成
- [ ] CDワークフローの動作確認
