# Task List - Session Content Integration

## Phase 1: 環境セットアップ

- [ ] `/frontend` スキルを参照
- [ ] 既存の型定義・atomsを確認

## Phase 2: 型定義（TDD）

- [ ] セッションAPI型のテスト作成
- [ ] セッションAPI型の実装（`lib/api/types.ts`拡張）

## Phase 3: SessionClient実装（TDD）

- [ ] SessionClientのテスト作成
- [ ] SessionClientの実装（`lib/api/sessionClient.ts`）
- [ ] エクスポート集約の更新（`lib/api/index.ts`）

## Phase 4: useSessionフック実装（TDD）

- [ ] useSessionのテスト作成
- [ ] useSessionの実装（`lib/hooks/useSession.ts`）
- [ ] エクスポート集約の更新（`lib/hooks/index.ts`）

## Phase 5: TextInputコンポーネント実装（TDD）

- [ ] TextInputのテスト作成
- [ ] TextInputの実装（`components/ui/TextInput/`）
- [ ] エクスポート集約の更新（`components/ui/index.ts`）

## Phase 6: SessionContent統合

- [ ] SessionContentのテスト更新
- [ ] SessionContentの実装更新
  - useSessionフック統合
  - useDialogueフック統合
  - TextInputコンポーネント追加
  - エラーハンドリング追加

## Phase 7: 品質チェック

- [ ] `bun lint` パス
- [ ] `bun typecheck` パス
- [ ] `bun run test` パス
- [ ] テストカバレッジ確認

## Phase 8: ドキュメント・コミット

- [ ] COMPLETED.md 作成
- [ ] CLAUDE.md 更新（進捗反映）
- [ ] コミット作成
