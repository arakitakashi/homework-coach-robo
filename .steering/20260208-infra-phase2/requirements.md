# Requirements - Infrastructure Phase 2 Update

## 背景・目的

Phase 2開発開始に伴い、既存のTerraformインフラをPhase 2（ツール導入、マルチエージェント、RAG、感情適応）に対応させる。現在のインフラはPhase 1/MVPの構成。Phase 2では新しいGCPサービス、IAMロール、BigQueryテーブル、Firestoreインデックス、環境変数が必要。

## 要求事項

### 機能要件

1. **Discovery Engine API有効化** - RAG用のVertex AI Discovery Engine
2. **IAMロール追加** - discoveryengine.editor, storage.objectAdmin（条件付き）
3. **Secret Manager拡張** - Gemini APIキーシークレット（条件付き）
4. **Firestoreインデックス追加** - Phase 2a/2b/2d用の5インデックス
5. **BigQueryテーブル追加** - agent_metrics, emotion_analysis, rag_metrics
6. **Cloud Run環境変数** - バックエンドへの動的環境変数注入
7. **環境レベル配線** - Feature flagで段階的有効化

### 非機能要件

- 後方互換性の維持（既存リソースに影響なし）
- Feature flagがfalseの場合、差分なし
- 既存モジュール拡張（新モジュール作成不要）

### 制約条件

- Terraform >= 1.5.0
- Google Provider ~> 5.0
- 既存のリソース名・構造を変更しない

## 対象範囲

### In Scope

- bootstrap API追加
- 環境レベルAPI追加
- IAMモジュール更新
- Secret Managerモジュール更新
- Firestoreインデックス追加
- BigQueryテーブル追加
- Cloud Runモジュール更新
- 環境レベル配線

### Out of Scope

- 実際のアプリケーションコード変更
- Vertex AI Discovery Engine corpusの作成（アプリ層で実施）
- 新モジュールの作成
- staging/production環境の設定

## 成功基準

- `terraform validate` が成功する
- Feature flags全てfalseで `terraform plan` に差分なし
- 各Feature flagをtrueにした際、適切なリソースのみ追加される
