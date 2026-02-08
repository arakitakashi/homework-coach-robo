# Task List - Phase 2c: RAG Corpus作成・インデクシング

## Phase 1: 環境セットアップ

- [ ] 依存パッケージのインストール
  - [ ] `google-cloud-aiplatform>=1.60.0` を pyproject.toml に追加
  - [ ] `uv sync` で依存関係を更新
- [ ] 環境変数の設定
  - [ ] `GCP_PROJECT_ID` 確認
  - [ ] `VERTEX_AI_LOCATION` 確認（us-central1推奨）
- [ ] 必要なディレクトリの作成
  - [ ] `backend/app/services/adk/rag/` 作成
  - [ ] `backend/tests/unit/services/adk/rag/` 作成
  - [ ] `backend/scripts/` 確認

## Phase 2: テスト実装（TDD）

### 2.1 RagDocument モデルのテスト

- [ ] `tests/unit/services/adk/rag/test_models.py` 作成
  - [ ] RagDocument生成のテスト
  - [ ] メタデータバリデーションのテスト
  - [ ] content sanitizationのテスト（個人情報マスキング）

### 2.2 RagCorpusService のテスト

- [ ] `tests/unit/services/adk/rag/test_corpus_service.py` 作成
  - [ ] create_corpus のテスト（モック使用）
  - [ ] index_document のテスト
  - [ ] index_documents_batch のテスト
  - [ ] search のテスト
  - [ ] エラーハンドリングのテスト（リトライロジック）

### 2.3 IndexingService のテスト

- [ ] `tests/unit/services/adk/rag/test_indexing_service.py` 作成
  - [ ] Firestoreからのデータ取得テスト
  - [ ] RagDocumentへの変換テスト
  - [ ] バッチインデクシングのテスト
  - [ ] インデクシング済みフラグ更新のテスト

### 2.4 search_memory_tool のテスト

- [ ] `tests/unit/services/adk/tools/test_search_memory.py` 作成
  - [ ] VertexAiSearchTool設定のテスト
  - [ ] フォールバックロジックのテスト（RAG → Firestore）
  - [ ] エージェント統合のテスト

## Phase 3: 実装

### 3.1 モデル定義

- [ ] `backend/app/services/adk/rag/models.py` 実装
  - [ ] 仮実装: RagDocument dataclass（必須フィールドのみ）
  - [ ] 本実装: メタデータ追加、バリデーション
  - [ ] リファクタリング: type hints、docstring

- [ ] `backend/app/services/adk/rag/models.py` に sanitize_content 追加
  - [ ] 仮実装: 子供の名前マスキング（正規表現）
  - [ ] 本実装: 保護者名、その他PII対応
  - [ ] リファクタリング: ヘルパー関数分離

### 3.2 RagCorpusService 実装

- [ ] `backend/app/services/adk/rag/corpus_service.py` 実装
  - [ ] 仮実装: create_corpus（ハードコード）
  - [ ] 本実装: Vertex AI RAG API統合
  - [ ] リファクタリング: エラーハンドリング、ロギング

- [ ] index_document 実装
  - [ ] 仮実装: モックレスポンス
  - [ ] 本実装: RAG API呼び出し
  - [ ] リファクタリング: リトライロジック追加

- [ ] index_documents_batch 実装
  - [ ] 仮実装: ループ処理
  - [ ] 本実装: バッチAPI呼び出し
  - [ ] リファクタリング: エラーハンドリング

- [ ] search 実装
  - [ ] 仮実装: 空リスト返却
  - [ ] 本実装: RAG検索API呼び出し
  - [ ] リファクタリング: フィルタリング、スコアリング

### 3.3 IndexingService 実装

- [ ] `backend/app/services/adk/rag/indexing_service.py` 実装
  - [ ] 仮実装: サンプルデータ生成
  - [ ] 本実装: Firestoreクエリ、RagDocument変換
  - [ ] リファクタリング: バッチ処理最適化

### 3.4 search_memory_tool 実装

- [ ] `backend/app/services/adk/tools/search_memory.py` 実装
  - [ ] 仮実装: VertexAiSearchTool定義（description）
  - [ ] 本実装: data_store_id設定、フォールバック
  - [ ] リファクタリング: エラーハンドリング強化

- [ ] Review Agentへの統合
  - [ ] `backend/app/services/adk/agents/review.py` に search_memory_tool 追加
  - [ ] プロンプト更新（ツール使用ガイダンス）
  - [ ] テストケース追加

### 3.5 初期化スクリプト実装

- [ ] `backend/scripts/initialize_rag_corpus.py` 実装
  - [ ] 仮実装: print文のみ
  - [ ] 本実装: Corpus作成、サンプルデータインデクシング
  - [ ] リファクタリング: CLI引数パース、エラーハンドリング

## Phase 4: 統合テスト

- [ ] `tests/integration/test_rag_search_flow.py` 作成
  - [ ] Corpus作成 → インデクシング → 検索のE2Eフロー
  - [ ] Review Agentとの統合テスト
  - [ ] フォールバックシナリオのテスト（RAG障害時）
  - [ ] 日本語クエリの精度検証

- [ ] 検索精度の評価
  - [ ] サンプルクエリ10件作成
  - [ ] 各クエリの検索結果を評価（関連度スコア）
  - [ ] 精度70%以上を確認

## Phase 5: 品質チェック

- [ ] コードレビュー（セルフレビュー）
  - [ ] 命名規則の確認（snake_case、PascalCase）
  - [ ] コード重複の確認
  - [ ] エッジケースの処理確認（空クエリ、0件結果）

- [ ] セキュリティレビュー（`/security-review` スキル使用）
  - [ ] 個人情報マスキングの確認
  - [ ] IAM設定の確認
  - [ ] エラーメッセージに機密情報が含まれていないか確認

- [ ] テストカバレッジ確認（80%以上）
  - [ ] `uv run pytest tests/unit/services/adk/rag/ --cov=app/services/adk/rag --cov-report=term-missing`
  - [ ] カバレッジレポート確認

- [ ] リンター・フォーマッター実行
  - [ ] `uv run ruff check app tests`
  - [ ] `uv run ruff format app tests`

- [ ] 型チェック実行
  - [ ] `uv run mypy app/services/adk/rag/`
  - [ ] 型エラーの修正

- [ ] ドキュメント更新
  - [ ] `docs/agent-architecture.md` にPhase 2c実装状況を記載
  - [ ] `docs/implementation-status.md` 更新
  - [ ] `CLAUDE.md` 更新（Phase 2c完了マーク）

## Phase 6: PR作成前チェック

### Backend

- [ ] `uv run ruff check app tests` → エラーなし
- [ ] `uv run mypy app/` → エラーなし
- [ ] `uv run pytest tests/` → 全テスト通過
- [ ] カバレッジ80%以上確認

## Phase 7: デプロイ準備（該当する場合）

- [ ] Terraform設定の追加
  - [ ] `infrastructure/terraform/modules/rag/main.tf` 作成
  - [ ] IAMロール設定
  - [ ] Vertex AI API有効化

- [ ] 初期化手順書の作成
  - [ ] `docs/rag-setup.md` 作成
  - [ ] Corpus作成手順
  - [ ] サンプルデータインデクシング手順

- [ ] 環境別設定の確認
  - [ ] 開発環境: サンプルデータのみ
  - [ ] 本番環境: 実データ移行は Phase 3で実施

---

## 進捗トラッキング

| Phase | ステータス | 完了日 |
|-------|----------|--------|
| Phase 1 | 🔲 未着手 | - |
| Phase 2 | 🔲 未着手 | - |
| Phase 3 | 🔲 未着手 | - |
| Phase 4 | 🔲 未着手 | - |
| Phase 5 | 🔲 未着手 | - |
| Phase 6 | 🔲 未着手 | - |
| Phase 7 | 🔲 未着手 | - |

---

## 作業再開時の確認事項

- 最後のコミット: `___`
- 次のタスク: `___`
- 前提条件・ブロッカー: `___`
- 参照すべきファイル:
  - `docs/agent-architecture.md`
  - `backend/app/services/adk/memory/firestore_memory_service.py`（既存実装参考）
  - ADK公式ドキュメント: https://google.github.io/adk-docs/tools/

---

## 備考

### 注意事項

1. **Vertex AI RAG APIはまだ完全なPython SDKがない可能性**
   - REST APIを直接呼び出す実装も検討
   - ADK VertexAiSearchToolのドキュメント確認必須

2. **日本語埋め込みモデルの選定**
   - `text-multilingual-embedding-002` を優先
   - 精度が不十分な場合は `textembedding-gecko-multilingual` も検討

3. **Firestoreフォールバックは当面維持**
   - Phase 2c完了後も並存
   - 完全移行はPhase 3以降で検討

4. **コスト最適化**
   - 検索クエリ数を最小化（キャッシュ活用）
   - バッチインデクシングで効率化
