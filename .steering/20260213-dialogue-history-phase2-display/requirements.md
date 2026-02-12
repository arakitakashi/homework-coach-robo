# Requirements - Phase 2 対話履歴の拡張表示

## 背景・目的

Phase 2（ADK Function Tools、マルチエージェント、RAG、感情適応）の実装により、`DialogueTurn` 型に以下のメタデータが追加されました：

- `questionType`: 質問タイプ（理解確認/思考誘導/ヒント）
- `responseAnalysis`: 回答分析結果（理解度、正しい方向か、明確化が必要か）
- `emotion`: 検出された感情（frustrated, confident, confused, happy, tired, neutral）
- `activeAgent`: 対応したエージェント（router, math_coach, japanese_coach, encouragement, review）
- `toolExecutions`: ツール実行結果（calculate_tool, manage_hint_tool, record_progress_tool, check_curriculum_tool, analyze_image_tool）

現在の `DialogueHistory` コンポーネントは、対話の `text` のみを表示しており、これらの Phase 2 メタデータが活用されていません。

**目的**: 対話履歴に Phase 2 メタデータを視覚的に表示することで、以下を実現します：

1. **学習プロセスの可視化**: どのツールが使われたか、どのエージェントが対応したかを確認
2. **感情適応の透明性**: AIが子供の感情をどのように認識しているかを保護者・教育者が確認
3. **質問戦略の理解**: どのタイプの質問が使われているかを可視化
4. **理解度の追跡**: 回答分析結果から子供の理解度の変化を追跡

## 要求事項

### 機能要件

#### FR-1: 質問タイプの表示

- `DialogueTurn.questionType` が存在する場合、質問タイプに応じたアイコンを表示
- 質問タイプ:
  - `understanding_check`: 理解確認（例: チェックマークアイコン）
  - `thinking_guide`: 思考誘導（例: 電球アイコン）
  - `hint`: ヒント（例: ヒントアイコン）
- アイコンは対話吹き出しの上部に小さく表示

#### FR-2: 回答分析の表示

- `DialogueTurn.responseAnalysis` が存在する場合、理解度インジケータを表示
- 理解度 (`understandingLevel`): 0.0～1.0 の値をパーセンテージまたはバーで表示
- 正しい方向 (`isCorrectDirection`): true の場合は緑色、false の場合は黄色
- 明確化が必要 (`needsClarification`): true の場合は「?」アイコンを表示
- インジケータは対話吹き出しの下部に小さく表示

#### FR-3: 感情の表示

- `DialogueTurn.emotion` が存在する場合、感情に応じたアイコンを表示
- 感情タイプ:
  - `frustrated`: 困っている（赤色）
  - `confident`: 自信満々（緑色）
  - `confused`: わからない（青色）
  - `happy`: 元気いっぱい（黄色）
  - `tired`: 疲れている（グレー）
  - `neutral`: 落ち着いている（紫色）
- アイコンは対話吹き出しの上部に表示（質問タイプと並べて配置）
- 既存の `EmotionIndicator` コンポーネントのアイコン・カラーコーディングを再利用

#### FR-4: アクティブエージェントの表示

- `DialogueTurn.activeAgent` が存在する場合、エージェント名を表示
- エージェントタイプ:
  - `router`: ルーター
  - `math_coach`: 算数コーチ
  - `japanese_coach`: 国語コーチ
  - `encouragement`: 励まし
  - `review`: 振り返り
- エージェント名は対話吹き出しの上部に小さなバッジとして表示
- 既存の `AgentIndicator` コンポーネントのアイコン・ラベルを再利用

#### FR-5: ツール実行の表示

- `DialogueTurn.toolExecutions` が存在する場合、ツール使用バッジを表示
- ツール名:
  - `calculate_tool`: けいさん
  - `manage_hint_tool`: ヒント
  - `record_progress_tool`: きろく
  - `check_curriculum_tool`: きょうかしょ
  - `analyze_image_tool`: しゃしん
- ツール実行状態（pending, running, completed, error）に応じたステータスアイコンを表示
- ツールバッジは対話吹き出しの下部に表示
- 既存の `ToolExecutionDisplay` コンポーネントのデザインを再利用

#### FR-6: 既存UIとの統合

- Phase 2 メタデータの表示は、既存の対話吹き出しUIに自然に統合
- 対話の本文（`text`）は引き続き吹き出しの中央に表示
- メタデータは対話の邪魔にならないよう、小さく控えめに表示
- モバイル表示でも適切にレイアウト

### 非機能要件

#### NFR-1: アクセシビリティ

- すべてのアイコンに `aria-label` を付与
- 色だけに依存せず、アイコンやテキストで情報を伝達
- スクリーンリーダーで Phase 2 メタデータが読み上げられる

#### NFR-2: パフォーマンス

- Phase 2 メタデータの有無にかかわらず、対話履歴のレンダリングパフォーマンスが劣化しない
- 大量の対話（100+ ターン）でもスムーズにスクロール

#### NFR-3: テスト

- Phase 2 メタデータの各表示パターンに対するユニットテストを実装
- メタデータが存在しない場合（Phase 1 互換）のテストも実装
- テストカバレッジ 80% 以上を維持

### 制約条件

- 既存の `DialogueHistory` コンポーネントを拡張（新規コンポーネントは作成しない）
- 既存の Phase 2 コンポーネント（`ToolExecutionDisplay`, `AgentIndicator`, `EmotionIndicator`）のデザインパターン・アイコン・カラーコーディングを再利用
- Tailwind CSS でスタイリング
- Framer Motion でアニメーション（オプション）

## 対象範囲

### In Scope

- `DialogueHistory` コンポーネントの拡張
- `DialogueBubble` サブコンポーネントの拡張
- Phase 2 メタデータ表示用の新しいサブコンポーネント（必要に応じて）
- ユニットテスト（Vitest + Testing Library）

### Out of Scope

- Phase 2 メタデータの取得ロジック（既に実装済み）
- WebSocket イベントハンドラの変更（既に実装済み）
- 状態管理（Jotai atoms は既に実装済み）
- `DialogueTurn` 型の変更（既に実装済み）
- 対話履歴のフィルタリング・検索機能（将来の拡張）

## 成功基準

1. **視覚的な表示**: 各 Phase 2 メタデータが、対応するアイコン・バッジ・インジケータで視覚的に表示される
2. **デザイン統合**: 既存の Phase 2 コンポーネントと一貫したデザイン
3. **後方互換性**: Phase 2 メタデータが存在しない場合でも、既存の対話表示が正常に動作
4. **アクセシビリティ**: すべてのメタデータがスクリーンリーダーで読み上げられる
5. **テスト**: 全ての表示パターンに対するテストが実装され、カバレッジ 80% 以上
6. **パフォーマンス**: 100+ ターンの対話履歴でもスムーズにレンダリング
