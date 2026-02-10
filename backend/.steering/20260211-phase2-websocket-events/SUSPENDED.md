# Suspended - Phase 2 WebSocket Events Implementation

## 状況

このステアリングディレクトリの作業は**一時停止**します。

## 理由

issue #98「Agent Engineを利用した内部完結型Router Agentの実装」が発見されました。
この実装により、以下の大きなアーキテクチャ変更が行われます：

1. **Firestoreベースのセッション管理**から**Agent Engine内蔵セッション管理**への移行
2. **Runner + FirestoreSessionService**から**AgentEngineWrapper**への移行
3. **create_socratic_agent()**（Phase 1）から**create_router_agent()**（Phase 2）への移行

## 影響

issue #94（Phase 2 WebSocketイベント送信）は、issue #98の実装に依存しています：

- `VoiceStreamingService`のアーキテクチャが根本的に変わる
- ツール実行・エージェント遷移の監視方法が変わる
- Agent Engine経由でのイベント取得が必要になる

## 実装順序

1. **先**: issue #98（Agent Engine統合）を実装
2. **後**: issue #94（WebSocketイベント送信）を実装

これにより、正しいアーキテクチャ上にPhase 2イベント送信を実装でき、二度手間を避けられます。

## 次のアクション

- [ ] issue #98用の新しいステアリングディレクトリを作成
- [ ] Agent EngineラッパーとRouter Agent統合を実装
- [ ] 完了後、このステアリングディレクトリに戻ってWebSocketイベント送信を実装

## 作成済みドキュメント

- `requirements.md` - Phase 2イベントの要求仕様（後で参照）
- `design.md` - WebSocketイベント設計（後で参照）
- `tasklist.md` - 実装タスク（後で参照）

これらのドキュメントは、issue #98完了後に再利用します。

---

**Suspended at**: 2026-02-11 05:50 JST
**Reason**: Architectural dependency on issue #98
**Resume after**: issue #98 completion
