# Requirements - Vertex AI 統一

## 背景・目的

現在、開発環境と本番環境で異なる認証方式を使用している：

- **開発環境**: Gemini API Key (`GOOGLE_API_KEY`)
- **本番環境**: Vertex AI (`GOOGLE_GENAI_USE_VERTEXAI=TRUE`)

この差異により、以下のリスクがある：

1. 開発環境で動作しても本番環境で動作しない可能性
2. Vertex AI 固有の挙動を開発段階でテストできない
3. 認証関連のコードパスが異なる

## 要求事項

### 機能要件

1. **認証方式の統一**
   - 開発・本番ともに Vertex AI (Application Default Credentials) を使用
   - API Key ベースの認証を廃止

2. **環境変数の簡素化**
   - `GOOGLE_API_KEY` / `GEMINI_API_KEY` を不要に
   - `GOOGLE_CLOUD_PROJECT` を必須に
   - `GOOGLE_GENAI_USE_VERTEXAI=TRUE` をデフォルトに

3. **既存機能の維持**
   - LLM統合（回答分析、質問生成、ヒント生成）は変更なし
   - フォールバック動作は維持

### 非機能要件

1. **後方互換性**
   - 既存の API Key 設定がある場合でも動作すること（警告を出す）

2. **テスト可能性**
   - モックを使用したユニットテストが引き続き動作すること

3. **ドキュメント**
   - セットアップ手順を更新すること

### 制約条件

- `google-genai` SDK を使用（変更なし）
- Python 3.10+ 互換性を維持

## 対象範囲

### In Scope

- `GeminiClient` の認証方式変更
- 環境変数の整理
- テストの更新
- ドキュメント更新

### Out of Scope

- ADK SessionService / MemoryBank 統合（次フェーズ）
- Firestore 永続化（次フェーズ）
- フロントエンドの変更

## 成功基準

- [ ] 全テストが通過（201件以上）
- [ ] カバレッジ80%以上維持
- [ ] `gcloud auth application-default login` 後に動作確認
- [ ] Ruff / mypy エラーなし
