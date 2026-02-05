# Requirements - ADK Runner統合

## 背景・目的

ADK（Agent Development Kit）のRunnerを使用して、SessionServiceとMemoryServiceを統合したエージェント実行環境を構築する。

現在の実装状況:
- `FirestoreSessionService`: ADK BaseSessionService準拠、Firestore永続化
- `FirestoreMemoryService`: ADK BaseMemoryService準拠、Firestore永続化
- `SocraticDialogueManager`: 対話ロジック、プロンプト生成、回答分析

これらを統合し、ADK Runnerを使ったエージェント実行フローを実現する。

## 要求事項

### 機能要件

1. **ADK Agent定義**
   - ソクラテス式対話エンジンをADK Agentとして定義
   - システムプロンプトでソクラテス式対話の原則を設定
   - 3段階ヒントシステムを組み込み

2. **Runner統合**
   - SessionService（Firestore）を使用したセッション永続化
   - MemoryService（Firestore）を使用した記憶管理
   - 非同期実行（`run_async`）対応

3. **学習プロファイル連携**
   - `ChildLearningProfile`とMemoryServiceの連携
   - 学習履歴の永続化と検索

### 非機能要件

1. **テストカバレッジ**: 80%以上
2. **型安全性**: mypy strict準拠
3. **パフォーマンス**: レイテンシ目標2秒以内（LLM呼び出し除く）

### 制約条件

1. ADK BaseSessionService/BaseMemoryServiceインターフェース準拠
2. 既存のSocraticDialogueManagerのロジックを再利用
3. TDD原則に従った開発

## 対象範囲

### In Scope

- ADK Agent定義（`SocraticDialogueAgent`）
- Agent実行サービス（`AgentRunner`）
- SessionService/MemoryServiceの統合
- ユニットテスト

### Out of Scope

- Gemini Live API統合（別フェーズ）
- 音声入出力処理
- Redisキャッシュ（後続フェーズ）
- 統合テスト・E2Eテスト

## 成功基準

- [ ] ADK Agentが定義され、Runnerで実行可能
- [ ] セッションがFirestoreに永続化される
- [ ] 記憶がFirestoreに保存・検索可能
- [ ] テストカバレッジ80%以上
- [ ] mypy/ruff エラーなし
