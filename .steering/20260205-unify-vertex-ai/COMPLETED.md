# COMPLETED - Vertex AI 統一

**完了日**: 2026-02-05

## 実装サマリー

開発環境と本番環境で異なっていた認証方式（API Key vs Vertex AI）を
Vertex AI（Application Default Credentials）に統一しました。

### 変更内容

| 項目 | Before | After |
|------|--------|-------|
| 開発環境認証 | `GOOGLE_API_KEY` | Vertex AI (ADC) |
| 本番環境認証 | Vertex AI | Vertex AI (ADC) |
| 必須環境変数 | `GOOGLE_API_KEY` | `GOOGLE_CLOUD_PROJECT` |
| コードパス | 開発/本番で分岐 | 統一 |

### 更新したファイル

| ファイル | 変更内容 |
|----------|----------|
| `gemini_client.py` | `project`/`location` パラメータ追加、API Key 関連削除 |
| `dialogue.py` | `get_llm_client()` を Vertex AI モードに変更 |
| `test_gemini_client.py` | Vertex AI モード用テストに更新 |
| `CLAUDE.md` | ローカル開発セットアップ手順を追加 |

### 品質メトリクス

- **テスト数**: 202件（全てパス）
- **カバレッジ**: 98%
- **Ruff lint**: エラーなし
- **mypy**: エラーなし

## 技術的な決定

### Vertex AI への統一を選択した理由

1. **環境間の一致**: 開発と本番で同じコードパス
2. **本番障害リスク低減**: 「開発で動いても本番で動かない」を防止
3. **GCP推奨方式**: Application Default Credentials は GCP 推奨
4. **セキュリティ向上**: API Key の漏洩リスクを排除

### Application Default Credentials (ADC)

認証情報は以下の順序で検索されます：

1. `GOOGLE_APPLICATION_CREDENTIALS` 環境変数
2. `gcloud auth application-default login` の認証情報
3. Compute Engine / Cloud Run のサービスアカウント

開発者は一度 `gcloud auth application-default login` を実行すれば、
以降は自動的に認証されます。

## ローカル開発セットアップ

```bash
# 1. 認証情報を設定（初回のみ）
gcloud auth application-default login

# 2. プロジェクトIDを設定
export GOOGLE_CLOUD_PROJECT=your-project-id

# 3. バックエンドを起動
cd backend && uv run uvicorn app.main:app --reload
```

## 発生した問題と解決

### Ruff ARG002 lint エラー

**問題**: `@patch` デコレータで注入されるモック引数が未使用とみなされた

**解決**: `# noqa: ARG002` コメントを追加

```python
@patch("app.services.adk.dialogue.gemini_client.genai.Client")
def test_init_with_default_model(
    self, mock_client: MagicMock  # noqa: ARG002
) -> None:
```

## Lessons Learned

1. **環境統一の重要性**: 開発/本番で異なる認証方式は避けるべき
2. **ADC の利便性**: `gcloud auth application-default login` で簡単にセットアップ
3. **TDD の効果**: テストを先に書くことで、実装の方向性が明確に
4. **モック注入パターン**: FastAPI の依存性オーバーライドでテストが容易

## 今後の改善点

1. **CI/CD での認証**: GitHub Actions で Workload Identity Federation を使用
2. **エラーハンドリング強化**: ADC 認証失敗時の明確なエラーメッセージ
3. **リージョン選択**: レイテンシ最適化のためのリージョン選択ガイド
