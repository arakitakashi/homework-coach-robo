# Requirements - Phase 2a: ADK Function Tools

## 背景・目的

MVP（Phase 1）ではシステムプロンプトのみの単一エージェント（`tools=[]`）で対話を行っていた。
Phase 2aでは、ADK FunctionToolを導入し、エージェントがツールを使って正確な処理を行えるようにする。

**対応Issue:**
- #37: `calculate_tool` - 四則演算の検証
- #38: `manage_hint_tool` - 3段階ヒント状態管理
- #39: `record_progress_tool` - 学習進捗記録・ポイント付与
- #40: `check_curriculum_tool` - カリキュラム・教科書参照
- #41: `analyze_image_tool` - 宿題写真の読み取り（Vision API）

## 要求事項

### 機能要件

1. **calculate_tool**: LLMの幻覚リスクを排除するため、四則演算を正確に検証
2. **manage_hint_tool**: 3段階ヒントシステムの厳密な状態管理（LLMが直接変更不可）
3. **record_progress_tool**: 学習進捗の記録とポイント付与（3pt/2pt/1pt）
4. **check_curriculum_tool**: 学年・教科に応じたカリキュラム情報の提供
5. **analyze_image_tool**: 宿題写真からの問題抽出（Gemini Vision）

### 非機能要件

- すべてのツールはADK `FunctionTool`インターフェース準拠
- mypy strict準拠（型ヒント必須）
- テストカバレッジ80%以上
- 日本語コンテンツ対応

### 制約条件

- 既存のRunner/API層は変更不要（ツールはエージェント内で透過的に実行される）
- `agent.py`のみ変更（ツールリストの追加、システムプロンプト更新）

## 対象範囲

### In Scope

- 5つのADK FunctionToolの実装
- ユニットテスト
- `agent.py`へのツール統合
- `tools/__init__.py`でのエクスポート

### Out of Scope

- マルチエージェント（Phase 2b）
- RAG統合（Phase 2c）
- 感情適応（Phase 2d）
- Firestoreへの実際の永続化（モック使用、永続化層は既存サービスで対応）
- API層の変更

## 成功基準

- 5つのツールがすべて実装済み
- 全テスト通過、カバレッジ80%以上
- ruff check / mypy エラーなし
- `create_socratic_agent()`がツールを含むエージェントを返す
