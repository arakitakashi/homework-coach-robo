# Task List - Phase 2d: 感情適応（バックエンド）

## Phase 1: update_emotion_tool の TDD 実装

- [x] `test_emotion_analyzer.py` テスト作成（Red）
  - [x] 正常系: 感情スコア更新 → session.state に記録
  - [x] 正常系: support_level 計算（intensive/moderate/minimal）
  - [x] 正常系: action_recommended 計算（continue/encourage/rest）
  - [x] バリデーション: 範囲外スコア（<0, >1）のクランプ
  - [x] バリデーション: 無効な primary_emotion → エラー
  - [x] FunctionTool インスタンス確認
- [x] `emotion_analyzer.py` 実装（Green）
- [x] `tools/__init__.py` に update_emotion_tool エクスポート追加
- [x] テスト全パス確認（83 tool tests passed）

## Phase 2: Router Agent の感情ツール統合（TDD）

- [x] `test_router.py` テスト追加（Red）
  - [x] Router Agent が update_emotion_tool を持つ
  - [x] Router プロンプトに感情分析指示が含まれる
  - [x] Router プロンプトに感情ベースルーティング基準が含まれる
- [x] `router.py` 実装更新（Green）: tools=[update_emotion_tool]
- [x] `prompts/router.py` プロンプト更新: 感情分析 + 感情ベースルーティング
- [x] テスト全パス確認（19 router tests passed）

## Phase 3: サブエージェントプロンプト更新

- [x] `prompts/math_coach.py` に感情コンテキスト参照セクション追加
- [x] `prompts/japanese_coach.py` に感情コンテキスト参照セクション追加
- [x] `prompts/encouragement.py` に感情コンテキスト参照セクション追加
- [x] 既存テスト全パス確認（76 agent tests passed）

## Phase 4: 品質チェック

- [x] `uv run ruff check .` → エラーなし
- [x] `uv run mypy .` → エラーなし（変更ファイル）
- [x] `uv run pytest tests/ -v` → 526 テスト全パス
- [x] カバレッジ 90%（80% 以上維持）
- [x] 既存 504 + 新規 22 = 526 テスト全パス
