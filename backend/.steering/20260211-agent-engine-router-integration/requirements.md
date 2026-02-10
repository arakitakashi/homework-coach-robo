# Requirements - Agent Engine統合による内部完結型Router Agent実装

## 背景・目的

### 現在の問題

現在のRouter AgentはFirestoreベースのセッション管理に依存しており、以下の問題があります：

1. **外部依存の複雑性**
   ```python
   class AgentRunnerService:
       def __init__(self):
           self._runner = Runner(
               agent=self._agent,
               session_service=FirestoreSessionService,  # Firestore依存
               memory_service=FirestoreMemoryService,    # Firestore依存
           )
   ```

2. **Agent Engineデプロイ時の問題**
   - 外部サービス（Firestore）への依存がpickleファイルに含められない
   - Agent Engineの実行環境で外部DB接続が複雑化
   - セッション管理の二重実装（Firestore + Agent Engine）

3. **VoiceStreamingServiceの問題**
   - Phase 1の単一エージェント（`create_socratic_agent()`）を使用
   - Phase 2のRouter Agentが統合されていない
   - ツール実行・エージェント遷移のイベント監視が困難

### 目的

Agent Engineの内蔵セッション管理機能を利用して、完全に自己完結型のRouter Agentを実装します。

**主な改善点**:
1. Firestore依存の完全排除（セッション管理・メモリ管理）
2. Agent Engine標準機能の活用（セッション管理、Memory Bank）
3. Phase 2 Router Agentの統合（Math Coach、Japanese Coach等）
4. pickleファイルの簡素化とデプロイの安定化

## 要求事項

### 機能要件

#### FR1: Agent Engineラッパーによるセッション管理

`backend/app/services/adk/agent_engine/agent_wrapper.py`を実装：

```python
class AgentEngineWrapper:
    """Agent Engine内蔵セッション管理を使用するラッパー

    Firestoreに依存せず、Agent Engineが提供するセッション管理APIを利用。
    """

    def __init__(self, agent: Agent):
        self._agent = agent
        # Runnerは使わない - Agent Engineがセッション管理を提供

    async def query(
        self,
        message: str,
        session_id: str,
        user_id: str,
    ) -> AsyncIterator[Event]:
        """Agent Engineのセッション管理を使ったクエリ処理

        Args:
            message: ユーザーメッセージ
            session_id: セッションID（Agent Engineが管理）
            user_id: ユーザーID

        Yields:
            Event: ADK Event（音声、トランスクリプション、ツール実行等）
        """
        pass
```

**要件**:
- Agent Engineのセッション管理API（create_session, get_session, list_sessions, delete_session）を使用
- 非同期イテレータでADK Eventをyield
- セッション作成・取得のエラーハンドリング

#### FR2: VoiceStreamingServiceのリファクタリング

`backend/app/services/voice/streaming_service.py`を更新：

**現在**:
```python
self._agent = create_socratic_agent(model=LIVE_MODEL)  # Phase 1単一エージェント
self._runner = Runner(...)
```

**変更後**:
```python
self._agent = create_router_agent(model=LIVE_MODEL)  # Phase 2 Router Agent
self._agent_wrapper = AgentEngineWrapper(self._agent)
# Runnerなし、Agent Engineがセッション管理
```

**要件**:
- Phase 2 Router Agentの統合
- Agent Engineラッパー経由でのイベント受信
- 既存の`send_audio()`, `send_text()`, `receive_events()`インターフェースの互換性維持

#### FR3: シリアライゼーションスクリプトの更新

`backend/scripts/serialize_agent.py`を更新：

```python
def main():
    root_agent = create_router_agent()
    agent_wrapper = AgentEngineWrapper(root_agent)

    # Firestoreサービスなしでシリアライズ
    with open("pickle.pkl", "wb") as f:
        cloudpickle.dump(agent_wrapper, f)
```

**要件**:
- 外部サービス依存の完全排除
- pickle化の成功確認
- デプロイ後の動作確認

#### FR4: Memory Bank統合

Agent EngineのMemory Bank機能を活用：

- `async_add_session_to_memory`: セッションから記憶を保存
- `async_search_memory`: 記憶検索

**Phase 2c Memory Bank統合との互換性を維持**。

### 非機能要件

#### NFR1: 後方互換性

既存のFirestoreベースのセッション管理と並行稼働可能：
- 環境変数で切り替え（`USE_AGENT_ENGINE=true/false`）
- 既存のE2Eテスト・統合テストがパス

#### NFR2: パフォーマンス

- Agent Engineセッション管理のレスポンスタイム < 500ms
- Firestoreと同等以上のパフォーマンス

#### NFR3: エラーハンドリング

- Agent Engine APIエラーの適切なハンドリング
- フォールバック機能（Agent Engine障害時）
- エラーログの充実

### 制約条件

1. **Agent Engine API仕様の調査が必須**
   - セッションAPI（create/get/list/delete）の正確な仕様
   - Memory Bank API（add/search）の仕様
   - ADK AgentとAgent Engine間の通信方法

2. **ADKバージョンの互換性**
   - 現在使用中のADKバージョンとAgent Engineの互換性確認

3. **Terraform設定の調整**
   - 既存のAgent Engine Terraform設定の確認・更新

## 対象範囲

### In Scope

- Agent EngineラッパーとRouter Agentの統合
- VoiceStreamingServiceのリファクタリング
- シリアライゼーションスクリプトの更新
- Memory Bank統合の基本実装
- 単体テスト・E2Eテストの更新

### Out of Scope

- Firestoreベースの既存実装の削除（並行稼働）
- Agent EngineのA/Bテスト実装（issue #55で対応）
- 音声トーン分析の高度化（issue #52で対応）
- Phase 2 WebSocketイベント送信（issue #94、本実装完了後に対応）

## 技術調査項目

### 必須調査

1. **Agent EngineセッションAPI仕様**
   - セッション作成・取得・削除の正確なAPI
   - セッションIDの管理方法（自動生成 vs 手動指定）
   - セッションデータの永続化期間
   - ドキュメント: https://docs.cloud.google.com/agent-builder/agent-engine/overview

2. **Memory Bank統合方法**
   - `async_add_session_to_memory`の使用方法
   - `async_search_memory`による記憶検索
   - Phase 2c Memory Bank統合との互換性

3. **ADK AgentとAgent Engine間の通信**
   - Runnerなしでのエージェント実行方法
   - 会話履歴の受け渡し方法
   - ツール実行の統合

### 検討事項

1. **Firestoreセッションとの移行戦略**
   - 既存データの互換性維持
   - 段階的な移行方法

2. **パフォーマンス比較**
   - Firestore vs Agent Engineのレイテンシ比較
   - コスト分析

3. **デプロイ済みAgent Engineの確認**
   - 現在デプロイされているAgent Engineの機能確認
   - pickleファイルの動作確認

## 成功基準

### 機能的成功

- [ ] Agent Engineにデプロイ可能なpickleファイルが生成できる
- [ ] デプロイ後のAgent Engineがqueryメソッドで応答を返す
- [ ] セッション管理が正常に機能する（会話履歴の保持）
- [ ] Router Agent機能が維持される（サブエージェント切り替え、ツール実行）
- [ ] Memory Bank統合が動作する（記憶の保存・検索）

### 品質的成功

- [ ] 全ユニットテストが通過（pytest）
- [ ] E2Eテストが通過
- [ ] mypy型チェックがパス
- [ ] ruff lintがパス
- [ ] テストカバレッジ80%以上

### 統合的成功

- [ ] VoiceStreamingServiceがRouter Agentを使用
- [ ] CI/CDパイプラインがすべてパス
- [ ] ドキュメントが更新されている

## 依存関係

### 前提条件

- Phase 2b Router Agent実装済み（`backend/app/services/adk/agents/router.py`）
- Agent Engine Terraformデプロイ済み（`infrastructure/terraform/modules/agent_engine/`）
- デプロイ済みAgent Engineが動作確認済み

### ブロック解除

- issue #94（Phase 2 WebSocketイベント送信）がこの実装完了を待機中
- issue #55（A/Bテスト）がこの実装完了後に実施可能

## 参考資料

- [Agent Engine概要](https://docs.cloud.google.com/agent-builder/agent-engine/overview?hl=ja)
- [ADKドキュメント](https://github.com/google/adk)
- 現在のTerraform設定: `infrastructure/terraform/modules/agent_engine/`
- 現在のシリアライゼーションスクリプト: `backend/scripts/serialize_agent.py`
- Router Agent実装: `backend/app/services/adk/agents/router.py`
