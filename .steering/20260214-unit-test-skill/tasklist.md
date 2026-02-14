# Task List - Unit Test Skill

## Phase 1: 環境セットアップ

- [x] ステアリングディレクトリの作成
- [x] requirements.md の作成
- [x] design.md の作成
- [x] tasklist.md の作成

## Phase 2: スキルファイル実装

- [x] `.claude/skills/unit-test.md` の作成
  - [x] スキル説明（Description）
  - [x] 使用タイミング（When to Use）
  - [x] 入力パラメータ（Parameters）
  - [x] 出力フォーマット（Output Format）
  - [x] 使用例（Examples）
  - [x] サブエージェントへの指示（Instructions）

## Phase 3: 手動テスト

### Frontend テスト

- [x] 全テスト実行
  - [x] Task ツールで frontend テスト実行
  - [x] 結果が適切にサマリー化されているか確認

- [x] 失敗ケース確認
  - [x] Frontend で 426 tests failed (document is not defined)
  - [x] 失敗メッセージが適切に抽出されることを確認

### Backend テスト

- [x] 全テスト実行
  - [x] Task ツールで backend テスト実行
  - [x] 結果が適切にサマリー化されているか確認（611 tests passed）

- [x] 特定ファイル実行
  - [x] test_firestore_session_service.py を実行
  - [x] サマリーのみが返却されるか確認（19 tests passed）

## Phase 4: ドキュメント更新

- [x] `CLAUDE.md` の更新
  - [x] Available Skills セクションに `/unit-test` を追加
  - [x] 既存スキルとの棲み分けを明記

- [x] `docs/implementation-status.md` の更新
  - [x] 完了済み機能一覧に追加
  - [x] ステアリングディレクトリ一覧に `.steering/20260214-unit-test-skill` を追加

## Phase 5: 品質チェック

- [x] スキルファイルの構文確認
  - [x] Markdownフォーマットが正しいか
  - [x] 使用例が明確か（4つのシナリオで明示）

- [x] セルフレビュー
  - [x] 要求仕様との整合性確認（すべての成功基準を満たす）
  - [x] 設計との整合性確認（サブエージェントタイプ、コマンド、出力フォーマット）

## Phase 6: コミット・PR作成

- [x] 変更内容のコミット
  - [x] スキルファイル
  - [x] ドキュメント更新（サブエージェントが実行）
  - [x] ステアリングディレクトリ

- [x] PR作成
  - [x] タイトル: `feat: /unit-test スキル追加（TDDサイクル中のテスト実行）`
  - [x] PR URL: https://github.com/arakitakashi/homework-coach-robo/pull/148

## Phase 7: 完了

- [x] `COMPLETED.md` の作成
  - [x] 実装内容の要約
  - [x] 学んだこと
  - [x] 今後の改善点
