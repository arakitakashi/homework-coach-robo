# Task List - Firestore Session Persistence (ADK統合)

## Phase 1: 環境セットアップ

- [x] 依存パッケージの確認・追加（google-adk, google-cloud-firestore）
- [x] ディレクトリ構造の作成（`backend/app/services/adk/sessions/`）

## Phase 2: データモデル実装（TDD）

### 2.1 コンバーター関数

- [x] テスト作成: `test_converters.py`
  - [x] ADK Session → Firestore dict 変換テスト
  - [x] Firestore dict → ADK Session 変換テスト
  - [x] ADK Event → Firestore dict 変換テスト
  - [x] 状態プレフィックス（app:, user:）処理テスト
- [x] 実装: `converters.py`
  - [x] `session_to_dict()` 関数
  - [x] `dict_to_session()` 関数
  - [x] `event_to_dict()` 関数
  - [x] `dict_to_event()` 関数
  - [x] `extract_state_delta()` 関数

### 2.2 状態マージロジック

- [x] テスト作成: 状態マージのテスト
  - [x] app状態のマージ
  - [x] user状態のマージ
  - [x] session状態のマージ
- [x] 実装: `_merge_state()` メソッド

## Phase 3: FirestoreSessionService 実装（TDD）

### 3.1 create_session

- [x] テスト作成: `test_firestore_session_service.py::test_create_session_*`
  - [x] 新規セッション作成成功
  - [x] session_id指定での作成
  - [x] 初期状態の設定
  - [x] 重複session_idでAlreadyExistsError
  - [x] app状態の抽出・保存
  - [x] user状態の抽出・保存
- [x] 実装: `create_session()` メソッド

### 3.2 get_session

- [x] テスト作成: `test_get_session_*`
  - [x] 存在するセッション取得
  - [x] 存在しないセッション → None
  - [x] 状態マージ（app + user + session）
  - [x] GetSessionConfig: num_recent_events
  - [x] GetSessionConfig: after_timestamp
- [x] 実装: `get_session()` メソッド

### 3.3 list_sessions

- [x] テスト作成: `test_list_sessions_*`
  - [x] ユーザー指定で一覧取得
  - [x] ユーザー未指定（アプリ全体）
  - [x] 空の一覧
  - [x] 状態マージ付き
- [x] 実装: `list_sessions()` メソッド

### 3.4 delete_session

- [x] テスト作成: `test_delete_session_*`
  - [x] セッション削除成功
  - [x] イベントサブコレクションも削除
  - [x] 存在しないセッション削除（エラーなし）
- [x] 実装: `delete_session()` メソッド

### 3.5 append_event

- [x] テスト作成: `test_append_event_*`
  - [x] イベント追加と永続化
  - [x] 状態差分の適用
  - [x] 部分イベント（partial=True）は永続化しない
  - [x] temp:* キーは永続化しない
  - [x] last_update_time の更新
  - [x] 状態スコープ別の永続化（app:, user:, session）
- [x] 実装: `append_event()` メソッド

## Phase 4: 統合テスト

- [ ] Firestore Emulator を使った統合テスト（将来のフェーズで実装）
  - [ ] セッションライフサイクル（create → get → append → delete）
  - [ ] 複数ユーザー間の分離
  - [ ] 並行イベント追加

## Phase 5: 品質チェック

- [x] コードレビュー（セルフレビュー）
  - [x] ADK BaseSessionServiceの契約を満たしているか
  - [x] エラーハンドリングは適切か
  - [x] ドキュメンテーションは十分か
- [x] テストカバレッジ確認（97% - 80%以上達成）
- [x] リンター・型チェック実行
  - [x] `uv run ruff check app/services/adk/sessions` → All checks passed
  - [x] `uv run mypy app/services/adk/sessions` → Success: no issues found

## Phase 6: ドキュメント更新

- [x] CLAUDE.md の更新（次のステップ、完了済みセクション）
- [x] COMPLETED.md の作成

---

## 実装サマリー

### 実装ファイル

| ファイル | 内容 |
|---------|------|
| `converters.py` | ADK ↔ Firestore変換関数 |
| `firestore_session_service.py` | FirestoreSessionService（ADK BaseSessionService準拠） |
| `__init__.py` | モジュールエクスポート |

### テストファイル

| ファイル | テスト数 |
|---------|---------|
| `test_converters.py` | 17テスト |
| `test_firestore_session_service.py` | 19テスト |
| **合計** | **36テスト** |

### テストカバレッジ

- `converters.py`: 100%
- `firestore_session_service.py`: 93%
- **全体**: 97%

### ADK SessionServiceの主要な契約

1. `create_session`: 新規セッション作成、重複IDでエラー ✅
2. `get_session`: 取得時に3層状態をマージ ✅
3. `list_sessions`: セッション一覧取得（イベントなし） ✅
4. `delete_session`: サブコレクションも含めて削除 ✅
5. `append_event`: 部分イベントは永続化しない、temp:*は除去 ✅
