# Requirements - Phase 2b: マルチエージェント構成

## 背景・目的

Phase 2a で ADK Function Tools（5ツール）を導入済み。現在は単一の `socratic_dialogue_agent` が全教科・全状況を担当しているが、教科ごとの最適化や感情サポートの分離ができていない。

Phase 2b では ADK のマルチエージェント機能（`sub_agents` + AutoFlow）を活用し、Router Agent が子供の入力を分析して最適な専門エージェントに委譲するアーキテクチャを実装する。

## 要求事項

### 機能要件

#### Router Agent (#42)
- 子供の入力を分析し、教科・状況に応じて適切なサブエージェントに振り分ける
- 判断基準:
  - 算数の問題 → Math Coach に委譲
  - 国語の問題（漢字、読解、作文）→ Japanese Coach に委譲
  - 「疲れた」「わからない」「やめたい」等 → Encouragement Agent に委譲
  - 「今日やったこと」「振り返り」→ Review Agent に委譲
  - 判断が難しい場合は子供に確認する

#### Math Coach Agent (#43)
- 算数に特化したソクラテス式対話
- `calculate_tool` との連携（計算の検証は必ずツール経由）
- 学年別の問題パターン対応（繰り上がり、九九、文章題等）
- `manage_hint_tool`, `check_curriculum_tool`, `record_progress_tool` を使用

#### Japanese Coach Agent (#44)
- 国語に特化したソクラテス式対話（読解、漢字、作文）
- 学年別の語彙レベル対応
- `manage_hint_tool`, `check_curriculum_tool`, `record_progress_tool` を使用

#### Encouragement Agent (#45)
- フラストレーション検知時の介入
- 疲労検知時の休憩提案
- 成功時の称賛メッセージ
- 成長マインドセットの促進
- `record_progress_tool` を使用（今日の頑張りを振り返る）

#### Review Agent (#46)
- セッション振り返りの生成
- 学習進捗サマリー
- 保護者向けレポート生成
- `record_progress_tool` を使用

### 非機能要件

- 既存の SSE / WebSocket エンドポイントとの後方互換性を維持
- テストカバレッジ 80% 以上
- 各エージェントのプロンプトは独立ファイルに分離
- ADK AutoFlow（LLM駆動委譲）を使用

### 制約条件

- ADK `google-adk>=1.23.0`（既にインストール済み）
- `Agent`（= `LlmAgent`）+ `sub_agents` パターンを使用
- `kanji_lookup_tool`, `reading_comprehension_tool`, `search_memory_tool` は Phase 2b スコープ外（Phase 2c 以降）
- 感情分析（`frustration_level`）は Phase 2d スコープ外（Encouragement Agent はテキストベースのトリガーのみ）

## 対象範囲

### In Scope

- Router Agent の作成
- Math Coach Agent の作成
- Japanese Coach Agent の作成
- Encouragement Agent の作成
- Review Agent の作成
- 各エージェント用プロンプトの作成
- `runner_service.py` のマルチエージェント対応
- 各エージェントのユニットテスト
- 統合テスト

### Out of Scope

- 新ツールの追加（Phase 2a ツールのみ使用）
- Vertex AI RAG 統合（Phase 2c）
- 音声感情分析（Phase 2d）
- Agent Engine デプロイ（Phase 3）
- フロントエンド変更（APIは後方互換）

## 成功基準

- 全5エージェントが正しく作成・委譲される
- Router が教科・状況に応じて適切にルーティングする
- 既存の SSE / WebSocket エンドポイントが変更なしで動作する
- テストカバレッジ 80% 以上
- `uv run ruff check .` / `uv run mypy .` / `uv run pytest` 全パス
