# COMPLETED - 対話API統合

**完了日時**: 2026-02-05

## 実装サマリー

### 実装内容

FastAPI SSEストリーミングエンドポイントを実装し、ADK Runnerとフロントエンドを接続するAPIを提供した。

### 作成ファイル

| ファイル | 説明 |
|---------|------|
| `app/schemas/dialogue_runner.py` | SSEイベントスキーマ（Request, Text, Error, Done） |
| `app/api/v1/dialogue_runner.py` | ストリーミングエンドポイント（`/api/v1/dialogue/run`） |
| `tests/unit/schemas/test_dialogue_runner.py` | スキーマテスト（10テスト） |
| `tests/unit/api/v1/test_dialogue_runner.py` | エンドポイントテスト（8テスト） |

### 変更ファイル

| ファイル | 変更内容 |
|---------|---------|
| `app/api/v1/router.py` | `dialogue_runner_router`を追加 |

## 品質メトリクス

| 指標 | 結果 |
|------|------|
| テスト数 | 18テスト（新規） / 309テスト（全体） |
| テストカバレッジ | 96% |
| Ruff | All checks passed |
| mypy | Success: no issues found |

## 学んだこと（Lessons Learned）

### FastAPIの依存性注入とモック

**問題**: `patch()` で依存性注入関数をモックしても、FastAPIは内部の依存関係を評価してしまう。

```python
# ❌ これでは不十分
with patch("app.api.v1.dialogue_runner.get_agent_runner_service", return_value=mock):
    ...  # 内部のget_session_service()がまだ呼ばれる
```

**解決策**: `app.dependency_overrides` を使用する。

```python
# ✅ 正しいアプローチ
app.dependency_overrides[get_agent_runner_service] = lambda: mock_runner
try:
    client = TestClient(app)
    response = client.post(...)
finally:
    app.dependency_overrides.clear()
```

**理由**: FastAPIの依存性注入システムは、関数の呼び出し時ではなく、エンドポイント定義時に`Depends()`を評価する。`dependency_overrides`はこの仕組みを正しくオーバーライドする。

## 次のステップ

1. **CLAUDE.md の更新** - API統合の完了を記録
2. **フロントエンド実装** - SSEクライアントの実装
3. **E2Eテスト** - 実際のADK Runnerとの統合テスト

## API仕様

### エンドポイント

```
POST /api/v1/dialogue/run
Content-Type: application/json
Accept: text/event-stream

Request:
{
  "user_id": "string",
  "session_id": "string",
  "message": "string"
}

Response (SSE):
event: text
data: {"text": "..."}

event: text
data: {"text": "..."}

event: done
data: {"session_id": "..."}

(エラー時)
event: error
data: {"error": "...", "code": "INTERNAL_ERROR"}
```
