# Requirements - Phase 3: セッション管理の移行 (#54)

## 背景・目的

Phase 3で、セッションファクトリによる`FirestoreSessionService`と`VertexAiSessionService`の切り替え機能を実装した。環境変数`AGENT_ENGINE_ID`を設定することで、Agent EngineのマネージドセッションサービスにすぐIssue切り替えられる基盤が整った。

しかし、以下の課題が残っている：

1. **既存セッションデータの移行**: 現在Firestoreに保存されている既存セッションを、Agent Engine形式に移行する手順が未整備
2. **段階的移行機能の欠如**: 環境変数による一括切り替えのみで、ユーザーごと・機能ごとの段階的ロールアウトができない
3. **ロールバック手順の未文書化**: 問題発生時の復旧手順が明確でない

Issue #54では、これらの課題を解決し、本番環境で安全にマネージドセッション管理に移行できる体制を整える。

### 期待されるメリット

- **運用負荷の軽減**: Firestoreセッション管理の自前実装（359行）のメンテナンスが不要に
- **マネージド機能の活用**: Agent Engineの自動スケーリング、専用ダッシュボード、トレーシング
- **将来のA/Bテスト基盤**: セッション単位での動作切り替えが可能に

## 要求事項

### 機能要件

#### 1. データ移行スクリプト

既存のFirestoreセッションデータをAgent Engine形式に移行するスクリプトを作成する。

**Input**:
- Firestore `sessions` コレクションの全ドキュメント

**Output**:
- Agent Engine VertexAiSessionService 経由で保存されたセッション

**処理内容**:
- Firestoreセッションの読み取り（`FirestoreSessionService.get_session()`）
- Agent Engine形式への変換（必要に応じてスキーマ変換）
- VertexAiSessionService経由での保存（`VertexAiSessionService.store_session()`）
- 移行ログの記録（成功・失敗・スキップ）

**エラーハンドリング**:
- 変換失敗時は警告を記録し、スキップ（全体の移行は継続）
- 保存失敗時はリトライ（最大3回）
- 致命的エラー時は移行を中断し、ロールバック

#### 2. 段階的移行機能（フィーチャーフラグ）

環境変数による一括切り替えではなく、ユーザーごとにマネージドセッションへの移行を制御する機能。

**実装方式**: セッションファクトリの拡張

現在:
```python
def create_session_service() -> BaseSessionService:
    if os.environ.get("AGENT_ENGINE_ID"):
        return VertexAiSessionService(...)
    return FirestoreSessionService()
```

拡張後:
```python
def create_session_service(user_id: str | None = None) -> BaseSessionService:
    if should_use_managed_session(user_id):
        return VertexAiSessionService(...)
    return FirestoreSessionService()

def should_use_managed_session(user_id: str | None) -> bool:
    # 1. 環境変数による全体制御（優先）
    if not os.environ.get("AGENT_ENGINE_ID"):
        return False

    # 2. フィーチャーフラグによるユーザー単位制御
    # 例: MIGRATED_USER_IDS="user1,user2,user3"
    migrated_users = os.environ.get("MIGRATED_USER_IDS", "").split(",")
    if user_id in migrated_users:
        return True

    # 3. パーセンテージロールアウト
    # 例: MIGRATION_PERCENTAGE=10 → 10%のユーザーを移行
    percentage = int(os.environ.get("MIGRATION_PERCENTAGE", "0"))
    if percentage > 0 and user_id:
        user_hash = hash(user_id) % 100
        return user_hash < percentage

    return False
```

**パーセンテージロールアウト**:
- `MIGRATION_PERCENTAGE=10` → 10%のユーザーがマネージドセッションを使用
- ユーザーIDのハッシュ値で決定（同じユーザーは常に同じサービスを使用）

#### 3. データ検証ツール

移行前後のセッションデータの整合性を検証するツール。

**検証項目**:
- セッション数の一致
- セッションIDの一致
- セッション状態（`app:`/`user:`/`temp:`スコープ）の一致
- タイムスタンプの一致（許容誤差: 1秒）

**Output**:
- 検証レポート（JSON/Markdown）
- 不一致がある場合は詳細ログ

#### 4. ロールバック手順の文書化

問題発生時に即座にFirestoreSessionServiceにフォールバックする手順を文書化する。

**手順**:
1. 環境変数`AGENT_ENGINE_ID`を削除または空にする
2. サービスを再起動（環境変数の再読み込み）
3. データ検証ツールで整合性確認
4. 必要に応じてAgent EngineセッションをFirestoreにバックアップ

### 非機能要件

| 要件 | 基準 |
|------|------|
| **可用性** | 移行中もサービス継続（ダウンタイムなし） |
| **データ整合性** | 移行前後でセッションデータの欠損なし（100%） |
| **パフォーマンス** | 移行による応答時間の劣化なし（P95 < 500ms） |
| **監視性** | 移行進捗と成功率の可視化（ログ出力） |
| **テストカバレッジ** | 80%以上を維持 |
| **型安全性** | mypy / ruff エラーなし |

### 制約条件

1. **後方互換性**: 既存セッションIDを維持（ユーザー影響なし）
2. **音声ストリーミング**: WebSocketエンドポイントは引き続きFirestoreSessionServiceを使用
   - Agent EngineはWebSocket/`run_live()`に未対応のため
   - テキスト対話のみマネージドセッションに移行
3. **環境変数の整合性**: `AGENT_ENGINE_ID`と`AGENT_ENGINE_RESOURCE_NAME`の両方が必要
4. **GCP権限**: Agent Engineサービスアカウントに`roles/datastore.user`が必要（ツールがFirestoreを操作するため）

## 対象範囲

### In Scope

- データ移行スクリプト（`scripts/migrate_sessions.py`）
- データ検証ツール（`scripts/validate_sessions.py`）
- セッションファクトリの拡張（段階的移行機能）
- ロールバック手順書（`docs/session-migration-rollback.md`）
- ユニットテスト・統合テストの追加

### Out of Scope

- 音声ストリーミング（WebSocket）のマネージドセッション対応
  - Agent Engineが`run_live()`をサポートするまで保留
- UI/ダッシュボードでの移行進捗表示
  - 将来の拡張で対応
- 自動ロールバック機能（エラー率閾値監視）
  - Issue #55（A/Bテスト基盤）で対応
- Firestoreセッションサービスの削除
  - フォールバックとして残す（少なくとも1ヶ月）

## 成功基準

1. **移行スクリプト実行成功**: 開発環境の全既存セッションがAgent Engineに移行される
2. **データ検証ツール合格**: 移行前後のセッション数・状態が100%一致
3. **段階的移行機能動作**: `MIGRATION_PERCENTAGE=10`で10%のユーザーのみマネージドセッション使用
4. **ロールバック成功**: 環境変数削除→再起動で5分以内にFirestoreに復旧
5. **全テストパス**: 既存548テスト + 新規テスト（最低20テスト追加）
6. **カバレッジ維持**: 80%以上（現在90%）
7. **型チェック・Lint通過**: mypy / ruff エラーなし
