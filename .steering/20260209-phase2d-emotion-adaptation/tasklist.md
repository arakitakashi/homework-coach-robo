# Task List - Phase 2d: 感情適応（バックエンド）

## Phase 1: update_emotion_tool の TDD 実装

- [ ] `test_emotion_analyzer.py` テスト作成（Red）
  - [ ] 正常系: 感情スコア更新 → session.state に記録
  - [ ] 正常系: support_level 計算（intensive/moderate/minimal）
  - [ ] 正常系: action_recommended 計算（continue/encourage/rest）
  - [ ] バリデーション: 範囲外スコア（<0, >1）のクランプ
  - [ ] バリデーション: 無効な primary_emotion → エラー
  - [ ] FunctionTool インスタンス確認
- [ ] `emotion_analyzer.py` 実装（Green）
- [ ] `tools/__init__.py` に update_emotion_tool エクスポート追加
- [ ] テスト全パス確認

## Phase 2: Router Agent の感情ツール統合（TDD）

- [ ] `test_router.py` テスト追加（Red）
  - [ ] Router Agent が update_emotion_tool を持つ
  - [ ] Router プロンプトに感情分析指示が含まれる
  - [ ] Router プロンプトに感情ベースルーティング基準が含まれる
- [ ] `router.py` 実装更新（Green）: tools=[update_emotion_tool]
- [ ] `prompts/router.py` プロンプト更新: 感情分析 + 感情ベースルーティング
- [ ] テスト全パス確認

## Phase 3: サブエージェントプロンプト更新

- [ ] `prompts/math_coach.py` に感情コンテキスト参照セクション追加
- [ ] `prompts/japanese_coach.py` に感情コンテキスト参照セクション追加
- [ ] `prompts/encouragement.py` に感情コンテキスト参照セクション追加
- [ ] 既存テスト全パス確認

## Phase 4: 品質チェック

- [ ] `uv run ruff check .` → エラーなし
- [ ] `uv run mypy .` → エラーなし
- [ ] `uv run pytest tests/ -v` → 全テスト通過
- [ ] カバレッジ 80% 以上維持
- [ ] 既存 504+ テスト全パス
