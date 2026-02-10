# Requirements - Agent Engine Terraform インフラ整備

## 背景・目的

Phase 3 Agent Engine デプロイ基盤の実装に続き、Terraform によるインフラ管理を整備する。バックエンド側で Agent Engine の内蔵セッション管理を利用する準備として、インフラ側の構成を完成させる。

## 要求事項

### 機能要件

1. **Terraform モジュールの作成**
   - Agent Engine リソース（google_vertex_ai_reasoning_engine）の定義
   - GCS アーティファクト URI の管理（pickle, requirements, dependencies）
   - 出力値の定義（resource_name, engine_id）

2. **環境統合**
   - dev 環境への Agent Engine モジュール追加
   - enable_agent_engine フラグによる有効化制御
   - Cloud Run 環境変数への自動設定

3. **Provider バージョン対応**
   - Google Provider >= 7.13.0 へのアップグレード
   - google_vertex_ai_reasoning_engine リソースのサポート確保

4. **ドキュメント整備**
   - モジュール README の作成
   - デプロイ手順の文書化
   - トラブルシューティングガイドの提供

### 非機能要件

1. **保守性**
   - モジュール化された再利用可能な構成
   - 明確な変数定義とドキュメント

2. **運用性**
   - デプロイ・更新・削除の手順明確化
   - エラー時の対処方法の提供

3. **互換性**
   - 既存の Firestore ベースのセッション管理との共存
   - バックエンド実装との疎結合

### 制約条件

- Agent Engine は us-central1 リージョンでのデプロイ
- GCS バケットは既存の assets バケットを利用
- バックエンドコードの変更は別 Issue（#98）で対応

## 対象範囲

### In Scope

- Terraform モジュール（agent_engine/）の作成
- dev 環境設定への統合
- Provider バージョンアップグレード
- ドキュメント作成（README, 手順書）
- implementation-status.md の更新

### Out of Scope

- バックエンドの Agent Engine 対応（Issue #98 で対応）
- セッション管理の実装変更
- フロントエンドの変更
- 本番環境へのデプロイ

## 成功基準

1. ✅ Terraform モジュールが正しく定義されている
2. ✅ terraform apply で Agent Engine がデプロイできる
3. ✅ Cloud Run の環境変数に AGENT_ENGINE_RESOURCE_NAME/ID が設定される
4. ✅ README と手順書が完備されている
5. ✅ Issue #98 がバックエンド実装の指針として利用可能
