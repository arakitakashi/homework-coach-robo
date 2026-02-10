# Requirements - Agent Engine統合による内部完結型Router Agent実装（簡素化版）

## 🎉 設計の大幅簡素化

公式ドキュメント調査により、実装が大幅に簡素化されました。

**変更点**: AgentEngineWrapper不要、SessionServiceの切り替えのみ

## 背景・目的

### 現在の問題

1. **Phase 1単一エージェント**: `create_socratic_agent()`を使用（Phase 2 Router Agent未統合）
2. **Firestore依存**: `FirestoreSessionService`への依存
3. **pickleファイルの複雑性**: 外部依存が含まれる

### 目的

1. **Phase 2 Router Agentの統合**: Math Coach、Japanese Coach等のサブエージェント
2. **VertexAiSessionServiceの採用**: Agent Engine提供のセッション管理に切り替え
3. **pickleファイルの簡素化**: Firestore依存排除

## 要求事項

### 機能要件

#### FR1: VoiceStreamingServiceのRouter Agent統合

**現在**:
```python
self._agent = create_socratic_agent(model=LIVE_MODEL)
```

**変更後**:
```python
self._agent = create_router_agent(model=LIVE_MODEL)
```

#### FR2: VertexAiSessionServiceの統合

**現在**:
```python
self._session_service = FirestoreSessionService()
```

**変更後**:
```python
self._session_service = VertexAiSessionService(
    project_id=PROJECT_ID,
    location=LOCATION,
    agent_engine_id=AGENT_ENGINE_ID,
)
```

#### FR3: 環境変数による切り替え

```python
USE_AGENT_ENGINE = os.getenv("USE_AGENT_ENGINE", "false")

if USE_AGENT_ENGINE == "true":
    session_service = VertexAiSessionService(...)
else:
    session_service = FirestoreSessionService()  # 後方互換
```

#### FR4: シリアライゼーションスクリプトの更新

```python
# backend/scripts/serialize_agent.py

def main():
    # Router Agent使用
    root_agent = create_router_agent()

    # VertexAiSessionService使用
    session_service = VertexAiSessionService(...)

    runner = Runner(
        agent=root_agent,
        session_service=session_service,
    )

    # pickle化
    with open("pickle.pkl", "wb") as f:
        cloudpickle.dump(runner, f)
```

### 非機能要件

#### NFR1: 後方互換性

- Firestoreベースとの並行稼働
- 既存のE2Eテスト・統合テストがパス

#### NFR2: パフォーマンス

- セッション管理のレスポンスタイム < 500ms
- Firestoreと同等以上

#### NFR3: エラーハンドリング

- VertexAiSessionService初期化エラーのフォールバック
- セッション作成失敗時のリトライ

### 制約条件

1. **ADK公式ドキュメントに準拠**
   - https://docs.cloud.google.com/agent-builder/agent-engine/sessions/manage-sessions-adk?hl=ja

2. **VertexAiSessionServiceの仕様調査**
   - `run_live()`のサポート状況
   - `LiveRequestQueue`との互換性

3. **Terraformの環境変数設定**
   - `PROJECT_ID`, `LOCATION`, `AGENT_ENGINE_ID`

## 対象範囲

### In Scope

- VoiceStreamingServiceのRouter Agent統合
- VertexAiSessionServiceへの切り替え
- シリアライゼーションスクリプトの更新
- 単体テスト・E2Eテストの更新

### Out of Scope

- Memory Bank統合（別issueまたは後続タスク）
- Firestoreベースの削除（並行稼働を維持）
- Agent EngineのA/Bテスト（issue #55で対応）
- Phase 2 WebSocketイベント送信（issue #94、本実装完了後に対応）

## 技術調査項目

### 必須調査

1. **VertexAiSessionServiceの`run_live()`サポート**
   - 音声ストリーミング（`LiveRequestQueue`）との互換性
   - サポートされない場合の代替実装

2. **環境変数の確認**
   - `PROJECT_ID`, `LOCATION`, `AGENT_ENGINE_ID`の取得方法
   - Terraformでの設定確認

3. **pickle化の確認**
   - VertexAiSessionServiceを含むRunnerのpickle化が成功するか
   - デプロイ後の動作確認

### 検討事項

1. **Firestoreセッションとの移行戦略**
   - 段階的な移行方法
   - データ移行の要否

2. **パフォーマンス比較**
   - Firestore vs VertexAiSessionServiceのレイテンシ

## 成功基準

### 機能的成功

- [ ] VoiceStreamingServiceがRouter Agentを使用
- [ ] VertexAiSessionServiceでセッション管理が動作
- [ ] `run_live()`が動作する（または代替実装）
- [ ] pickle化が成功する
- [ ] デプロイ後のAgent Engineが正常動作

### 品質的成功

- [ ] 全ユニットテストが通過（pytest）
- [ ] E2Eテストが通過
- [ ] mypy型チェックがパス
- [ ] ruff lintがパス
- [ ] テストカバレッジ80%以上

### 統合的成功

- [ ] 既存のWebSocket統合が正常動作
- [ ] CI/CDパイプラインがすべてパス
- [ ] ドキュメントが更新されている

## 依存関係

### 前提条件

- Phase 2b Router Agent実装済み（`backend/app/services/adk/agents/router.py`）
- Agent Engine Terraformデプロイ済み（`infrastructure/terraform/modules/agent_engine/`）
- VertexAiSessionServiceがADK SDKに含まれている

### ブロック解除

- issue #94（Phase 2 WebSocketイベント送信）がこの実装完了を待機中
- issue #55（A/Bテスト）がこの実装完了後に実施可能

## 参考資料

- [Agent Engine概要](https://docs.cloud.google.com/agent-builder/agent-engine/overview?hl=ja)
- [ADKセッション管理](https://docs.cloud.google.com/agent-builder/agent-engine/sessions/manage-sessions-adk?hl=ja)
- [ADKドキュメント](https://github.com/google/adk)
- Router Agent実装: `backend/app/services/adk/agents/router.py`
- 現在のシリアライゼーションスクリプト: `backend/scripts/serialize_agent.py`
