# Requirements - Phase 2c: RAG Search Tool 統合

## 背景・目的

Phase 2c の実装として、Vertex AI RAG Engine を使用したセマンティック記憶検索ツール（`search_memory_tool`）を統合する。これにより、現在のキーワードベースの記憶検索を、セマンティック検索に置き換え、子供の過去の学習パターンを文脈的に検索できるようにする。

## 要求事項

### 機能要件

1. **search_memory_tool の実装**
   - Vertex AI RAG API との統合
   - ADK FunctionTool インターフェース準拠
   - セマンティック検索によるメモリ検索

2. **既存キーワード検索の置換**
   - `FirestoreMemoryService.search_memory()` を RAG ベースに置き換え
   - 後方互換性を維持（インターフェースは変更しない）

3. **記憶の種類対応**
   - 対話履歴（過去の対話から関連する指導パターンを検索）
   - 苦手分野（「繰り上がりで3回つまずいた」等のパターン）
   - 成功体験（「前回は自力で解けた」等のポジティブ記録）
   - カリキュラム（学習指導要領、教科書の内容）

### 非機能要件

1. **パフォーマンス**
   - 検索レスポンスタイム: 2秒以内
   - 大量データでもスケーラブル

2. **精度**
   - セマンティック類似度による高精度な検索
   - 日本語対応

3. **テスト駆動開発**
   - カバレッジ80%以上
   - ユニットテスト、統合テストを含む

### 制約条件

1. **Vertex AI RAG API の制約**
   - データストアの作成・管理は手動（初回のみ）
   - インデクシングの遅延を考慮

2. **ADK インターフェース準拠**
   - `FunctionTool` として実装
   - `ToolContext` を通じてセッション状態にアクセス

## 対象範囲

### In Scope

- `search_memory_tool` の実装（ADK FunctionTool）
- Vertex AI RAG との統合コード
- 既存キーワード検索からの移行ロジック
- ユニットテスト・統合テストの作成
- Review Agent への `search_memory_tool` 追加

### Out of Scope

- Vertex AI RAG Corpus の作成（手動で事前に実施）
- 記憶の自動インデクシング（Phase 2c 後半で実装予定）
- カリキュラムデータの RAG 化（Phase 2c 後半で実装予定）

## 成功基準

1. `search_memory_tool` が ADK FunctionTool として正しく動作する
2. Vertex AI RAG API との統合が正常に機能する
3. セマンティック検索がキーワード検索よりも高精度である
4. すべてのテストが通る（カバレッジ80%以上）
5. 既存のエージェントが新しいツールを使用できる
