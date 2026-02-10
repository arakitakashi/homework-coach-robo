# Task List - CI/CD Agent Engine Artifact Deployment

## Phase 1: 事前確認

- [ ] 現在のブランチ確認（feature/ci-cd-agent-engine-deploy）
- [ ] ステアリングディレクトリ作成（`.steering/20260211-ci-cd-agent-engine-deploy/`）
- [ ] requirements.md, design.md 作成完了
- [ ] 既存のserialize_agent.pyスクリプト確認
- [ ] 既存のagent_engine_requirements.txt確認

---

## Phase 2: ローカルでのスクリプト検証（TDD準備）

### 2.1 シリアライズスクリプトの動作確認

- [ ] backend/ディレクトリで `uv sync` 実行
- [ ] `uv run python scripts/serialize_agent.py` 実行
- [ ] pickle.pkl が生成されることを確認
- [ ] pickle.pkl のサイズが妥当であることを確認（数KB以上）

### 2.2 依存関係パッケージ化の確認

- [ ] `tar -czf dependencies.tar.gz app/` 実行
- [ ] dependencies.tar.gz が生成されることを確認
- [ ] tar内容の確認: `tar -tzf dependencies.tar.gz | head -20`
- [ ] 不要なファイル（.env, .venv）が含まれていないことを確認

### 2.3 GCSバケット存在確認（ローカル）

- [ ] gcloud認証確認: `gcloud auth list`
- [ ] バケット確認: `gcloud storage buckets list --filter="name:homework-coach-assets"`
- [ ] バケット名の取得ロジック確認

---

## Phase 3: ワークフロー実装

### 3.1 cd.yml に deploy-agent-engine ジョブ追加

- [ ] `.github/workflows/cd.yml` を読み込み
- [ ] 新しいジョブ `deploy-agent-engine` を追加
  - [ ] ジョブ基本設定（name, runs-on, needs, permissions）
  - [ ] Step 1: Checkout（fetch-depth: 0）
  - [ ] Step 2: バックエンド変更検知（git diff）
  - [ ] Step 3: Python環境セットアップ（条件付き）
  - [ ] Step 4: uv インストール（条件付き）
  - [ ] Step 5: バックエンド依存関係インストール（条件付き）
  - [ ] Step 6: エージェントシリアライズ（条件付き）
  - [ ] Step 7: 依存関係パッケージ化（条件付き）
  - [ ] Step 8: GCS認証（条件付き）
  - [ ] Step 9: Cloud SDKセットアップ（条件付き）
  - [ ] Step 10: GCSアップロード（条件付き）

### 3.2 deploy-frontend ジョブの依存関係更新

- [ ] `deploy-frontend` の `needs` に `deploy-agent-engine` を追加
- [ ] 構文の確認（YAML構文エラーがないか）

---

## Phase 4: ワークフロー構文検証

### 4.1 ローカル検証

- [ ] actionlint をインストール（ある場合）
- [ ] `actionlint .github/workflows/cd.yml` 実行（エラーがないか確認）

### 4.2 GitHub Actions構文チェック

- [ ] cd.yml の構文が正しいことを目視確認
- [ ] 条件分岐ロジック（if: steps.backend_changes.outputs.changed == 'true'）の確認
- [ ] 環境変数の参照が正しいことを確認

---

## Phase 5: 統合テスト準備

### 5.1 テストシナリオ設計

**シナリオ1: バックエンド変更あり**
- [ ] backend/app/services/adk/agents/router.py に小さな変更（コメント追加など）
- [ ] コミット・プッシュ
- [ ] cd.yml が実行されることを確認
- [ ] deploy-agent-engine ジョブが実行されることを確認
- [ ] GCSにアーティファクトがアップロードされることを確認

**シナリオ2: フロントエンドのみ変更**
- [ ] frontend/src/app/page.tsx に小さな変更
- [ ] コミット・プッシュ
- [ ] cd.yml が実行されることを確認
- [ ] deploy-agent-engine ジョブがスキップされることを確認

**シナリオ3: エラーハンドリング**
- [ ] 意図的にシリアライズエラーを発生させる（一時的にコードを壊す）
- [ ] CI/CDが適切に失敗することを確認
- [ ] エラーメッセージが明示的に表示されることを確認

---

## Phase 6: PR作成とレビュー

### 6.1 ローカル品質チェック

- [ ] Git status 確認: `git status`
- [ ] 変更ファイル確認: `git diff --name-only`
- [ ] コミット準備:
  - [ ] `.github/workflows/cd.yml` の変更をステージング
  - [ ] `.steering/20260211-ci-cd-agent-engine-deploy/` をコミット

### 6.2 コミット・プッシュ

- [ ] コミットメッセージ作成（Conventional Commits形式）:
  ```
  feat(ci): automate Agent Engine artifact deployment in cd.yml

  - Add deploy-agent-engine job to cd.yml
  - Detect backend changes with git diff
  - Serialize agent and package dependencies
  - Upload artifacts to GCS
  - Update deploy-frontend to depend on deploy-agent-engine

  Closes #101

  Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
  ```
- [ ] ブランチプッシュ: `git push -u origin feature/ci-cd-agent-engine-deploy`

### 6.3 PR作成

- [ ] GitHub でPR作成
- [ ] タイトル: `feat(ci): automate Agent Engine artifact deployment in cd.yml`
- [ ] 説明に以下を含める:
  - [ ] 概要（イシュー #101 の要約）
  - [ ] 変更内容（deploy-agent-engine ジョブ追加）
  - [ ] テストシナリオ（バックエンド変更あり/なし）
  - [ ] Closes #101

### 6.4 PR上でのテスト

- [ ] PRマージせず、feature ブランチで cd.yml をトリガー
- [ ] バックエンド変更を追加コミット
- [ ] CI/CDが成功することを確認
- [ ] GCSにアーティファクトがアップロードされることを確認:
  ```bash
  gcloud storage ls gs://homework-coach-assets-XXXXXXXX/agent-engine/
  ```

---

## Phase 7: ドキュメント更新

### 7.1 CLAUDE.md 更新

- [ ] `CLAUDE.md` の「既知の問題と対応中の課題」セクションを確認
- [ ] イシュー #101 の解決済みステータスに更新（必要に応じて）
- [ ] Development Context に Agent Engineアーティファクト自動デプロイが完了した旨を追記

### 7.2 implementation-status.md 更新

- [ ] `docs/implementation-status.md` の完了済み機能一覧に追記:
  ```markdown
  - Agent Engineアーティファクト自動デプロイ（cd.yml）
  ```
- [ ] ステアリングディレクトリ一覧に追記:
  ```markdown
  - `.steering/20260211-ci-cd-agent-engine-deploy/`: Agent Engineアーティファクト自動デプロイ
  ```

### 7.3 Agent Engine README 更新（必要に応じて）

- [ ] `infrastructure/terraform/modules/agent_engine/README.md` を確認
- [ ] 手動デプロイ手順の代わりに、CI/CDでの自動デプロイ方法を追記

---

## Phase 8: マージとクリーンアップ

### 8.1 PR承認・マージ

- [ ] PR レビュー（セルフレビュー）
- [ ] CI/CD が全て通っていることを確認
- [ ] PRをmainにマージ

### 8.2 main ブランチでの動作確認

- [ ] main ブランチで cd.yml が自動実行されることを確認
- [ ] deploy-agent-engine ジョブが正常に完了することを確認
- [ ] GCSアーティファクトが最新になっていることを確認

### 8.3 イシュークローズ

- [ ] GitHub Issue #101 がクローズされていることを確認
- [ ] ステータスが「Done」になっていることを確認（Project board）

### 8.4 ブランチクリーンアップ

- [ ] ローカルブランチ削除: `git branch -d feature/ci-cd-agent-engine-deploy`
- [ ] リモートブランチ削除: `git push origin --delete feature/ci-cd-agent-engine-deploy`

---

## Phase 9: 完了サマリー作成

- [ ] `.steering/20260211-ci-cd-agent-engine-deploy/COMPLETED.md` 作成
  - [ ] 実装内容の要約
  - [ ] 発生した問題と解決方法
  - [ ] 今後の改善点（Agent Engine自動再作成など）
  - [ ] 学んだこと（Lessons Learned）

---

## 備考

### 条件分岐の確認ポイント

全てのステップが `if: steps.backend_changes.outputs.changed == 'true'` で条件付き実行されることを確認。

### GCSアップロードの確認方法

```bash
# バケット名取得
BUCKET_NAME=$(gcloud storage buckets list --format="value(name)" --filter="name:homework-coach-assets")

# アップロードされたファイル確認
gcloud storage ls "gs://${BUCKET_NAME}/agent-engine/"

# ファイルのメタデータ確認（タイムスタンプなど）
gcloud storage ls -l "gs://${BUCKET_NAME}/agent-engine/"
```

### トラブルシューティング

**症状: git diff が空**
- 原因: `fetch-depth: 1` でshallow cloneしている
- 対策: `fetch-depth: 0` で全履歴取得

**症状: uv が見つからない**
- 原因: PATH設定漏れ
- 対策: `echo "$HOME/.local/bin" >> $GITHUB_PATH`

**症状: GCSバケットが見つからない**
- 原因: Terraformでバケットが作成されていない
- 対策: Terraform apply 実行確認
