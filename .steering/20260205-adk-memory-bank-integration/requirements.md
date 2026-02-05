# Requirements - ADK MemoryBank統合

## 背景・目的

### 背景

宿題コーチロボットでは、子供の学習履歴や傾向を記録し、パーソナライズされた対話を提供する必要がある。
現在、以下のコンポーネントが実装済み：

1. **FirestoreSessionService**: ADK SessionService準拠のセッション永続化
2. **ChildLearningProfile**: 学習プロファイルのデータモデル（thinking, subjects, session summaries）
3. **LearningMemory**: ADK MemoryBank用の記憶モデル（learning_insight, thinking_pattern, effective_approach）

しかし、ADK `MemoryService` との統合がまだ実装されておらず、以下の課題がある：

- セッション間で学習記憶を引き継げない
- エージェントが過去の学習パターンを参照できない
- 長期的な学習傾向の分析ができない

### 目的

ADK `BaseMemoryService` に準拠した `FirestoreMemoryService` を実装し、以下を実現する：

1. セッションイベントの永続的な記憶保存
2. 学習プロファイルとの連携（記憶から洞察を抽出）
3. セマンティック検索による記憶の検索

---

## 要求事項

### 機能要件

#### FR-1: セッション記憶の追加

- `add_session_to_memory(session)` でセッションを記憶に追加
- セッションのイベントから重要な内容を抽出して保存
- メタデータ（タイムスタンプ、著者、カスタムメタデータ）を保持

#### FR-2: 記憶の検索

- `search_memory(app_name, user_id, query)` で記憶を検索
- キーワードベースの検索をサポート
- 将来的にセマンティック検索（Vertex AI RAG）に拡張可能な設計

#### FR-3: 学習プロファイルとの連携

- セッション追加時に学習傾向を更新
- 記憶から学習洞察（LearningMemory）を抽出
- ChildLearningProfileの更新トリガー

#### FR-4: Firestoreコレクション設計

- `/memories/{app_name}/users/{user_id}/entries/{id}` - 記憶エントリ
- 効率的なクエリのためのインデックス設計

### 非機能要件

#### NFR-1: パフォーマンス

- 記憶追加: 500ms以内
- 記憶検索: 1秒以内（100件まで）

#### NFR-2: スケーラビリティ

- ユーザーあたり最大10,000件の記憶エントリをサポート
- 古い記憶の自動アーカイブ機能（将来）

#### NFR-3: テストカバレッジ

- 80%以上のカバレッジを維持

---

## 対象範囲

### In Scope

1. `FirestoreMemoryService` の実装（ADK BaseMemoryService準拠）
2. Firestoreコレクション設計と実装
3. 単体テスト
4. 既存の `LearningMemory` / `ChildLearningProfile` との連携

### Out of Scope

1. セマンティック検索（Vertex AI RAG統合）- 将来のフェーズ
2. 記憶の自動要約・圧縮 - 将来のフェーズ
3. Redis キャッシュ層 - 別タスク

---

## 成功基準

1. ADK `BaseMemoryService` の全メソッドが実装されている
2. 単体テストが全てパスし、カバレッジ80%以上
3. lint/mypy チェックが全てパス
4. 既存のFirestoreSessionServiceと整合性がある
