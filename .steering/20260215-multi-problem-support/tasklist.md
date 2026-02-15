# Task List - 複数問題認識サポート

## Phase 1: Atoms（状態管理）

- [ ] `multiProblem.test.ts` テスト作成
- [ ] `multiProblem.ts` 実装

## Phase 2: ProblemSelectorコンポーネント

- [ ] `ProblemSelector.test.tsx` テスト作成
- [ ] `ProblemItem.tsx` + `ProblemSelector.tsx` 実装
- [ ] `index.ts` エクスポート

## Phase 3: CameraInterface変更

- [ ] `CameraInterface.test.tsx` テスト更新
- [ ] `CameraInterface.tsx` に `onRecognitionComplete` prop追加

## Phase 4: WebSocket型 + クライアント変更

- [ ] `websocket.ts` 型拡張
- [ ] `voiceWebSocket.ts` sendImageStart引数追加
- [ ] `useVoiceStream.ts` sendImageStart引数追加

## Phase 5: SessionContent統合

- [ ] `SessionContent.tsx` 更新（ProblemSelector統合、問題遷移ロジック）
- [ ] `features/index.ts` エクスポート追加

## Phase 6: Backend変更

- [ ] `voice_stream.py` 問題番号コンテキスト追加

## Phase 7: 品質チェック

- [ ] `bun lint && bun typecheck && bun test`
- [ ] `uv run ruff check . && uv run mypy . && uv run pytest`
