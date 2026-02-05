# Requirements - Firestore Session Persistence (ADK統合)

## 背景・目的

### 背景

ソクラテス式対話エンジンの基盤実装とLLM統合が完了した。現在の`SessionStore`はインメモリ実装のため：

1. サーバー再起動でセッションが消失
2. 複数インスタンス間で状態が共有されない
3. ADK (Agent Development Kit) のSessionServiceと互換性がない

Cloud Runでのスケーリングや本番運用に向けて、永続化が必須。

### 目的

1. **ADK準拠のSessionService実装**: `google.adk.sessions.BaseSessionService`を継承し、Firestoreで永続化
2. **既存インターフェースとの統合**: 現在の`SessionStore`の機能を保ちながらADK互換性を追加
3. **3層状態管理**: ADKの`app:`, `user:`, セッションスコープを適切に管理

---

## 要求事項

### 機能要件

#### FR-1: ADK BaseSessionService準拠

`FirestoreSessionService`は以下の抽象メソッドを実装すること：

- `create_session(app_name, user_id, state, session_id) -> Session`
- `get_session(app_name, user_id, session_id, config) -> Optional[Session]`
- `list_sessions(app_name, user_id) -> ListSessionsResponse`
- `delete_session(app_name, user_id, session_id) -> None`

#### FR-2: イベント永続化

- `append_event(session, event) -> Event` をオーバーライド
- イベントをFirestoreに永続化
- 部分イベント (`partial=True`) は永続化しない
- 一時状態 (`temp:*` キー) は永続化しない

#### FR-3: 3層状態管理

ADKの状態スコープを適切に管理：

| スコープ | プレフィックス | 共有範囲 |
|---------|--------------|---------|
| アプリ | `app:` | 全ユーザー共通 |
| ユーザー | `user:` | ユーザーの全セッション |
| セッション | なし | 単一セッション |

#### FR-4: DialogueContextとの互換性

- 既存の`DialogueContext.from_adk_session()`でADK Sessionから変換可能
- 対話エンジンは既存コードを変更せず動作

#### FR-5: Firestoreコレクション構造

`docs/firestore-design.md`で定義された構造に従う：

```
/sessions/{session_id}
  ├─ id, userId, appName, createdAt, updatedAt
  ├─ isActive, currentProblemId, hintLevel, emotionalState
  └─ /dialogue_turns/{turn_id}
```

追加で状態管理用：

```
/app_state/{app_name}
  └─ state: map

/user_state/{app_name}/{user_id}
  └─ state: map
```

#### FR-6: セッション一覧取得

- ユーザー指定時: そのユーザーのセッション一覧
- ユーザー未指定時: アプリの全セッション一覧
- イベントと状態をマージして返却

#### FR-7: GetSessionConfig対応

- `num_recent_events`: 最新N件のイベントのみ取得
- `after_timestamp`: 指定タイムスタンプ以降のイベントのみ取得

---

### 非機能要件

#### NFR-1: パフォーマンス

- セッション取得: 500ms以内
- イベント追加: 300ms以内
- Firestoreの読み取り/書き込み回数を最小化

#### NFR-2: 信頼性

- Firestoreトランザクションで整合性を保証
- 一時的なネットワークエラーはリトライ
- AlreadyExistsError: 既存セッションIDで作成時に発生

#### NFR-3: テストカバレッジ

- 80%以上のカバレッジ
- ADKの既存テストケースを参考に網羅的テスト

#### NFR-4: セキュリティ

- Firestore Security Rulesで認可を強制
- ユーザーは自分のセッションのみアクセス可能

---

### 制約条件

1. **ADK 1.23.0+**: `google-adk>=1.23.0`に依存
2. **非同期API**: Firestore AsyncClientを使用
3. **既存コード影響最小化**: 対話エンジンの変更は避ける
4. **インメモリ実装を残す**: 開発・テスト用に`SessionStore`は維持

---

## 対象範囲

### In Scope

1. `FirestoreSessionService`クラスの実装
2. Firestoreコレクション設計（状態管理用の追加）
3. ユニットテスト・統合テスト
4. 既存`SessionStore`との互換レイヤー

### Out of Scope

1. ADK MemoryBank統合（別タスク）
2. Redisキャッシュ統合（別タスク）
3. BigQueryへのデータ移行（別タスク）
4. フロントエンドの変更

---

## 成功基準

1. [ ] ADK BaseSessionServiceの全抽象メソッドが実装されている
2. [ ] 3層状態管理が正しく動作する
3. [ ] イベントがFirestoreに永続化される
4. [ ] 既存の対話エンジンが変更なしで動作する
5. [ ] テストカバレッジ80%以上
6. [ ] CIが全てパス（lint, typecheck, test）
